import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv(".env")

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

found = False
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"FOUND_MODEL:{m.name}")
        found = True
        break
if not found:
    print("NO_MODEL_FOUND")
