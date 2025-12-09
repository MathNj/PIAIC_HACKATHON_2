"""Test script to verify Gemini API access."""
import asyncio
import os
from openai import AsyncOpenAI

async def test_gemini():
    api_key = "AIzaSyB6lhYw7jAoGNLmuQODT0tQEOCjcMkgg30"

    print(f"Testing Gemini API...")
    print(f"API Key: {api_key[:20]}...")

    try:
        # Test with OpenAI-compatible endpoint
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        print("\nListing available models...")
        models = await client.models.list()
        print("Available models:")
        for model in models.data:
            print(f"  - {model.id}")

        # Try the exact model we're using in the agent
        test_model = "models/gemini-2.5-flash"
        print(f"\nTrying model: {test_model}...")
        response = await client.chat.completions.create(
            model=test_model,
            messages=[
                {"role": "user", "content": "Say 'Hello, World!' and nothing else."}
            ]
        )

        print(f"SUCCESS!")
        print(f"Response: {response.choices[0].message.content}")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(f"\nFull error details:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini())
