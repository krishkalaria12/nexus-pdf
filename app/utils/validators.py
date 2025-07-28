import re
from typing import Optional, Tuple
from pathlib import Path

def validate_filename(filename: str) -> Tuple[bool, Optional[str]]:
    """Validate filename for security and compatibility"""
    if not filename:
        return False, "Filename cannot be empty"
    
    # Check for dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    if any(char in filename for char in dangerous_chars):
        return False, "Filename contains invalid characters"
    
    # Check length
    if len(filename) > 255:
        return False, "Filename too long (max 255 characters)"
    
    # Check file extension
    if not filename.lower().endswith('.pdf'):
        return False, "Only PDF files are allowed"
    
    return True, None

def validate_file_size(file_size: int, max_size: int) -> Tuple[bool, Optional[str]]:
    """Validate file size"""
    if file_size <= 0:
        return False, "File size must be greater than 0"
    
    if file_size > max_size:
        return False, f"File size exceeds maximum limit of {max_size} bytes"
    
    return True, None

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace dangerous characters
    sanitized = re.sub(r'[<>:"|?*\\/]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit('.', 1)
        sanitized = name[:250] + '.' + ext
    
    return sanitized

def validate_object_id(object_id: str) -> bool:
    """Validate MongoDB ObjectId format"""
    import re
    pattern = r'^[0-9a-fA-F]{24}$'
    return bool(re.match(pattern, object_id)) 