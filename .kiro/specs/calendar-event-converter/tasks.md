# Implementation Plan: Calendar Event Converter

## Overview

This implementation plan breaks down the Calendar Event Converter into discrete coding tasks. The approach follows a bottom-up strategy: build core components first (parser, extractor, generator), then the service layer, and finally the API/UI interfaces. Each task includes property-based tests to validate correctness properties from the design document.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create Python project with uv package manager
  - Set up directory structure: `src/`, `tests/`, `config/`
  - Add dependencies: fastapi, uvicorn, pypdf, python-docx, icalendar, openai, pyyaml, hypothesis, pytest
  - Create Dockerfile with Python base image and uv installation
  - Create docker-compose.yml for container orchestration
  - _Requirements: 6.1, 6.2_

- [x] 2. Implement configuration management
  - [x] 2.1 Create configuration data models (LLMConfig, ServerConfig)
    - Define dataclasses for configuration structure
    - _Requirements: 7.1_
  
  - [x] 2.2 Implement configuration loader
    - Read and parse config.yaml file
    - Provide default values for LM Studio connection
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [x] 2.3 Write unit tests for configuration loading
    - Test default configuration values
    - Test custom configuration override
    - _Requirements: 7.2, 7.3_
  
  - [x] 2.4 Write property test for configuration override
    - **Property 13: Configuration Override**
    - **Validates: Requirements 7.5**

- [x] 3. Implement document parser
  - [x] 3.1 Create DocumentParser class with parse method
    - Implement factory pattern for file type selection
    - Implement PDF parsing using pypdf
    - Implement DOCX parsing using python-docx
    - Implement TXT parsing with UTF-8 decoding
    - Raise ParsingError for unsupported or corrupted files
    - _Requirements: 1.1, 1.3, 1.4_
  
  - [x] 3.2 Write property test for text extraction consistency
    - **Property 1: Text Extraction Consistency**
    - **Validates: Requirements 1.1**
  
  - [x] 3.3 Write property test for invalid document error handling
    - **Property 3: Invalid Document Error Handling**
    - **Validates: Requirements 1.3**
  
  - [x] 3.4 Write unit tests for document parser
    - Test parsing sample PDF, DOCX, and TXT files
    - Test error handling for corrupted files
    - _Requirements: 1.4_

- [x] 4. Implement data models
  - [x] 4.1 Create EventData dataclass with validation
    - Define fields: event_name, start_datetime, end_datetime, location, description
    - Implement validate() method checking required fields and datetime logic
    - _Requirements: 2.3, 2.5_
  
  - [x] 4.2 Create custom exception classes
    - Define CalendarConverterError, ParsingError, LLMError, ExtractionError, ValidationError
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [x] 4.3 Write property test for datetime validation
    - **Property 7: Datetime Validation**
    - **Validates: Requirements 2.5**

- [x] 5. Implement LLM extractor
  - [x] 5.1 Create LLMExtractor class
    - Initialize OpenAI client with configuration
    - Implement extract_event_data method
    - Craft system prompt for event extraction in JSON format
    - Parse LLM JSON response into EventData
    - Validate required fields are present
    - Raise LLMError for communication failures
    - Raise ExtractionError for missing required fields
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [x] 5.2 Write property test for LLM request formation
    - **Property 4: LLM Request Formation**
    - **Validates: Requirements 2.1, 2.2**
  
  - [x] 5.3 Write property test for event data extraction completeness
    - **Property 5: Event Data Extraction Completeness**
    - **Validates: Requirements 2.3**
  
  - [x] 5.4 Write property test for missing field detection
    - **Property 6: Missing Field Detection**
    - **Validates: Requirements 2.4**
  
  - [x] 5.5 Write unit tests for LLM extractor
    - Test with mocked successful LLM responses
    - Test with mocked error responses
    - Test with incomplete event data
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 6. Checkpoint - Ensure core components work
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement CalDAV generator
  - [x] 7.1 Create CalDAVGenerator class
    - Implement generate_ics method using icalendar library
    - Create VCALENDAR component with VERSION 2.0
    - Create VEVENT with UID (UUID), DTSTAMP, DTSTART, DTEND, SUMMARY, LOCATION, DESCRIPTION
    - Default end_datetime to start_datetime + 1 hour if not provided
    - Validate generated ICS structure
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 7.2 Write property test for ICS generation round-trip
    - **Property 8: ICS Generation Round-Trip**
    - **Validates: Requirements 3.1, 3.4, 3.5**
  
  - [x] 7.3 Write property test for event data preservation
    - **Property 9: Event Data Preservation**
    - **Validates: Requirements 3.2**
  
  - [x] 7.4 Write property test for UID uniqueness
    - **Property 10: UID Uniqueness**
    - **Validates: Requirements 3.3**
  
  - [x] 7.5 Write unit tests for CalDAV generator
    - Test ICS generation with complete EventData
    - Test ICS generation with minimal EventData
    - Test default end_datetime behavior
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 8. Implement event conversion service
  - [x] 8.1 Create EventConversionService class
    - Inject DocumentParser, LLMExtractor, CalDAVGenerator as dependencies
    - Implement convert_document method (parse → extract → generate)
    - Implement convert_text method (extract → generate, treating text as pre-parsed)
    - Handle errors at each pipeline stage
    - Add logging for debugging
    - _Requirements: 1.1, 1.2, 2.1, 3.1, 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [x] 8.2 Write property test for plain text identity
    - **Property 2: Plain Text Identity**
    - **Validates: Requirements 1.2**
  
  - [x] 8.3 Write property test for comprehensive error handling
    - **Property 12: Comprehensive Error Handling**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**
  
  - [x] 8.4 Write integration tests for conversion service
    - Test end-to-end document conversion
    - Test end-to-end text conversion
    - Test error propagation through pipeline
    - _Requirements: 1.1, 1.2, 2.1, 3.1_

