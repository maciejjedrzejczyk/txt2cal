# Design Document: Calendar Event Converter

## Overview

The Calendar Event Converter is a containerized Python application that transforms unstructured text and documents into CalDAV-compatible calendar events using LLM-powered extraction. The system follows a pipeline architecture: input reception → content parsing → LLM extraction → CalDAV generation → response delivery.

The application provides two interfaces: a web UI for interactive use and a RESTful API for programmatic integration. All processing occurs within Docker containers, ensuring isolation and reproducibility. The system communicates with OpenAI-compatible LLM servers (defaulting to local LM Studio) to intelligently extract event details from natural language.

## Architecture

The system follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Interface Layer                       │
│  ┌──────────────────┐      ┌──────────────────────┐    │
│  │   Web UI         │      │   REST API           │    │
│  │  (FastAPI/HTML)  │      │   (FastAPI)          │    │
│  └──────────────────┘      └──────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   Service Layer                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Event Conversion Service                  │  │
│  │  (Orchestrates the conversion pipeline)          │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  Processing Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │   Document   │  │     LLM      │  │   CalDAV    │  │
│  │   Parser     │  │   Extractor  │  │  Generator  │  │
│  └──────────────┘  └──────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                     │
│  ┌──────────────┐  ┌──────────────────────────────┐    │
│  │   Config     │  │   External LLM Server        │    │
│  │   Manager    │  │   (LM Studio/OpenAI API)     │    │
│  └──────────────┘  └──────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

**Key Architectural Decisions:**

1. **FastAPI Framework**: Provides both web UI serving and REST API endpoints in a single framework with automatic OpenAPI documentation
2. **Pipeline Pattern**: Linear processing flow makes the system easy to understand, test, and extend
3. **Dependency Injection**: Configuration and external dependencies injected at startup for testability
4. **Container Isolation**: Docker ensures consistent environment and prevents host filesystem access

## Components and Interfaces

### 1. Document Parser

**Responsibility**: Extract text content from various document formats

**Interface**:
```python
class DocumentParser:
    def parse(self, file_content: bytes, file_type: str) -> str:
        """
        Extract text from document content.
        
        Args:
            file_content: Raw bytes of the document
            file_type: MIME type or file extension (e.g., 'pdf', 'docx', 'txt')
            
        Returns:
            Extracted text content
            
        Raises:
            ParsingError: If document cannot be parsed
        """
```

**Implementation Strategy**:
- Use `pypdf` for PDF files
- Use `python-docx` for DOCX files
- Direct UTF-8 decoding for TXT files
- Factory pattern to select appropriate parser based on file type

### 2. LLM Extractor

**Responsibility**: Communicate with LLM to extract structured event data from text

**Interface**:
```python
class LLMExtractor:
    def __init__(self, config: LLMConfig):
        """Initialize with LLM configuration (API endpoint, model, API key)"""
        
    def extract_event_data(self, text: str) -> EventData:
        """
        Extract event information from text using LLM.
        
        Args:
            text: Unstructured text containing event information
            
        Returns:
            EventData with extracted fields (name, datetime, location, description)
            
        Raises:
            LLMError: If LLM communication fails
            ExtractionError: If required event data cannot be extracted
        """
```

**Implementation Strategy**:
- Use OpenAI Python client library for API communication
- Craft system prompt instructing LLM to extract event fields in JSON format
- Request structured JSON output with fields: event_name, start_datetime, end_datetime, location, description
- Validate LLM response contains required fields
- Parse and validate datetime strings

### 3. CalDAV Generator

**Responsibility**: Generate valid ICS files from structured event data

**Interface**:
```python
class CalDAVGenerator:
    def generate_ics(self, event_data: EventData) -> str:
        """
        Generate CalDAV-compatible ICS file content.
        
        Args:
            event_data: Structured event information
            
        Returns:
            ICS file content as string
            
        Raises:
            ValidationError: If event data is invalid or ICS generation fails
        """
```

**Implementation Strategy**:
- Use `icalendar` library for ICS generation
- Create VCALENDAR component with VERSION 2.0
- Create VEVENT component with:
  - UID (generated using UUID)
  - DTSTAMP (current timestamp)
  - DTSTART (event start datetime)
  - DTEND (event end datetime, default to +1 hour if not provided)
  - SUMMARY (event name)
  - LOCATION (event location)
  - DESCRIPTION (event description)
- Validate generated ICS structure

### 4. Event Conversion Service

**Responsibility**: Orchestrate the conversion pipeline

**Interface**:
```python
class EventConversionService:
    def __init__(self, parser: DocumentParser, extractor: LLMExtractor, 
                 generator: CalDAVGenerator):
        """Initialize with injected dependencies"""
        
    def convert_document(self, file_content: bytes, file_type: str) -> str:
        """
        Convert document to ICS file.
        
        Returns:
            ICS file content
        """
        
    def convert_text(self, text: str) -> str:
        """
        Convert plain text to ICS file.
        
        Returns:
            ICS file content
        """
```

