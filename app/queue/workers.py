import os
import logging
from typing import List, Optional
from bson import ObjectId
from pdf2image import convert_from_path
from pdf2image.exceptions import PDFPageCountError, PDFSyntaxError

# custom imports
from ..db.collections.files import files_collection
from ..utils.ai_call import process_multiple_images_with_ai, combine_ai_results
from ..utils.file import generate_image_paths, cleanup_files, get_file_size
from ..config import IMAGE_DIR

logger = logging.getLogger(__name__)

async def update_file_status(file_id: str, status: str, error: Optional[str] = None) -> bool:
    """Update file status in database"""
    try:
        update_data = {
            "status": status,
            "updated_at": "$$NOW"
        }
        if error:
            update_data["error"] = error
            
        await files_collection.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": update_data}
        )
        logger.info(f"Updated file {file_id} status to: {status}")
        return True
    except Exception as e:
        logger.error(f"Failed to update file {file_id} status: {e}")
        return False

async def convert_pdf_to_images(file_path: str, file_id: str) -> tuple[bool, Optional[List[str]], Optional[str]]:
    """Convert PDF to images with error handling"""
    try:
        # Create image directory
        image_dir = os.path.join(IMAGE_DIR, file_id)
        os.makedirs(image_dir, exist_ok=True)
        
        # Convert PDF to images
        images = convert_from_path(file_path, dpi=200, fmt='JPEG')
        
        if not images:
            return False, None, "No pages found in PDF"
        
        # Save images
        image_paths = []
        for i, page in enumerate(images):
            image_path = os.path.join(image_dir, f"page-{i+1}.jpg")
            page.save(image_path, "JPEG", quality=85)
            image_paths.append(image_path)
        
        logger.info(f"Successfully converted PDF to {len(image_paths)} images")
        return True, image_paths, None
        
    except PDFPageCountError as e:
        error_msg = f"PDF page count error: {e}"
        logger.error(error_msg)
        return False, None, error_msg
    except PDFSyntaxError as e:
        error_msg = f"PDF syntax error: {e}"
        logger.error(error_msg)
        return False, None, error_msg
    except Exception as e:
        error_msg = f"Failed to convert PDF to images: {e}"
        logger.error(error_msg)
        return False, None, error_msg

async def process_images_with_ai(image_paths: List[str]) -> tuple[bool, Optional[str], Optional[str]]:
    """Process images with AI"""
    try:
        # Process all images
        results = await process_multiple_images_with_ai(image_paths)
        
        # Combine results
        combined_result = combine_ai_results(results)
        
        if combined_result and combined_result != "No valid results from AI processing":
            logger.info("AI processing completed successfully")
            return True, combined_result, None
        else:
            error_msg = "AI processing failed to generate valid results"
            logger.error(error_msg)
            return False, None, error_msg
            
    except Exception as e:
        error_msg = f"AI processing failed: {e}"
        logger.error(error_msg)
        return False, None, error_msg

async def cleanup_processing_files(file_path: str, image_paths: List[str]) -> bool:
    """Clean up processing files"""
    try:
        files_to_cleanup = [file_path] + image_paths
        await cleanup_files(files_to_cleanup)
        return True
    except Exception as e:
        logger.error(f"Failed to cleanup processing files: {e}")
        return False

async def process_file(file_id: str, file_path: str) -> bool:
    """Main file processing function"""
    logger.info(f"Starting processing for file {file_id}")
    
    try:
        # Update status to processing
        await update_file_status(file_id, "processing")
        
        # Convert PDF to images
        conversion_success, image_paths, conversion_error = await convert_pdf_to_images(file_path, file_id)
        
        if not conversion_success:
            await update_file_status(file_id, "failed", conversion_error)
            return False
        
        # Update status after conversion
        await update_file_status(file_id, "converting_to_image_success")
        
        # Update database with image paths
        await files_collection.update_one(
            {"_id": ObjectId(file_id)},
            {
                "$set": {
                    "image_paths": image_paths,
                    "updated_at": "$$NOW"
                }
            }
        )
        
        # Process images with AI
        ai_success, ai_result, ai_error = await process_images_with_ai(image_paths)
        
        if not ai_success:
            await update_file_status(file_id, "failed", ai_error)
            return False
        
        # Update final status and result
        await files_collection.update_one(
            {"_id": ObjectId(file_id)},
            {
                "$set": {
                    "status": "success",
                    "result": ai_result,
                    "updated_at": "$$NOW"
                }
            }
        )
        
        logger.info(f"Successfully processed file {file_id}")
        
        # Cleanup temporary files
        await cleanup_processing_files(file_path, image_paths)
        
        return True
        
    except Exception as e:
        error_msg = f"Unexpected error during processing: {e}"
        logger.error(error_msg)
        await update_file_status(file_id, "failed", error_msg)
        return False