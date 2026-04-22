import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

models_to_test = ["gemini-1.5-flash", "gemini-2.0-flash-exp", "gemini-pro"]

for model in models_to_test:
    try:
        print(f"Testing model: {model}")
        llm = ChatGoogleGenerativeAI(model=model, google_api_key=api_key)
        response = llm.invoke("Say hello")
        print(f"Success with {model}: {response.content}")
        break
    except Exception as e:
        print(f"Failed with {model}: {e}")
