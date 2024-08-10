# Superbench tech assessment note

## cases tested:

### multi-turn conversation
   
 user: I want to book a general cleaning service.

 Response content: {'message': "It looks like you didn't mention the type of cleaning services. Can you please specify whether you're looking for a 3-hour or 4-hour 
 cleaning?", 'thread_id': '22', 'requires_more_info': True}

 user: 4-hour

 Response content: {'message': "The next available slot is on 2025-01-01 00:00, and the price is $100 for 3 hours. Would you like to confirm this booking? (Please respond 
 with 'yes' if you'd like to confirm)", 'thread_id': '22', 'requires_more_info': False}

 user: yes

 Response content: {'message': 'Booking confirmed.', 'thread_id': '22', 'requires_more_info': False}

### single-turn with type specified
   
 user: I want to book a 3-hour general cleaning service.

 Response content: {'message': "The next available slot is on 2025-01-01 00:00, and the price is $120 for 4 hours. Would you like to confirm this booking? (Please respond with 'yes' if you'd like to confirm)", 'thread_id': '22', 'requires_more_info': False}

 user: yes.

 Response content: {'message': 'Booking confirmed.', 'thread_id': '22', 'requires_more_info': False}

### post-renovation
   
   Response content: {'message': "We're connecting you with a human agent.", 'thread_id': '22', 'requires_more_info': False}

## Implemenation:

This script is implemented with fastapi, groq for calling large language models, and some simple rule-based matching with langgraph for routing the agents. Note that it's only implemented for the given simple cases, and can be extended with more functionalities for more complicated cases. Memory is kept through thread_id passed by user.

## Running:

start the server with running the superbench_fastapi.py script, and can be tested through the following two ways:

1. For running on Windows cmd:
   ```curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d "{\"message\": \"I want to book post-renovation cleaning\", \"thread_id\": \"22\"}"```

2. Running directly with the given python script superbench.py:
   navigate into the corresponding directory and enter "python superbench.py" in terminal.
   
