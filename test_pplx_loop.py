import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("PPLX_API_KEY")
url = "https://api.perplexity.ai/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

messages = [{"role": "user", "content": "Hello"}]

# List of potential models to try
models_to_test = [
    "sonar", 
    "sonar-pro",
    "llama-3.1-sonar-small-128k-online",
    "llama-3.1-sonar-large-128k-online",
    "llama-3.1-sonar-huge-128k-online",
    "llama-3-sonar-small-32k-online",
    "llama-3-sonar-large-32k-online"
]

for model in models_to_test:
    print(f"Testing model: {model}...")
    payload = {
        "model": model, 
        "messages": messages,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"SUCCESS! Model '{model}' is valid.")
            print(f"Response: {response.json()['choices'][0]['message']['content'][:50]}...")
            break # Found a working one
        else:
            print(f"FAILED: {model} - Status: {response.status_code}")
            # print(response.text)
    except Exception as e:
        print(f"ERROR: {model} - {e}")
