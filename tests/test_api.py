"""Tests for REST API endpoints."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from io import BytesIO

from fastapi.testclient import TestClient
from hypothesis import given, strategies as st, settings

from src.api import create_app
from src.service import EventConversionService
from src.models import EventData
from src.exceptions import (
    ParsingError,
    LLMError,
    ExtractionError,
    ValidationError
)


# Test fixtures
@pytest.fixture
def mock_service():
    """Create a mock EventConversionService."""
    return Mock(spec=EventConversionService)


@pytest.fixture
def test_client(mock_service):
    """Create a test client with mock service."""
    app = create_app(
        service=mock_service,
        max_file_size_bytes=10 * 1024 * 1024,  # 10 MB
        max_text_length=50000
    )
    return TestClient(app)


# Hypothesis strategies for generating test data
@st.composite
def valid_ics_content(draw):
    """Generate valid ICS content."""
    event_name = draw(st.text(min_size=1, max_size=100))
    start_dt = draw(st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31)
    ))
    
    # Simple ICS format
    ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Calendar Event Converter//EN
BEGIN:VEVENT
UID:test-uid-123
DTSTAMP:{start_dt.strftime('%Y%m%dT%H%M%S')}
DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}
DTEND:{(start_dt + timedelta(hours=1)).strftime('%Y%m%dT%H%M%S')}
SUMMARY:{event_name}
END:VEVENT
END:VCALENDAR"""
    return ics


# Property-Based Tests

@settings(max_examples=100)
@given(ics_content=valid_ics_content())
def test_property_api_success_response_format_document(ics_content):
    """
    Property 11: API Success Response Format
    
    For any successful conversion via the API, the response should include 
    valid ICS content and appropriate HTTP headers (Content-Type: application/json,
    and response body with ics_content and filename fields).
    
    Feature: calendar-event-converter, Property 11: API Success Response Format
    Validates: Requirements 5.3
    """
    # Create mock service for this test
    mock_service = Mock(spec=EventConversionService)
    mock_service.convert_document.return_value = ics_content
    
    # Create test client
    app = create_app(
        service=mock_service,
        max_file_size_bytes=10 * 1024 * 1024,
        max_text_length=50000
    )
    client = TestClient(app)
    
    # Create a test file
    file_content = b"Test document content"
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
    
    # Make request
    response = client.post("/api/v1/convert/document", files=files)
    
    # Verify response format
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    
    # Verify response body structure
    response_data = response.json()
    assert "ics_content" in response_data
    assert "filename" in response_data
    
    # Verify ICS content is present
    assert response_data["ics_content"] == ics_content
    
    # Verify filename format (should be event_YYYYMMDD_HHMMSS.ics)
    filename = response_data["filename"]
    assert filename.startswith("event_")
    assert filename.endswith(".ics")
    assert len(filename) == len("event_20250105_123456.ics")


@settings(max_examples=100)
@given(
    ics_content=valid_ics_content(),
    text=st.text(min_size=10, max_size=1000)
)
def test_property_api_success_response_format_text(ics_content, text):
    """
    Property 11: API Success Response Format (Text endpoint)
    
    For any successful text conversion via the API, the response should include 
    valid ICS content and appropriate response structure.
    
    Feature: calendar-event-converter, Property 11: API Success Response Format
    Validates: Requirements 5.3
    """
    # Create mock service for this test
    mock_service = Mock(spec=EventConversionService)
    mock_service.convert_text.return_value = ics_content
    
    # Create test client
    app = create_app(
        service=mock_service,
        max_file_size_bytes=10 * 1024 * 1024,
        max_text_length=50000
    )
    client = TestClient(app)
    
    # Make request
    response = client.post("/api/v1/convert/text", json={"text": text})
    
    # Verify response format
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    
    # Verify response body structure
    response_data = response.json()
    assert "ics_content" in response_data
    assert "filename" in response_data
    
    # Verify ICS content is present
    assert response_data["ics_content"] == ics_content
    
    # Verify filename format
    filename = response_data["filename"]
    assert filename.startswith("event_")
    assert filename.endswith(".ics")


