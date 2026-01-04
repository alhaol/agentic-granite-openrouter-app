import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

def get_api_key():
    """Retrieves the API key from environment variables."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not found in .env file.")
        print("Please create a .env file with your API key.")
        sys.exit(1)
    return api_key

def main():
    """Main function to run the Granite chat loop."""
    
    # Configuration
    API_KEY = get_api_key()
    BASE_URL = "https://openrouter.ai/api/v1"
    MODEL_ID = "ibm-granite/granite-4.0-h-micro"
    
    # Initialize the OpenAI client pointing to OpenRouter
    client = OpenAI(
        base_url=BASE_URL,
        api_key=API_KEY,
        # Optional headers required by OpenRouter for rankings
        default_headers={
            "HTTP-Referer": "http://localhost:3000", # Replace with your site URL
            "X-Title": "Granite Console Chat",      # Replace with your app name
        }
    )

    print(f"--- Chatting with {MODEL_ID} ---")
    print("Type 'quit', 'exit', or 'q' to end the session.\n")

    # Conversation history
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ]

    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue

            # Add user message to history
            messages.append({"role": "user", "content": user_input})

            # Create the completion request
            stream = client.chat.completions.create(
                model=MODEL_ID,
                messages=messages,
                stream=True  # Enable streaming for a better chat experience
            )

            print("Granite: ", end="", flush=True)
            
            collected_response = ""
            
            # Process the stream
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    print(content, end="", flush=True)
                    collected_response += content
            
            print() # Newline after response is complete

            # Add assistant response to history to maintain context
            messages.append({"role": "assistant", "content": collected_response})

        except KeyboardInterrupt:
            print("\n\nExiting chat...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()