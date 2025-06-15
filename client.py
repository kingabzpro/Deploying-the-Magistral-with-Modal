import asyncio
import json
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
api_key = os.getenv("VLLM_API_KEY")

# Set up the OpenAI client with custom base URL
client = OpenAI(
    api_key=api_key,
    base_url="https://abidali899--magistral-small-vllm-serve.modal.run/v1",
)

MODEL_NAME = "mistralai/Magistral-Small-2506"


# --- 1. Simple Completion ---
def run_simple_completion():
    print("\n" + "=" * 40)
    print("[1] SIMPLE COMPLETION DEMO")
    print("=" * 40)
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"},
        ]
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=32,
        )
        print("\nResponse:\n    " + response.choices[0].message.content.strip())
    except Exception as e:
        print(f"[ERROR] Simple completion failed: {e}")
    print("\n" + "=" * 40 + "\n")


# --- 2. Streaming Example ---
def run_streaming():
    print("\n" + "=" * 40)
    print("[2] STREAMING DEMO")
    print("=" * 40)
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a short poem about AI."},
        ]
        stream = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=64,
            stream=True,
        )
        print("\nStreaming response:")
        print("    ", end="")
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
        print("\n[END OF STREAM]")
    except Exception as e:
        print(f"[ERROR] Streaming demo failed: {e}")
    print("\n" + "=" * 40 + "\n")


# --- 3. Async Streaming Example ---
async def run_async_streaming():
    print("\n" + "=" * 40)
    print("[3] ASYNC STREAMING DEMO")
    print("=" * 40)
    try:
        async_client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://abidali899--magistral-small-vllm-serve.modal.run/v1",
        )
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me a fun fact about space."},
        ]
        stream = await async_client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=32,
            stream=True,
        )
        print("\nAsync streaming response:")
        print("    ", end="")
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
        print("\n[END OF ASYNC STREAM]")
    except Exception as e:
        print(f"[ERROR] Async streaming demo failed: {e}")
    print("\n" + "=" * 40 + "\n")



if __name__ == "__main__":
    run_simple_completion()
    run_streaming()
    asyncio.run(run_async_streaming())
