import sys
from types import ModuleType

try:
    import google.generativeai.plugins
except ImportError:
    m = ModuleType("google.generativeai.plugins")
    m.get_plugins = lambda: []
    sys.modules["google.generativeai.plugins"] = m

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv("backend/.env")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
print(llm.invoke("Hi").content)
