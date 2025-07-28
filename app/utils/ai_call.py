import base64
import logging
from typing import Optional, List
from openai import OpenAI
import asyncio

# custom imports
from ..config import GEMINI_API_KEY, AI_MODEL, AI_BASE_URL

logger = logging.getLogger(__name__)

def create_ai_client() -> OpenAI:
    """Create OpenAI-compatible client for Gemini"""
    return OpenAI(
        api_key=GEMINI_API_KEY,
        base_url=AI_BASE_URL
    )

def encode_image_to_base64(image_path: str) -> str:
    """Encode image file to base64 string"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to encode image {image_path}: {e}")
        raise

async def process_image_with_ai(image_base64: str, prompt: str = "Based on the image, Roast the resume") -> Optional[str]:
    """Process image with AI using retry logic"""
    client = create_ai_client()
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    { 
                        "type": "input_text", 
                        "text": prompt 
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_base64}",
                    },
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            if response.choices and response.choices[0].message.content:
                logger.info("AI processing completed successfully")
                return response.choices[0].message.content
            else:
                logger.warning("AI response was empty")
                return None
                
        except Exception as e:
            logger.error(f"AI processing attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("All AI processing attempts failed")
                raise
    
    return None

async def process_multiple_images_with_ai(image_paths: List[str], prompt: str = "Based on the image, Roast the resume") -> List[Optional[str]]:
    """Process multiple images with AI"""
    results = []
    
    for image_path in image_paths:
        try:
            base64_image = encode_image_to_base64(image_path)
            result = await process_image_with_ai(base64_image, prompt)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to process image {image_path}: {e}")
            results.append(None)
    
    return results

def combine_ai_results(results: List[Optional[str]]) -> str:
    """Combine multiple AI results into a single response"""
    valid_results = [result for result in results if result]
    
    if not valid_results:
        return "No valid results from AI processing"
    
    if len(valid_results) == 1:
        return valid_results[0]
    
    # Combine multiple results
    combined = "\n\n--- Page Break ---\n\n".join(valid_results)
    return combined