from bson import ObjectId
import os

from pdf2image import convert_from_path
import base64

# custom imports
from app.db.collections.files import files_collection
from app.utils.ai_call import process_image_with_ai

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

async def process_file(id: str, file_path: str):
    await files_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": "processing"}}
    )

    # Convert pdf to image

    images = convert_from_path(file_path)
    image_paths = []

    for i, page in enumerate(images):
        image_path = f"/mnt/uploads/images/{id}/images-{i}.jpg"
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        page.save(image_path, "JPEG")
        image_paths.append(image_path)

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

    # Getting the Base64 string
    base64_image = [encode_image(image_path) for img in image_paths]

    response = await process_image_with_ai(base64_image[0])

    await files_collection.update_one(
        {
            "_id": ObjectId(id)
            },
        {
            "$set": {
                "status": "success",
                "result": response,
            }
        }
    )