import os
import aiofiles
import logging
from typing import List, Optional
from pathlib import Path
import mimetypes

from ..config import UPLOAD_DIR, IMAGE_DIR, MAX_FILE_SIZE

logger = logging.getLogger(__name__)

async def save_file(file_content: bytes, file_path: str) -> bool:
    """Save file content to specified path with error handling"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            await out_file.write(file_content)
        
        logger.info(f"File saved successfully: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save file {file_path}: {e}")
        return False

def validate_file(file_content: bytes, filename: str) -> tuple[bool, Optional[str]]:
    """Validate uploaded file"""
    # Check file size
    if len(file_content) > MAX_FILE_SIZE:
        return False, f"File size exceeds maximum limit of {MAX_FILE_SIZE} bytes"
    
    # Check file type
    mime_type, _ = mimetypes.guess_type(filename)
    if not mime_type or mime_type != 'application/pdf':
        return False, "Only PDF files are allowed"
    
    return True, None

def generate_file_path(file_id: str, filename: str) -> str:
    """Generate file path for uploaded file"""
    return os.path.join(UPLOAD_DIR, f"{file_id}-{filename}")

def generate_image_paths(file_id: str, page_count: int) -> List[str]:
    """Generate image paths for converted PDF pages"""
    image_paths = []
    for i in range(page_count):
        image_path = os.path.join(IMAGE_DIR, file_id, f"page-{i+1}.jpg")
        image_paths.append(image_path)
    return image_paths

async def cleanup_files(file_paths: List[str]) -> bool:
    """Clean up temporary files"""
    try:
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to cleanup files: {e}")
        return False

def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0