@settings(max_examples=100)
@given(
    error_type=st.sampled_from([
        ParsingError,
        LLMError,
        ExtractionError,
        ValidationError
    ]),
    error_message=st.text(min_size=1, max_size=200)
)
def test_property_api_error_response_format_document(error_type, error_message):
    """
    Property 14: API Error Response Format
    
    For any failed conversion via the API, the response should include an 
    appropriate HTTP error status code (4xx or 5xx) and a JSON body with 
    error details.
    
    Feature: calendar-event-converter, Property 14: API Error Response Format
    Validates: Requirements 5.4
    """
    # Create mock service that raises the error
    mock_service = Mock(spec=EventConversionService)
    mock_service.convert_document.side_effect = error_type(error_message)
    
    # Create test client
    app = create_app(
        service=mock_service,
        max_file_size_bytes=10 * 1024 * 1024,
        max_text_length=50000
    )
    client = TestClient(app)
    
    # Create a test file
    file_content = b"Test document content"
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
    
    # Make request
    response = client.post("/api/v1/convert/document", files=files)
    
    # Verify error response format
    # Should be 4xx or 5xx status code
    assert response.status_code >= 400
    assert response.status_code < 600
    
    # Should have JSON content type
    assert "application/json" in response.headers["content-type"]
    
    # Should have error details in response body
    response_data = response.json()
    assert "detail" in response_data
    
    # Detail should contain error and details fields
    detail = response_data["detail"]
    assert isinstance(detail, dict)
    assert "error" in detail
    assert "details" in detail
    
    # Error and details should be non-empty strings
    assert isinstance(detail["error"], str)
    assert len(detail["error"]) > 0
    assert isinstance(detail["details"], str)
    assert len(detail["details"]) > 0
    
    # Verify correct status code based on error type
    if error_type == LLMError:
        assert response.status_code == 500
    else:
        assert response.status_code == 400


@settings(max_examples=100)
@given(
    error_type=st.sampled_from([
        LLMError,
        ExtractionError,
        ValidationError
    ]),
    error_message=st.text(min_size=1, max_size=200),
    text=st.text(min_size=10, max_size=1000)
)
def test_property_api_error_response_format_text(error_type, error_message, text):
    """
    Property 14: API Error Response Format (Text endpoint)
    
    For any failed text conversion via the API, the response should include an 
    appropriate HTTP error status code and JSON body with error details.
    
    Feature: calendar-event-converter, Property 14: API Error Response Format
    Validates: Requirements 5.4
    """
    # Create mock service that raises the error
    mock_service = Mock(spec=EventConversionService)
    mock_service.convert_text.side_effect = error_type(error_message)
    
    # Create test client
    app = create_app(
        service=mock_service,
        max_file_size_bytes=10 * 1024 * 1024,
        max_text_length=50000
    )
    client = TestClient(app)
    
    # Make request
    response = client.post("/api/v1/convert/text", json={"text": text})
    
    # Verify error response format
    assert response.status_code >= 400
    assert response.status_code < 600
    assert "application/json" in response.headers["content-type"]
    
    # Verify error details structure
    response_data = response.json()
    assert "detail" in response_data
    detail = response_data["detail"]
    assert isinstance(detail, dict)
    assert "error" in detail
    assert "details" in detail
    assert isinstance(detail["error"], str)
    assert len(detail["error"]) > 0
    assert isinstance(detail["details"], str)
    assert len(detail["details"]) > 0
    
    # Verify correct status code based on error type
    if error_type == LLMError:
        assert response.status_code == 500
    else:
        assert response.status_code == 400


# Unit Tests

def test_convert_document_success(test_client, mock_service):
    """Test successful document conversion."""
    # Setup mock
    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"
    mock_service.convert_document.return_value = ics_content
    
    # Create test file
    file_content = b"Meeting tomorrow at 2pm"
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
    
    # Make request
    response = test_client.post("/api/v1/convert/document", files=files)
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["ics_content"] == ics_content
    assert "event_" in data["filename"]
    assert data["filename"].endswith(".ics")
    
    # Verify service was called correctly
    mock_service.convert_document.assert_called_once()
    call_args = mock_service.convert_document.call_args
    assert call_args[0][0] == file_content
    assert call_args[0][1] == "txt"


def test_convert_document_pdf(test_client, mock_service):
    """Test document conversion with PDF file."""
    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"
    mock_service.convert_document.return_value = ics_content
    
    file_content = b"PDF content"
    files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}
    
    response = test_client.post("/api/v1/convert/document", files=files)
    
    assert response.status_code == 200
    call_args = mock_service.convert_document.call_args
    assert call_args[0][1] == "pdf"


