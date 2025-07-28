from typing import Optional, Dict, Any

class NexusPDFError(Exception):
    """Base exception for Nexus PDF Processor"""
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class FileValidationError(NexusPDFError):
    """Raised when file validation fails"""
    pass

class FileProcessingError(NexusPDFError):
    """Raised when file processing fails"""
    pass

class AIProcessingError(NexusPDFError):
    """Raised when AI processing fails"""
    pass

class DatabaseError(NexusPDFError):
    """Raised when database operations fail"""
    pass

class QueueError(NexusPDFError):
    """Raised when queue operations fail"""
    pass

class ConfigurationError(NexusPDFError):
    """Raised when configuration is invalid"""
    pass

def handle_processing_error(error: Exception, context: str = "") -> Dict[str, Any]:
    """Standardized error handling for processing operations"""
    error_info = {
        "error_type": type(error).__name__,
        "message": str(error),
        "context": context
    }
    
    if isinstance(error, NexusPDFError):
        error_info.update({
            "error_code": error.error_code,
            "details": error.details
        })
    
    return error_info 