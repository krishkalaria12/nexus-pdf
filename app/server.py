from fastapi import FastAPI, UploadFile

# custom imports 
from .utils.file import save_file
from .db.collections.files import files_collection, FileSchema

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello, World!"}

@app.post("/upload")
async def file_upload(
        file: UploadFile
):
    db_file = await files_collection.insert_one(
        document=FileSchema(
            name=file.filename,
            status="saving"
        )
    )

    db_file_id = str(db_file.inserted_id)

    file_path = f"/mnt/uploads/{db_file_id}-{file.filename}"
    await save_file(await file.read(), file_path)

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