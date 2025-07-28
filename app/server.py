from fastapi import FastAPI, UploadFile, Path
from bson import ObjectId

# custom imports 
from .utils.file import save_file
from .db.collections.files import files_collection, FileSchema
from app.queue.queue import queue
from app.queue.workers import process_file

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello, World!"}

@app.get("/{id}")
async def get_file(id: str = Path(..., description="The ID of the file to retrieve")):
    db_file = await files_collection.find_one({"_id": ObjectId(id)})

    if not db_file:
        return {"error": "File not found"}

    return {
        "_id": str(db_file["_id"]),
        "name": db_file["name"],
        "status": db_file["status"],
        "result": db_file.get("result", None),
    }

@app.post("/upload")
async def file_upload(
        file: UploadFile
):
    db_file = await files_collection.insert_one(
        document=FileSchema(
            name=file.filename,
            status="saving",
        )
    )

    db_file_id = str(db_file.inserted_id)

    file_path = f"/mnt/uploads/{db_file_id}-{file.filename}"
    await save_file(await file.read(), file_path)

    # push to queue
    job = queue.enqueue(process_file(id, file_path), db_file_id)

    await files_collection.update_one(
        {
            "_id": db_file.inserted_id
        },
        {
            "$set": {
                "status": "queued",
            }
        }
    )

    return {"file_id": db_file_id}