import os
import json
import requests
from dotenv import load_dotenv

# 1. Load environment variables from the .env file
load_dotenv()

def run_test():
    # 2. Get API Key and Model from environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    model_name = os.getenv("MODEL_NAME", "ibm-granite/granite-4.0-h-micro")
    
    # Validation
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found. Please check your .env file.")
        return

    print(f"🧪 Testing Model: {model_name}")
    print("--------------------------------------------------")

    try:
        # 3. Make the Request
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                # Optional headers for OpenRouter rankings
                "HTTP-Referer": "http://localhost:7777", 
                "X-Title": "Granite Test Script", 
            },
            data=json.dumps({
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": "What is the meaning of life?"
                    }
                ]
            })
        )

        # 4. Check for HTTP errors (4xx or 5xx)
        response.raise_for_status()

        # 5. Parse and Print Results
        result = response.json()
        
        # Print the actual text response clearly
        print("\n🤖 Assistant Response:")
        if "choices" in result and result["choices"]:
            print(result["choices"][0]["message"]["content"])
        else:
            print("No content returned.")

        # Print full debug info
        print("\n\n📦 Full JSON Response (Debug Info):")
        print(json.dumps(result, indent=2))

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        if response is not None:
             print(f"Status Code: {response.status_code}")
             print(f"Response Text: {response.text}")

if __name__ == "__main__":
    run_test()