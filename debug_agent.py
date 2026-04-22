import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

load_dotenv("backend/.env")
api_key = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)

@tool
def get_weather(city: str):
    """Get weather for a city."""
    return f"The weather in {city} is sunny."

tools = [get_weather]
prompt = "You are a helpful assistant."

try:
    print("Creating agent...")
    agent = create_react_agent(llm, tools, messages_modifier=prompt)
    print("Agent created successfully.")
    
    print("Invoking agent...")
    result = agent.invoke({"messages": [HumanMessage(content="What is the weather in Jakarta?")]})
    print("Result:", result["messages"][-1].content)
except Exception as e:
    import traceback
    traceback.print_exc()
