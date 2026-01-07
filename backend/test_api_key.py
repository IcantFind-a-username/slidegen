import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY", "")

print("=" * 60)
print("API KEY CHECK")
print("=" * 60)

if not api_key:
    print("[ERROR] OPENAI_API_KEY not found in .env file")
elif len(api_key) < 20:
    print(f"[ERROR] API key too short: {len(api_key)} characters")
elif not api_key.startswith("sk-"):
    print(f"[ERROR] API key should start with 'sk-', got: {api_key[:10]}...")
else:
    print(f"[OK] API key found: {api_key[:15]}...{api_key[-8:]}")
    print(f"[OK] Length: {len(api_key)} characters")
    
    # Test OpenAI connection
    print("\nTesting OpenAI connection...")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5
        )
        
        print("[OK] OpenAI API connection successful!")
        print(f"[OK] Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"[ERROR] OpenAI API test failed: {e}")

print("=" * 60)

