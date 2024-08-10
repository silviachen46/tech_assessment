from typing import Literal
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph, MessagesState
import os
from typing import Literal, Dict


class UserInput(BaseModel):
    message: str
    thread_id: str

class AIResponse(BaseModel):
    message: str
    thread_id: str
    requires_more_info: bool

app = FastAPI()

scheduler_prompt = SystemMessage(content="""
You are a scheduling assistant. When the user wants a general cleaning service, generate a random time and return a service message like: The next available slot is on year-month-date (time in 24 hours scale), and the price is $100 for 3 hours.
Note that the price is fixed. Do not tell user the time slot is randomly generated.
If time slot info and type of cleaning hours has been provided and user has confirmed with a "yes", you should return with a hard-coded text "Booking confirmed".
""")

guardrail_prompt = SystemMessage(content="""
You are a guardrail agent responsible for overseeing interactions. Your tasks include:
Checking if the user mentioned post-renovation. If yes, return the hardcoded answer "We're connecting you with a human agent."
        if the user hasn't mention anything about post-renovation, do not mention it in your response either.
""")

info_collection_prompt = SystemMessage(content="""
You are an information collection agent.
Specifically, we have the following types: 3-hour or 4-hour cleaning. If the user didn't mention the type, you should ask for it.
If type information is already provided, respond with "all information collected:".
If information is missing, ask for the specific missing information.
""")

os.environ['GROQ_API_KEY'] = 'groq_api_key_here'

scheduler_model = ChatGroq(model="llama3-8b-8192")
guardrail_model = ChatGroq(model="llama3-8b-8192")
info_collection_model = ChatGroq(model="llama3-8b-8192")

def route_message(state: MessagesState) -> Literal["guardrail", "info_collection", "scheduler", END]:
    messages = state['messages']
    last_ai_message = next((msg for msg in reversed(messages) if isinstance(msg, AIMessage)), None).content.lower()
    last_human_message = next((msg for msg in reversed(messages) if isinstance(msg, HumanMessage)), None).content.lower()

    if "connecting you with a human agent" in last_ai_message or "booking confirmed" in last_ai_message:
        return END
    elif "3-hour" in last_human_message or "4-hour" in last_human_message or "yes" in last_human_message:
        return "scheduler"
    elif "3-hour and 4-hour" in last_ai_message or "3-hour or 4-hour" in last_ai_message: # easiest way to determine if we asks for more info
        return END
    else:
        return "info_collection"
    

def call_guardrail_model(state: MessagesState):
    print("guardrail")
    messages = state['messages']
    full_messages = [guardrail_prompt] + messages
    response = guardrail_model.invoke(full_messages)
    return {"messages": [response]}

def call_info_collection_model(state: MessagesState):
    print("info")
    messages = state['messages']
    full_messages = [info_collection_prompt] + messages
    response = info_collection_model.invoke(full_messages)
    return {"messages": [response]}

def call_scheduler_model(state: MessagesState):
    print("scheduler")
    messages = state['messages']
    full_messages = [scheduler_prompt] + messages
    response = scheduler_model.invoke(full_messages)
    return {"messages": [response]}

workflow = StateGraph(MessagesState)

workflow.add_node("guardrail", call_guardrail_model)
workflow.add_node("info_collection", call_info_collection_model)
workflow.add_node("scheduler", call_scheduler_model)


workflow.set_entry_point("guardrail")

workflow.add_conditional_edges("guardrail", route_message)
workflow.add_conditional_edges("info_collection", route_message)
workflow.add_conditional_edges("scheduler", lambda _: END)

app_workflow = workflow.compile()

thread_memory: Dict[str, Dict] = {}

@app.post("/chat", response_model=AIResponse)
async def chat(user_input: UserInput):
    thread_id = user_input.thread_id
    
    if thread_id not in thread_memory:
        thread_memory[thread_id] = {"messages": [], "current_state": None}
    
    thread_memory[thread_id]["messages"].append(HumanMessage(content=user_input.message))
    result = app_workflow.invoke(thread_memory[thread_id], {"recursion_limit": 3})
    
    thread_memory[thread_id]["messages"] = result["messages"]
    
    last_ai_message = next((msg for msg in reversed(result["messages"]) if isinstance(msg, AIMessage)), None)
    
    requires_more_info = False
    if last_ai_message and ("3-hour" in last_ai_message.content or "4-hour" in last_ai_message.content):
        requires_more_info = True
        thread_memory[thread_id]["current_state"] = result
    else:
        thread_memory[thread_id]["current_state"] = None
    
    if last_ai_message:
        return AIResponse(
            message=last_ai_message.content,
            thread_id=thread_id,
            requires_more_info=requires_more_info
        )
    else:
        return AIResponse(
            message="No AI response generated.",
            thread_id=thread_id,
            requires_more_info=False
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
