import os
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("MONGO_URI"):
    raise ValueError("MONGO_URI environment variable is not set.")

mongo_uri = os.getenv("MONGO_URI")