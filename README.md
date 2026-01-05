# Calendar Event Converter

Transform unstructured text and documents into CalDAV-compatible calendar events using LLM-powered extraction.

## Overview

The Calendar Event Converter is a containerized Python application that intelligently extracts event information from unstructured text or documents and generates properly formatted CalDAV (.ics) calendar files. Using Large Language Model (LLM) technology, the system can understand natural language descriptions of events and automatically structure them into calendar-compatible formats.

## Features

- **Multi-Format Document Parsing**: Extract text from PDF, DOCX, and TXT files
- **Intelligent Event Extraction**: Use LLM to identify event details (name, date/time, location, description)
- **CalDAV-Compatible Output**: Generate standard .ics files that work with any calendar application
- **Dual Interface**: Web UI with drag-and-drop file upload and RESTful API for programmatic access
- **Containerized Deployment**: Runs entirely in Docker containers for isolation and reproducibility
- **Flexible LLM Integration**: Compatible with any OpenAI API-compatible LLM server (LM Studio, OpenAI, etc.)
- **Comprehensive Error Handling**: Clear error messages for parsing, extraction, and validation failures

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- LM Studio running locally (or another OpenAI-compatible LLM server)
  - Default configuration expects LM Studio at `http://host.docker.internal:1234/v1`
  - Default model: `ibm/granite-4-h-tiny`

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd calendar-event-converter
```

2. (Optional) Configure LLM settings in `config/config.yaml`:
```yaml
llm:
  api_base: "http://host.docker.internal:1234/v1"
  model: "ibm/granite-4-h-tiny"
  api_key: "not-needed"
  timeout: 30
```

3. Build and run with Docker Compose:
```bash
docker-compose up --build
```

4. Access the web UI at http://localhost:8000

The application will be ready to accept requests immediately after startup.

## Configuration

The application is configured via `config/config.yaml`. All settings have sensible defaults.

### Configuration Options

```yaml
# LLM Server Configuration
llm:
  api_base: "http://host.docker.internal:1234/v1"  # LLM API endpoint
  model: "ibm/granite-4-h-tiny"                     # Model name
  api_key: "not-needed"                             # API key (not needed for LM Studio)
  timeout: 30                                        # Request timeout in seconds

# Server Configuration
server:
  host: "0.0.0.0"                                   # Server bind address
  port: 8000                                        # Server port

# Input Limits
limits:
  max_file_size_mb: 10                              # Maximum file upload size
  max_text_length: 50000                            # Maximum text input length
```

### Using Different LLM Providers

**LM Studio (Default)**:
```yaml
llm:
  api_base: "http://host.docker.internal:1234/v1"
  model: "ibm/granite-4-h-tiny"
  api_key: "not-needed"
```

**OpenAI**:
```yaml
llm:
  api_base: "https://api.openai.com/v1"
  model: "gpt-4"
  api_key: "your-openai-api-key"
```

**Other OpenAI-Compatible Servers**:
```yaml
llm:
  api_base: "http://your-server:port/v1"
  model: "your-model-name"
  api_key: "your-api-key-if-needed"
```

## Usage

### Web UI

1. Navigate to http://localhost:8000
2. Choose one of two input methods:
   - **Drag and drop** a document file (PDF, DOCX, or TXT)
   - **Paste text** directly into the text input field
3. Click "Convert to Calendar Event"
4. Download the generated .ics file
5. Import into your calendar application (Google Calendar, Apple Calendar, Outlook, etc.)

### API Endpoints

The application provides two REST API endpoints for programmatic access.

#### POST /api/v1/convert/document

Convert a document file to a calendar event.

**Request**:
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: File upload with field name `file`

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/convert/document \
  -F "file=@meeting-notes.pdf" \
  -o event.ics
```

**Success Response** (200 OK):
```json
{
  "ics_content": "BEGIN:VCALENDAR\nVERSION:2.0\n...",
  "filename": "event_20250105_140000.ics"
}
```

**Error Response** (4xx/5xx):
```json
{
  "error": "Failed to parse document",
  "details": "Unsupported file format"
}
```

#### POST /api/v1/convert/text

Convert plain text to a calendar event.

**Request**:
- Method: `POST`
- Content-Type: `application/json`
- Body: JSON object with `text` field

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/convert/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Team meeting tomorrow at 2pm in Conference Room A. We will discuss Q1 planning and budget allocation."
  }' \
  -o event.ics
```

**Success Response** (200 OK):
```json
{
  "ics_content": "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Calendar Event Converter//EN\nBEGIN:VEVENT\nUID:...\nDTSTAMP:...\nDTSTART:20250106T140000\nDTEND:20250106T150000\nSUMMARY:Team meeting\nLOCATION:Conference Room A\nDESCRIPTION:We will discuss Q1 planning and budget allocation.\nEND:VEVENT\nEND:VCALENDAR",
  "filename": "event_20250106_140000.ics"
}
```

**Error Response** (4xx/5xx):
```json
{
  "error": "Could not extract event information",
  "details": "No valid datetime found in input"
}
```

### Usage Examples

#### Example 1: Convert Meeting Notes

Input text:
```
Project kickoff meeting scheduled for January 15, 2025 at 10:00 AM in Building 3, Room 201.
Attendees should bring their laptops. We'll review the project timeline and assign initial tasks.
```

Generated event:
- Name: Project kickoff meeting
- Date/Time: January 15, 2025, 10:00 AM - 11:00 AM
- Location: Building 3, Room 201
- Description: Attendees should bring their laptops. We'll review the project timeline and assign initial tasks.

#### Example 2: Convert Email Content

Input text:
```
Hi team,

