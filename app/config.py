import os
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("MONGO_URI"):
    raise ValueError("MONGO_URI environment variable is not set.")

if not os.getenv("REDIS_PASS"):
    raise ValueError("REDIS_PASS environment variable is not set.")

if not os.getenv("REDIS_HOST"):
    raise ValueError("REDIS_HOST environment variable is not set.")

if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

mongo_uri = os.getenv("MONGO_URI")
redis_pass = os.getenv("REDIS_PASS")
redis_host = os.getenv("REDIS_HOST")
gemini_api_key = os.getenv("GEMINI_API_KEY")