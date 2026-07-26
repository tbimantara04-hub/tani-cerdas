import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
api_key = os.getenv("GITHUB_TOKEN")

models_to_test = ["gpt-4o-mini", "gpt-4o", "meta-llama-3.1-405b-instruct"]

for model in models_to_test:
    try:
        print(f"Testing model: {model}")
        llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url="https://models.inference.ai.azure.com",
            temperature=0.1
        )
        response = llm.invoke("Say hello")
        print(f"Success with {model}: {response.content}")
        break
    except Exception as e:
        print(f"Failed with {model}: {e}")