Just a reminder about our quarterly review on March 3rd at 2:30 PM.
We'll meet in the main conference room on the 5th floor.
Please prepare your department updates and bring any questions about the new policies.

Thanks!
```

Generated event:
- Name: Quarterly review
- Date/Time: March 3, 2025, 2:30 PM - 3:30 PM
- Location: Main conference room, 5th floor
- Description: Please prepare your department updates and bring any questions about the new policies.

#### Example 3: Convert Document

Upload a PDF containing:
```
WORKSHOP ANNOUNCEMENT

Python for Data Science Workshop
Date: February 20, 2025
Time: 9:00 AM - 4:00 PM
Venue: Tech Hub, Downtown Campus
```

Generated event:
- Name: Python for Data Science Workshop
- Date/Time: February 20, 2025, 9:00 AM - 4:00 PM
- Location: Tech Hub, Downtown Campus

## Development

### Project Structure

```
calendar-event-converter/
├── src/                          # Application source code
│   ├── __init__.py
│   ├── main.py                   # Application entry point
│   ├── api.py                    # FastAPI routes and endpoints
│   ├── service.py                # Event conversion service
│   ├── parser.py                 # Document parser
│   ├── extractor.py              # LLM extractor
│   ├── generator.py              # CalDAV generator
│   ├── models.py                 # Data models
│   ├── config.py                 # Configuration management
│   ├── exceptions.py             # Custom exceptions
│   └── static/
│       └── index.html            # Web UI
├── tests/                        # Test suite
│   ├── test_parser.py            # Parser tests
│   ├── test_extractor.py         # Extractor tests
│   ├── test_generator.py         # Generator tests
│   ├── test_service.py           # Service tests
│   ├── test_api.py               # API tests
│   ├── test_models.py            # Model tests
│   └── test_config.py            # Configuration tests
├── config/
│   └── config.yaml               # Configuration file
├── Dockerfile                    # Container definition
├── docker-compose.yml            # Container orchestration
├── pyproject.toml                # Python project configuration
└── README.md                     # This file
```

### Running Tests

Run the complete test suite:
```bash
docker build -t calendar-event-converter .
docker run calendar-event-converter pytest tests/ -v
```

Run specific test files:
```bash
docker run calendar-event-converter pytest tests/test_parser.py -v
```

Run with coverage:
```bash
docker run calendar-event-converter pytest tests/ --cov=src --cov-report=html
```

### Testing Strategy

The project uses a dual testing approach:

1. **Unit Tests**: Verify specific examples, edge cases, and integration points
2. **Property-Based Tests**: Use Hypothesis library to verify universal properties across randomized inputs (minimum 100 iterations per property)

### Building Without Docker

If you prefer to run locally without Docker:

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -e .

# Run the application
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## Error Handling

The application provides clear error messages for common issues:

| Error Type | Cause | User Message |
|------------|-------|--------------|
| ParsingError | Document parsing failed | "Failed to parse document. Please ensure the file is not corrupted." |
| LLMError | LLM communication failed | "Failed to communicate with LLM server. Please check your connection." |
| ExtractionError | Event data cannot be extracted | "Could not extract event information. Please ensure your text includes event name and date." |
| ValidationError | Data validation failed | Specific validation issue (e.g., "End datetime must be after start datetime") |

## Troubleshooting

### LLM Connection Issues

If you see "Failed to communicate with LLM server":

1. Ensure LM Studio (or your LLM server) is running
2. Verify the API endpoint in `config/config.yaml`
3. Check that the model is loaded in LM Studio
4. Test the connection: `curl http://localhost:1234/v1/models`

### Document Parsing Issues

If document parsing fails:

1. Ensure the file is not corrupted
2. Verify the file format is supported (PDF, DOCX, TXT)
3. Check file size is under the configured limit (default 10MB)
4. Try converting the document to plain text first

### Event Extraction Issues

If event extraction fails:

1. Ensure your text includes clear date/time information
2. Include an event name or title
3. Use standard date formats (e.g., "January 15, 2025" or "2025-01-15")
4. Be explicit about times (e.g., "2:00 PM" or "14:00")

## Architecture

The system follows a layered architecture:

```
┌─────────────────────────────────────────┐
│     Interface Layer (FastAPI)           │
│  ┌──────────────┐  ┌─────────────────┐ │
│  │   Web UI     │  │   REST API      │ │
│  └──────────────┘  └─────────────────┘ │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│     Service Layer                        │
│  ┌─────────────────────────────────────┐│
│  │  Event Conversion Service           ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│     Processing Layer                     │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ │
│  │ Parser   │ │Extractor │ │Generator│ │
│  └──────────┘ └──────────┘ └─────────┘ │
└─────────────────────────────────────────┘
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or contributions, please open an issue on the project repository.