**Implementation Strategy**:
- Chain parser → extractor → generator
- Handle errors at each stage with appropriate error types
- Log processing steps for debugging

### 5. Web UI (FastAPI + HTML)

**Responsibility**: Provide interactive interface for users

**Endpoints**:
- `GET /` - Serve HTML page with drag-and-drop and text input
- `POST /convert/document` - Accept file upload, return ICS download
- `POST /convert/text` - Accept text input, return ICS download

**Implementation Strategy**:
- Use FastAPI's `UploadFile` for file handling
- Serve static HTML with JavaScript for drag-and-drop
- Return ICS files with `Content-Disposition: attachment` header
- Display errors in user-friendly format

### 6. REST API (FastAPI)

**Responsibility**: Provide programmatic access

**Endpoints**:
- `POST /api/v1/convert/document` - Accept multipart file, return ICS content
- `POST /api/v1/convert/text` - Accept JSON with text field, return ICS content

**Request/Response Formats**:
```python
# Text conversion request
{
    "text": "Team meeting tomorrow at 2pm in Conference Room A..."
}

# Success response
{
    "ics_content": "BEGIN:VCALENDAR\nVERSION:2.0\n...",
    "filename": "event_20250105_140000.ics"
}

# Error response
{
    "error": "Failed to extract event date from text",
    "details": "No valid datetime found in input"
}
```

### 7. Configuration Manager

**Responsibility**: Load and provide configuration settings

**Configuration File** (`config.yaml`):
```yaml
llm:
  api_base: "http://host.docker.internal:1234/v1"  # LM Studio default
  model: "ibm/granite-4-h-tiny"
  api_key: "not-needed"  # LM Studio doesn't require key
  timeout: 30

server:
  host: "0.0.0.0"
  port: 8000

limits:
  max_file_size_mb: 10
  max_text_length: 50000
```

## Data Models

### EventData

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class EventData:
    event_name: str
    start_datetime: datetime
    location: Optional[str] = None
    description: Optional[str] = None
    end_datetime: Optional[datetime] = None
    
    def validate(self) -> None:
        """
        Validate that required fields are present and valid.
        
        Raises:
            ValidationError: If validation fails
        """
        if not self.event_name or not self.event_name.strip():
            raise ValidationError("Event name is required")
        if not self.start_datetime:
            raise ValidationError("Start datetime is required")
        if self.end_datetime and self.end_datetime < self.start_datetime:
            raise ValidationError("End datetime must be after start datetime")
```

### LLMConfig

```python
@dataclass
class LLMConfig:
    api_base: str
    model: str
    api_key: str = "not-needed"
    timeout: int = 30
```

### Error Types

```python
class CalendarConverterError(Exception):
    """Base exception for all application errors"""

class ParsingError(CalendarConverterError):
    """Document parsing failed"""

class LLMError(CalendarConverterError):
    """LLM communication failed"""

class ExtractionError(CalendarConverterError):
    """Event data extraction failed"""

class ValidationError(CalendarConverterError):
    """Data validation failed"""
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Text Extraction Consistency

*For any* valid document file (PDF, DOCX, TXT), parsing the document should produce a non-empty string containing the document's text content.

**Validates: Requirements 1.1**

### Property 2: Plain Text Identity

*For any* plain text input, the system should accept and process it without modification, treating it as already-parsed content.

**Validates: Requirements 1.2**

### Property 3: Invalid Document Error Handling

*For any* invalid or corrupted document file, the parser should raise a ParsingError with a descriptive message rather than crashing or returning empty content.

**Validates: Requirements 1.3**

### Property 4: LLM Request Formation

*For any* parsed text content, the system should construct a valid OpenAI API request with proper headers, authentication, and prompt structure.

**Validates: Requirements 2.1, 2.2**

### Property 5: Event Data Extraction Completeness

*For any* LLM response containing valid event information, the extractor should successfully parse and return an EventData object with at least event_name and start_datetime populated.

**Validates: Requirements 2.3**

### Property 6: Missing Field Detection

*For any* LLM response missing required event fields (event_name or start_datetime), the system should raise an ExtractionError specifying which fields are missing.

**Validates: Requirements 2.4**

### Property 7: Datetime Validation

*For any* extracted datetime string, the system should either successfully parse it into a Python datetime object or raise a ValidationError if the format is invalid.

**Validates: Requirements 2.5**

### Property 8: ICS Generation Round-Trip

*For any* valid EventData object, generating an ICS file and then parsing it back using an iCalendar parser should produce a calendar event with equivalent data (same event name, datetime, location, description).

**Validates: Requirements 3.1, 3.4, 3.5**

### Property 9: Event Data Preservation

*For any* EventData object with specific field values, the generated ICS file content should contain those values in the appropriate VEVENT properties (SUMMARY, DTSTART, LOCATION, DESCRIPTION).

