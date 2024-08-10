import requests
url = "http://127.0.0.1:8000/chat" 

payload = {
    "message": "I want to book post-renovation cleaning",
    "thread_id": '22'  
}

headers = {
    "Content-Type": "application/json"
}
response = requests.post(url, json=payload, headers=headers)
if response.status_code == 200:
    print("Response content:", response.json())
else:
    print("Failed to get a valid response. Status code:", response.status_code)
    print("Response content:", response.text)