- [x] 9. Checkpoint - Ensure service layer works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement REST API endpoints
  - [x] 10.1 Create FastAPI application with API routes
    - Define POST /api/v1/convert/document endpoint (multipart/form-data)
    - Define POST /api/v1/convert/text endpoint (JSON)
    - Inject EventConversionService into endpoints
    - Return ICS content with appropriate headers for success
    - Return JSON error responses with HTTP status codes for failures
    - Implement file size validation
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [x] 10.2 Write property test for API success response format
    - **Property 11: API Success Response Format**
    - **Validates: Requirements 5.3**
  
  - [x] 10.3 Write property test for API error response format
    - **Property 14: API Error Response Format**
    - **Validates: Requirements 5.4**
  
  - [x] 10.4 Write unit tests for API endpoints
    - Test document upload endpoint with sample files
    - Test text conversion endpoint with sample text
    - Test error responses for invalid inputs
    - Test file size limit validation
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 11. Implement web UI
  - [x] 11.1 Create HTML template with drag-and-drop and text input
    - Create static HTML page with drag-and-drop area
    - Add text input field
    - Add JavaScript for file upload and form submission
    - Display download link on success
    - Display error messages on failure
    - Add loading indicators during processing
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [x] 11.2 Create FastAPI routes for UI
    - Define GET / endpoint to serve HTML page
    - Define POST /convert/document endpoint for UI file uploads
    - Define POST /convert/text endpoint for UI text submissions
    - Return ICS files with Content-Disposition: attachment header
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [x] 11.3 Write unit tests for UI endpoints
    - Test HTML page is served correctly
    - Test UI conversion endpoints return downloadable files
    - Test error display in UI responses
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 12. Implement application entry point and wiring
  - [x] 12.1 Create main application module
    - Load configuration from config.yaml
    - Initialize DocumentParser, LLMExtractor, CalDAVGenerator
    - Initialize EventConversionService with dependencies
    - Create FastAPI app with all routes
    - Add error handlers for custom exceptions
    - Add logging configuration
    - _Requirements: 7.1, 8.5_
  
  - [x] 12.2 Create default config.yaml file
    - Set LM Studio defaults (http://host.docker.internal:1234/v1, ibm/granite-4-h-tiny)
    - Set server defaults (host: 0.0.0.0, port: 8000)
    - Set limits (max_file_size_mb: 10, max_text_length: 50000)
    - _Requirements: 7.1, 7.2, 7.3_

- [x] 13. Complete Docker setup
  - [x] 13.1 Finalize Dockerfile
    - Use Python 3.11+ base image
    - Install uv package manager
    - Copy project files and install dependencies
    - Expose port 8000
    - Set CMD to run uvicorn server
    - _Requirements: 6.1, 6.2, 6.4_
  
  - [x] 13.2 Create docker-compose.yml
    - Define service for calendar-converter
    - Mount config.yaml as volume
    - Map port 8000
    - Set network mode to allow host.docker.internal access
    - _Requirements: 6.1, 6.3_
  
  - [x] 13.3 Write container integration tests
    - Test container starts successfully
    - Test health check endpoint responds
    - Test container can communicate with external services
    - _Requirements: 6.3, 6.4_

- [x] 14. Create documentation and README
  - [x] 14.1 Write README.md
    - Document project overview and features
    - Provide setup instructions (Docker build and run)
    - Document API endpoints with examples
    - Document configuration options
    - Provide usage examples for UI and API
    - _Requirements: All_
  
  - [x] 14.2 Add inline code documentation
    - Add docstrings to all classes and methods
    - Add type hints throughout codebase
    - _Requirements: All_

- [ ] 15. Final checkpoint - End-to-end validation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- All tasks are required for comprehensive implementation
- Each task references specific requirements for traceability
- Property tests use Hypothesis library with minimum 100 iterations
- All tests run inside Docker container to ensure environment consistency
- The implementation follows a bottom-up approach: core components → service layer → interfaces