def test_convert_document_docx(test_client, mock_service):
    """Test document conversion with DOCX file."""
    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"
    mock_service.convert_document.return_value = ics_content
    
    file_content = b"DOCX content"
    files = {"file": ("test.docx", BytesIO(file_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    
    response = test_client.post("/api/v1/convert/document", files=files)
    
    assert response.status_code == 200
    call_args = mock_service.convert_document.call_args
    assert call_args[0][1] == "docx"


def test_convert_text_success(test_client, mock_service):
    """Test successful text conversion."""
    # Setup mock
    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"
    mock_service.convert_text.return_value = ics_content
    
    # Make request
    text = "Team meeting tomorrow at 2pm in Conference Room A"
    response = test_client.post("/api/v1/convert/text", json={"text": text})
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["ics_content"] == ics_content
    assert "event_" in data["filename"]
    assert data["filename"].endswith(".ics")
    
    # Verify service was called correctly
    mock_service.convert_text.assert_called_once_with(text)


def test_convert_document_file_too_large(test_client, mock_service):
    """Test file size validation."""
    # Create file larger than limit (10 MB)
    large_content = b"x" * (11 * 1024 * 1024)
    files = {"file": ("large.txt", BytesIO(large_content), "text/plain")}
    
    response = test_client.post("/api/v1/convert/document", files=files)
    
    assert response.status_code == 413
    data = response.json()
    assert "error" in data["detail"]
    assert "File too large" in data["detail"]["error"]


def test_convert_document_unsupported_type(test_client, mock_service):
    """Test unsupported file type validation."""
    file_content = b"Some content"
    files = {"file": ("test.xyz", BytesIO(file_content), "application/octet-stream")}
    
    response = test_client.post("/api/v1/convert/document", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert "error" in data["detail"]
    assert "Unsupported file type" in data["detail"]["error"]


def test_convert_text_too_long(test_client, mock_service):
    """Test text length validation."""
    # Create text longer than limit (50000 characters)
    long_text = "x" * 50001
    
    response = test_client.post("/api/v1/convert/text", json={"text": long_text})
    
    assert response.status_code == 413
    data = response.json()
    assert "error" in data["detail"]
    assert "Text too long" in data["detail"]["error"]


def test_convert_text_empty(test_client, mock_service):
    """Test empty text validation."""
    response = test_client.post("/api/v1/convert/text", json={"text": "   "})
    
    assert response.status_code == 400
    data = response.json()
    assert "error" in data["detail"]
    assert "Empty text" in data["detail"]["error"]


def test_convert_document_parsing_error(test_client, mock_service):
    """Test error handling for parsing errors."""
    mock_service.convert_document.side_effect = ParsingError("Failed to parse PDF")
    
    file_content = b"Corrupted content"
    files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}
    
    response = test_client.post("/api/v1/convert/document", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert "error" in data["detail"]
    assert "Failed to parse document" in data["detail"]["error"]


def test_convert_document_llm_error(test_client, mock_service):
    """Test error handling for LLM errors."""
    mock_service.convert_document.side_effect = LLMError("Connection timeout")
    
    file_content = b"Meeting content"
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
    
    response = test_client.post("/api/v1/convert/document", files=files)
    
    assert response.status_code == 500
    data = response.json()
    assert "error" in data["detail"]
    assert "Failed to communicate with LLM server" in data["detail"]["error"]


def test_convert_text_extraction_error(test_client, mock_service):
    """Test error handling for extraction errors."""
    mock_service.convert_text.side_effect = ExtractionError("Missing event name")
    
    response = test_client.post("/api/v1/convert/text", json={"text": "Some text"})
    
    assert response.status_code == 400
    data = response.json()
    assert "error" in data["detail"]
    assert "Could not extract event information" in data["detail"]["error"]


def test_convert_text_validation_error(test_client, mock_service):
    """Test error handling for validation errors."""
    mock_service.convert_text.side_effect = ValidationError("Invalid datetime")
    
    response = test_client.post("/api/v1/convert/text", json={"text": "Some text"})
    
    assert response.status_code == 400
    data = response.json()
    assert "error" in data["detail"]
    assert "Validation failed" in data["detail"]["error"]


def test_health_check(test_client):
    """Test health check endpoint."""
    response = test_client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


# UI Endpoint Tests

def test_serve_ui_html_page(test_client):
    """Test that HTML page is served correctly at root endpoint."""
    response = test_client.get("/")
    
    # Should return 200 OK
    assert response.status_code == 200
    
    # Should return HTML content
    assert "text/html" in response.headers["content-type"]
    
    # Should contain expected HTML elements
    html_content = response.text
    assert "Calendar Event Converter" in html_content
    assert "drag-and-drop" in html_content.lower() or "drag" in html_content.lower()
    assert "text" in html_content.lower()


def test_ui_convert_document_returns_downloadable_file(test_client, mock_service):
    """Test UI document conversion endpoint returns downloadable ICS file."""
    # Setup mock
    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"
    mock_service.convert_document.return_value = ics_content
    
    # Create test file
    file_content = b"Meeting tomorrow at 2pm"
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
    
    # Make request to UI endpoint
    response = test_client.post("/convert/document", files=files)
    
    # Verify response
    assert response.status_code == 200
    
    # Should return ICS content directly (not JSON)
    assert response.text == ics_content
    
    # Should have calendar content type
    assert response.headers["content-type"] == "text/calendar; charset=utf-8"
    
    # Should have Content-Disposition header for download
    assert "content-disposition" in response.headers
    disposition = response.headers["content-disposition"]
    assert "attachment" in disposition
    assert "filename=" in disposition
    assert ".ics" in disposition


def test_ui_convert_text_returns_downloadable_file(test_client, mock_service):
    """Test UI text conversion endpoint returns downloadable ICS file."""
    # Setup mock
    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"
    mock_service.convert_text.return_value = ics_content
    
    # Make request to UI endpoint
    text = "Team meeting tomorrow at 2pm in Conference Room A"
    response = test_client.post("/convert/text", json={"text": text})
    
    # Verify response
    assert response.status_code == 200
    
    # Should return ICS content directly (not JSON)
    assert response.text == ics_content
    
    # Should have calendar content type
    assert response.headers["content-type"] == "text/calendar; charset=utf-8"
    
    # Should have Content-Disposition header for download
    assert "content-disposition" in response.headers
    disposition = response.headers["content-disposition"]
    assert "attachment" in disposition
    assert "filename=" in disposition
    assert ".ics" in disposition


def test_ui_convert_document_error_display(test_client, mock_service):
    """Test UI document conversion displays errors properly."""
    # Setup mock to raise error
    mock_service.convert_document.side_effect = ExtractionError("Missing event name")
    
    # Create test file
    file_content = b"Some text without event info"
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
    
    # Make request to UI endpoint
    response = test_client.post("/convert/document", files=files)
    
    # Should return error status
    assert response.status_code == 400
    
    # Should return JSON error response
    assert "application/json" in response.headers["content-type"]
    
    # Should have error details
    data = response.json()
    assert "detail" in data
    assert "error" in data["detail"]
    assert "details" in data["detail"]


def test_ui_convert_text_error_display(test_client, mock_service):
    """Test UI text conversion displays errors properly."""
    # Setup mock to raise error
    mock_service.convert_text.side_effect = LLMError("Connection failed")
    
    # Make request to UI endpoint
    response = test_client.post("/convert/text", json={"text": "Some text"})
    
    # Should return error status
    assert response.status_code == 500
    
    # Should return JSON error response
    assert "application/json" in response.headers["content-type"]
    
    # Should have error details
    data = response.json()
    assert "detail" in data
    assert "error" in data["detail"]
    assert "details" in data["detail"]


def test_ui_convert_document_with_pdf(test_client, mock_service):
    """Test UI document conversion with PDF file."""
    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"
    mock_service.convert_document.return_value = ics_content
    
    file_content = b"PDF content"
    files = {"file": ("meeting.pdf", BytesIO(file_content), "application/pdf")}
    
    response = test_client.post("/convert/document", files=files)
    
    assert response.status_code == 200
    assert response.text == ics_content
    assert "text/calendar" in response.headers["content-type"]


def test_ui_convert_document_with_docx(test_client, mock_service):
    """Test UI document conversion with DOCX file."""
    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"
    mock_service.convert_document.return_value = ics_content
    
    file_content = b"DOCX content"
    files = {"file": ("meeting.docx", BytesIO(file_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    
    response = test_client.post("/convert/document", files=files)
    
    assert response.status_code == 200
    assert response.text == ics_content
    assert "text/calendar" in response.headers["content-type"]

