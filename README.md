# Nexus PDF Processor

A modular, scalable PDF processing service that converts PDFs to images and analyzes them using AI (Gemini). Built with FastAPI, MongoDB, Redis, and RQ for robust asynchronous processing.

## Features

- **PDF to Image Conversion**: Convert PDF pages to high-quality JPEG images
- **AI Analysis**: Analyze images using Google's Gemini AI model
- **Asynchronous Processing**: Queue-based processing with Redis and RQ
- **RESTful API**: Clean FastAPI endpoints for file upload and status checking
- **Modular Architecture**: Well-structured, composable codebase
- **Error Handling**: Comprehensive error handling and logging
- **File Validation**: Security-focused file validation
- **Database Storage**: MongoDB for persistent storage
- **Status Tracking**: Real-time processing status updates

## Architecture

```
nexus-pdf/
├── app/
│   ├── config.py              # Configuration management
│   ├── main.py                # Application entry point
│   ├── server.py              # FastAPI server and routes
│   ├── db/                    # Database layer
│   │   ├── client.py          # MongoDB client
│   │   ├── db.py              # Database connection
│   │   └── collections/       # Database collections
│   │       └── files.py       # File schema and operations
│   ├── queue/                 # Queue processing
│   │   ├── queue.py           # Redis queue setup
│   │   └── workers.py         # Background workers
│   └── utils/                 # Utility modules
│       ├── ai_call.py         # AI processing utilities
│       ├── file.py            # File handling utilities
│       ├── logger.py          # Logging utilities
│       ├── validators.py      # Validation utilities
│       └── errors.py          # Custom error handling
├── pyproject.toml             # Project dependencies
└── README.md                  # This file
```

## API Endpoints

### Health Check
- `GET /` - Health check endpoint

### File Management
- `POST /upload` - Upload and process a PDF file
- `GET /files/{file_id}` - Get file processing status and results
- `GET /files` - List recent files with pagination
- `DELETE /files/{file_id}` - Delete a file and its results

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nexus-pdf
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   ```

3. **Install system dependencies**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install poppler-utils
   
   # macOS
   brew install poppler
   
   # Arch Linux
   sudo pacman -S poppler
   ```

4. **Set up environment variables**
   Create a `.env` file:
   ```env
   MONGO_URI=mongodb://localhost:27017
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_PASS=your_redis_password
   GEMINI_API_KEY=your_gemini_api_key
   UPLOAD_DIR=/mnt/uploads
   IMAGE_DIR=/mnt/uploads/images
   MAX_FILE_SIZE=10485760
   ```

5. **Start the services**
   ```bash
   # Start MongoDB
   sudo systemctl start mongod
   
   # Start Redis
   sudo systemctl start redis
   
   # Start the application
   python -m app.main
   ```

6. **Start the worker**
   ```bash
   # In a separate terminal
   rq worker
   ```

## Usage

### Upload a PDF
```bash
curl -X POST "http://localhost:8000/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_resume.pdf"
```

### Check Processing Status
```bash
curl "http://localhost:8000/files/{file_id}"
```

### List Files
```bash
curl "http://localhost:8000/files?limit=10&offset=0"
```

## Configuration

The application uses environment variables for configuration:

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGO_URI` | MongoDB connection string | Required |
| `REDIS_HOST` | Redis host | localhost |
| `REDIS_PORT` | Redis port | 6379 |
| `REDIS_PASS` | Redis password | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `UPLOAD_DIR` | File upload directory | /mnt/uploads |
| `IMAGE_DIR` | Image storage directory | /mnt/uploads/images |
| `MAX_FILE_SIZE` | Maximum file size in bytes | 10485760 (10MB) |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |

## Development

### Code Style
- Uses Black for code formatting
- Type hints throughout
- Comprehensive error handling
- Modular function-based architecture

### Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

### Logging
The application uses structured logging with different levels:
- INFO: General application flow
- ERROR: Error conditions
- DEBUG: Detailed debugging information

## Error Handling

The application includes comprehensive error handling:
- File validation errors
- Processing errors
- AI processing errors
- Database errors
- Queue errors

All errors are logged and returned with appropriate HTTP status codes.

## Security Features

- File type validation (PDF only)
- File size limits
- Filename sanitization
- Input validation
- Error message sanitization

## Performance

- Asynchronous processing with RQ
- Connection pooling for MongoDB
- Redis for fast queue operations
- Efficient PDF to image conversion
- Parallel AI processing for multiple pages

## Monitoring

- Health check endpoint
- Processing status tracking
- Error logging
- Performance metrics

## License

MIT License
