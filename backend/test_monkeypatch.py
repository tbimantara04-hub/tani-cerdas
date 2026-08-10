import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv("backend/.env")
api_key = os.getenv("GITHUB_TOKEN")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=api_key,
    base_url="https://models.inference.ai.azure.com",
    temperature=0.1
)
print(llm.invoke("Hi").content)
