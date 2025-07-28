from .client import mongo_client
from ..config import DATABASE_NAME

database = mongo_client[DATABASE_NAME]