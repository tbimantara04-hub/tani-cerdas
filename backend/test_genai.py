import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GITHUB_TOKEN")

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=api_key
)

try:
    print("Testing gpt-4o-mini with openai SDK on GitHub Models...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Say hello"}
        ]
    )
    print(f"Success: {response.choices[0].message.content}")
except Exception as e:
    print(f"Failed: {e}")
