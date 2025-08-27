### Core Functionality
- FastAPI application that acts as a middleware between clients and a Tika service
- Main endpoint `/process` that:
    - Accepts file data via PUT requests
    - Determines appropriate Tika endpoint based on mime-type
    - For PDFs: forwards to `/tika/text`
    - For other files: forwards to `/tika`
    - Returns document content in the format expected by `ExternalDocumentLoader`

### Dependencies
- FastAPI
- Pydantic for data validation
- Requests for HTTP calls
- Pytest for testing

### Security & Configuration
- Bearer token authentication
- Environment variables required:
    - TIKA_BASE_URL - URL of the Tika service
    - API_KEY(s) for authentication

### Docker
- Minimal base image
- No specific port requirements
- No volume mounts
- Designed for both docker-compose (dev) and kubernetes (prod)
- Configuration via environment variables

### Additional Features
- Health check endpoint
- API documentation (Swagger/OpenAPI)
- Test suite using pytest
- Error handling matching the parent application pattern

### Not Required
- Rate limiting
- Tika-python library
- Volume mounts
- Custom port configurations
