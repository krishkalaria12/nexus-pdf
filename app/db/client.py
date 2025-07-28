from pymongo import AsyncMongoClient

# custom imports
from ..config import mongo_uri

mongo_client: AsyncMongoClient = AsyncMongoClient(mongo_uri)