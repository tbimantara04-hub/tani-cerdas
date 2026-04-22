import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model_name = "gemini-1.5-flash"
try:
    print(f"Testing {model_name} with genai...")
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Say hello")
    print(f"Success: {response.text}")
except Exception as e:
    print(f"Failed: {e}")

model_name = "gemini-1.5-flash-latest"
try:
    print(f"Testing {model_name} with genai...")
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Say hello")
    print(f"Success: {response.text}")
except Exception as e:
    print(f"Failed: {e}")
