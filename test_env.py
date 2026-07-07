from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("GEMINI_API_KEY")

if key:
    print("✅ API Key Loaded")
    print(key[:10] + "...")
else:
    print("❌ API Key Not Found")