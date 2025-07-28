# custom imports
from app.db.db import database
from bson import ObjectId

async def process_file(id: str):
    await database.files_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": "processing"}}
    )