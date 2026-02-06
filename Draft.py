from openai import OpenAI
import os
from dotenv import load_dotenv

# Load API key
load_dotenv() # An OpenAI API key should be provided using a .env file

# Check if API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    print("Warning: OPENAI_API_KEY not found in environment variables")

try:
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )
    print("OpenAI client initialized successfully")
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    client = None

models = client.models.list()
for m in models.data:
    print(m.id)