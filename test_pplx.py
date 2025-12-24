import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("PPLX_API_KEY")
print(f"API Key found: {True if api_key else False}")

url = "https://api.perplexity.ai/chat/completions"

messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    },
    {
        "role": "user", 
        "content": "Hello"
    }
]

# Testing with the model currently in code
payload = {
    "model": "sonar-small-online", 
    "messages": messages,
    "temperature": 0.1
}

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

try:
    print(f"Sending request to {url} with model {payload['model']}...")
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
