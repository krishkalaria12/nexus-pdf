from fastapi import FastAPI, UploadFile
from uuid import uuid4

# custom imports 
from .utils.file import save_file

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello, World!"}

@app.post("/upload")
async def file_upload(
        file: UploadFile
):
    id = uuid4()

    file_path = f"/mnt/uploads/{id}-{file.filename}"
    await save_file(file, file_path)

    return {"file_id": str(id)}