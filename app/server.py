from fastapi import FastAPI, UploadFile, HTTPException, Path, BackgroundTasks
from fastapi.responses import JSONResponse
from bson import ObjectId
import logging
from typing import Optional

# custom imports
from .utils.file import save_file, validate_file, generate_file_path, get_file_size
from .db.collections.files import files_collection, FileSchema
from .queue.queue import queue
from .queue.workers import process_file
from .config import HOST, PORT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Nexus PDF Processor",
    description="A PDF processing service that converts PDFs to images and analyzes them with AI",
    version="1.0.0"
)

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Nexus PDF Processor",
        "version": "1.0.0"
    }

@app.get("/files/{file_id}")
async def get_file(file_id: str = Path(..., description="The ID of the file to retrieve")):
    """Get file processing status and results"""
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(file_id):
            raise HTTPException(status_code=400, detail="Invalid file ID format")
        
        db_file = await files_collection.find_one({"_id": ObjectId(file_id)})
        
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "file_id": str(db_file["_id"]),
            "name": db_file["name"],
            "status": db_file["status"],
            "result": db_file.get("result"),
            "error": db_file.get("error"),
            "created_at": db_file.get("created_at"),
            "updated_at": db_file.get("updated_at"),
            "file_size": db_file.get("file_size"),
            "image_paths": db_file.get("image_paths")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving file {file_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/upload")
async def upload_file(file: UploadFile, background_tasks: BackgroundTasks):
    """Upload and process a PDF file"""
    try:
        # Read file content
        file_content = await file.read()
        
        # Validate file
        is_valid, validation_error = validate_file(file_content, file.filename)
        if not is_valid:
            raise HTTPException(status_code=400, detail=validation_error)
        
        # Create file record in database
        file_schema = FileSchema(
            name=file.filename,
            status="saving",
            file_size=len(file_content)
        )
        
        db_file = await files_collection.insert_one(file_schema.dict())
        file_id = str(db_file.inserted_id)
        
        # Generate file path and save file
        file_path = generate_file_path(file_id, file.filename)
        save_success = await save_file(file_content, file_path)
        
        if not save_success:
            # Cleanup database record if file save failed
            await files_collection.delete_one({"_id": db_file.inserted_id})
            raise HTTPException(status_code=500, detail="Failed to save file")
        
        # Update database with file path
        await files_collection.update_one(
            {"_id": db_file.inserted_id},
            {
                "$set": {
                    "file_path": file_path,
                    "status": "queued",
                    "updated_at": "$$NOW"
                }
            }
        )
        
        # Add processing job to queue
        try:
            job = queue.enqueue(process_file, file_id, file_path, job_id=file_id)
            logger.info(f"Added file {file_id} to processing queue")
        except Exception as e:
            logger.error(f"Failed to add file {file_id} to queue: {e}")
            # Update status to failed if queue addition fails
            await files_collection.update_one(
                {"_id": db_file.inserted_id},
                {
                    "$set": {
                        "status": "failed",
                        "error": f"Failed to add to processing queue: {e}",
                        "updated_at": "$$NOW"
                    }
                }
            )
            raise HTTPException(status_code=500, detail="Failed to queue file for processing")
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "status": "queued",
            "message": "File uploaded and queued for processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/files")
async def list_files(limit: int = 10, offset: int = 0):
    """List recent files with pagination"""
    try:
        cursor = files_collection.find().sort("created_at", -1).skip(offset).limit(limit)
        files = await cursor.to_list(length=limit)
        
        return {
            "files": [
                {
                    "file_id": str(file["_id"]),
                    "name": file["name"],
                    "status": file["status"],
                    "created_at": file.get("created_at"),
                    "file_size": file.get("file_size")
                }
                for file in files
            ],
            "total": len(files),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/files/{file_id}")
async def delete_file(file_id: str = Path(..., description="The ID of the file to delete")):
    """Delete a file and its processing results"""
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(file_id):
            raise HTTPException(status_code=400, detail="Invalid file ID format")
        
        # Find file in database
        db_file = await files_collection.find_one({"_id": ObjectId(file_id)})
        
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete from database
        await files_collection.delete_one({"_id": ObjectId(file_id)})
        
        # TODO: Clean up associated files from storage
        
        return {"message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file {file_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )