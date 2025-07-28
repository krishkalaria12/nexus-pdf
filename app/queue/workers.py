# custom imports
from app.db.collections.files import files_collection
from bson import ObjectId
import os

from pdf2image import convert_from_path

async def process_file(id: str, file_path: str):
    await files_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": "processing"}}
    )

    # Convert pdf to image

    images = convert_from_path(file_path)

    for i, page in enumerate(images):
        image_path = f"/mnt/uploads/images/{id}/images-{i}.jpg"
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        page.save(image_path, "JPEG")

    await files_collection.update_one(
        {
            "_id": ObjectId(id)
            },
        {
            "$set": {
                "status": "converting to image success"
            }
        }
    )

