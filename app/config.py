import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set.")

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASS")
REDIS_USERNAME = os.getenv("REDIS_USERNAME", "default")

if not REDIS_PASSWORD:
    raise ValueError("REDIS_PASS environment variable is not set.")

# AI Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

# File Storage Configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/mnt/uploads")
IMAGE_DIR = os.getenv("IMAGE_DIR", "/mnt/uploads/images")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# AI Model Configuration
AI_MODEL = os.getenv("AI_MODEL", "gemini-2.5-flash")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")

# Database Configuration
DATABASE_NAME = os.getenv("DATABASE_NAME", "nexus_pdf")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "files")