**Validates: Requirements 3.2**

### Property 10: UID Uniqueness

*For any* two separate calls to generate_ics (even with identical EventData), the generated UIDs should be different, ensuring each event has a unique identifier.

**Validates: Requirements 3.3**

### Property 11: API Success Response Format

*For any* successful conversion via the API, the response should include valid ICS content and appropriate HTTP headers (Content-Type: text/calendar, Content-Disposition with filename).

**Validates: Requirements 5.3**

### Property 12: Comprehensive Error Handling

*For any* error occurring during the conversion pipeline (parsing, LLM communication, extraction, or ICS generation), the system should return an appropriate error response with a user-friendly message and log the detailed error for debugging.

**Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**

### Property 13: Configuration Override

*For any* custom LLM configuration provided (API base URL, model name, API key), the system should use those values instead of defaults when communicating with the LLM server.

**Validates: Requirements 7.5**

### Property 14: API Error Response Format

*For any* failed conversion via the API, the response should include an appropriate HTTP error status code (4xx or 5xx) and a JSON body with error details.

**Validates: Requirements 5.4**

## Error Handling

The system uses a hierarchy of custom exceptions to handle different failure modes:

1. **ParsingError**: Raised when document parsing fails
   - Log the file type and error details
   - Return user message: "Failed to parse document. Please ensure the file is not corrupted."

2. **LLMError**: Raised when LLM communication fails
   - Log the API endpoint, model, and error details
   - Return user message: "Failed to communicate with LLM server. Please check your connection."

3. **ExtractionError**: Raised when event data cannot be extracted
   - Log the LLM response and missing fields
   - Return user message: "Could not extract event information. Please ensure your text includes event name and date."

4. **ValidationError**: Raised when data validation fails
   - Log the validation failure details
   - Return user message with specific validation issue

All errors are caught at the API/UI layer and converted to appropriate responses:
- **UI**: Display error message in red text below the input area
- **API**: Return JSON with `{"error": "message", "details": "specifics"}` and appropriate HTTP status code

## Testing Strategy

The system will be tested using a dual approach combining unit tests and property-based tests:

### Unit Tests

Unit tests will verify specific examples, edge cases, and integration points:

- **Document Parser**: Test parsing of sample PDF, DOCX, and TXT files
- **LLM Extractor**: Test with mocked LLM responses (success and failure cases)
- **CalDAV Generator**: Test ICS generation with specific EventData examples
- **API Endpoints**: Test request/response handling with example inputs
- **Configuration**: Test loading of default and custom configurations
- **Error Handling**: Test specific error scenarios (corrupted files, network failures, invalid dates)

### Property-Based Tests

Property-based tests will verify universal properties across randomized inputs using the **Hypothesis** library for Python. Each test will run a minimum of 100 iterations to ensure comprehensive coverage.

**Test Configuration**:
- Library: Hypothesis (Python property-based testing framework)
- Minimum iterations: 100 per property test
- Each test tagged with: `# Feature: calendar-event-converter, Property N: [property text]`

**Property Test Coverage**:

1. **Property 1 (Text Extraction)**: Generate random valid documents, verify non-empty extraction
2. **Property 2 (Plain Text)**: Generate random text strings, verify identity
3. **Property 3 (Error Handling)**: Generate random corrupted files, verify ParsingError raised
4. **Property 5 (Extraction)**: Generate random valid LLM responses, verify EventData creation
5. **Property 6 (Missing Fields)**: Generate random incomplete LLM responses, verify ExtractionError
6. **Property 7 (Datetime)**: Generate random datetime strings (valid and invalid), verify parsing
7. **Property 8 (Round-Trip)**: Generate random EventData, verify ICS round-trip preserves data
8. **Property 9 (Preservation)**: Generate random EventData, verify all fields present in ICS
9. **Property 10 (UID Uniqueness)**: Generate multiple ICS files, verify unique UIDs
10. **Property 11 (API Success)**: Generate random successful conversions, verify response format
11. **Property 12 (Error Handling)**: Generate random error conditions, verify appropriate error responses
12. **Property 13 (Config Override)**: Generate random configurations, verify they're used
13. **Property 14 (API Errors)**: Generate random failure conditions, verify error response format

**Hypothesis Strategies**:
- Use `st.text()` for generating random text inputs
- Use `st.datetimes()` for generating random datetime values
- Use `st.builds()` to generate random EventData objects
- Use custom strategies for generating valid/invalid document content
- Use `st.sampled_from()` for file types and error conditions

### Integration Testing

Integration tests will verify the complete pipeline:
- End-to-end conversion from document upload to ICS download
- API request/response cycle with real FastAPI test client
- Docker container startup and health checks
- LLM communication with mock server

### Testing in Docker

All tests will run inside the Docker container to ensure consistency:
```bash
docker build -t calendar-converter .
docker run calendar-converter pytest tests/ -v
```

This ensures tests run in the same environment as production, catching any environment-specific issues.
