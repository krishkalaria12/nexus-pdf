from pydantic import Field, BaseModel
from typing import Optional, List
from datetime import datetime
from pymongo.asynchronous.collection import AsyncCollection

# custom imports
from ..db import database
from ...config import COLLECTION_NAME

class FileSchema(BaseModel):
    name: str = Field(..., description="Name of the file")
    status: str = Field(..., description="Status of the file processing")
    file_path: Optional[str] = Field(None, description="Path to the uploaded file")
    result: Optional[str] = Field(None, description="Result of the file processing")
    error: Optional[str] = Field(None, description="Error message if processing failed")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="File creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    image_paths: Optional[List[str]] = Field(None, description="Paths to converted images")
    file_size: Optional[int] = Field(None, description="File size in bytes")

files_collection: AsyncCollection = database[COLLECTION_NAME]

async def create_file_indexes():
    """Create indexes for better query performance"""
    try:
        await files_collection.create_index("status")
        await files_collection.create_index("created_at")
        await files_collection.create_index("name")
    except Exception as e:
        print(f"Failed to create indexes: {e}")