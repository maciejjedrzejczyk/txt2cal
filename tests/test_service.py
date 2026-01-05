"""Tests for EventConversionService."""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime
from unittest.mock import Mock, MagicMock

from src.service import EventConversionService
from src.parser import DocumentParser
from src.extractor import LLMExtractor
from src.generator import CalDAVGenerator
from src.models import EventData
from src.exceptions import (
    ParsingError,
    LLMError,
    ExtractionError,
    ValidationError
)


# Feature: calendar-event-converter, Property 2: Plain Text Identity
@settings(max_examples=100)
@given(st.text(min_size=10, max_size=1000))
def test_plain_text_identity(text):
    """
    Property 2: Plain Text Identity
    
    For any plain text input, the system should accept and process it without 
    modification, treating it as already-parsed content.
    
    Validates: Requirements 1.2
    """
    # Create mock dependencies
    parser = Mock(spec=DocumentParser)
    extractor = Mock(spec=LLMExtractor)
    generator = Mock(spec=CalDAVGenerator)
    
    # Create a valid EventData for the extractor to return
    mock_event_data = EventData(
        event_name="Test Event",
        start_datetime=datetime(2025, 1, 10, 14, 0, 0),
        location="Test Location",
        description="Test Description"
    )
    extractor.extract_event_data.return_value = mock_event_data
    
    # Mock ICS generation
    mock_ics = "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"
    generator.generate_ics.return_value = mock_ics
    
    # Create service
    service = EventConversionService(parser, extractor, generator)
    
    # Convert text - should NOT call parser
    result = service.convert_text(text)
    
    # Verify parser was NOT called (text is treated as already-parsed)
    parser.parse.assert_not_called()
    
    # Verify extractor was called with the original text (no modification)
    extractor.extract_event_data.assert_called_once_with(text)
    
    # Verify generator was called
    generator.generate_ics.assert_called_once_with(mock_event_data)
    
    # Verify result is the ICS content
    assert result == mock_ics


# Feature: calendar-event-converter, Property 12: Comprehensive Error Handling
@settings(max_examples=100)
@given(
    error_type=st.sampled_from([
        'parsing',
        'llm',
        'extraction',
        'validation'
    ]),
    error_message=st.text(min_size=5, max_size=100)
)
def test_comprehensive_error_handling(error_type, error_message):
    """
    Property 12: Comprehensive Error Handling
    
    For any error occurring during the conversion pipeline (parsing, LLM 
    communication, extraction, or ICS generation), the system should return 
    an appropriate error response with a user-friendly message and log the 
    detailed error for debugging.
    
    Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5
    """
    # Create mock dependencies
    parser = Mock(spec=DocumentParser)
    extractor = Mock(spec=LLMExtractor)
    generator = Mock(spec=CalDAVGenerator)
    
    # Create service
    service = EventConversionService(parser, extractor, generator)
    
    # Configure mocks to raise appropriate errors based on error_type
    if error_type == 'parsing':
        parser.parse.side_effect = ParsingError(error_message)
        
        # Test document conversion with parsing error
        with pytest.raises(ParsingError) as exc_info:
            service.convert_document(b"test content", "pdf")
        
        # Verify the error message is preserved
        assert error_message in str(exc_info.value)
        
    elif error_type == 'llm':
        extractor.extract_event_data.side_effect = LLMError(error_message)
        
        # Test text conversion with LLM error
        with pytest.raises(LLMError) as exc_info:
            service.convert_text("test text")
        
        # Verify the error message is preserved
        assert error_message in str(exc_info.value)
        
    elif error_type == 'extraction':
        extractor.extract_event_data.side_effect = ExtractionError(error_message)
        
        # Test text conversion with extraction error
        with pytest.raises(ExtractionError) as exc_info:
            service.convert_text("test text")
        
        # Verify the error message is preserved
        assert error_message in str(exc_info.value)
        
    elif error_type == 'validation':
        # Mock successful extraction
        mock_event_data = EventData(
            event_name="Test Event",
            start_datetime=datetime(2025, 1, 10, 14, 0, 0)
        )
        extractor.extract_event_data.return_value = mock_event_data
        
        # Mock validation error during ICS generation
        generator.generate_ics.side_effect = ValidationError(error_message)
        
        # Test text conversion with validation error
        with pytest.raises(ValidationError) as exc_info:
            service.convert_text("test text")
        
        # Verify the error message is preserved
        assert error_message in str(exc_info.value)



# Integration Tests

def test_end_to_end_document_conversion():
    """
    Integration test for end-to-end document conversion.
    
    Tests the complete pipeline: parse → extract → generate
    
    Validates: Requirements 1.1, 2.1, 3.1
    """
    # Create real dependencies (with mocked LLM)
    parser = DocumentParser()
    
    # Mock LLM extractor
    extractor = Mock(spec=LLMExtractor)
    mock_event_data = EventData(
        event_name="Team Meeting",
        start_datetime=datetime(2025, 1, 15, 14, 0, 0),
        end_datetime=datetime(2025, 1, 15, 15, 0, 0),
        location="Conference Room A",
        description="Quarterly planning meeting"
    )
    extractor.extract_event_data.return_value = mock_event_data
    
    # Real generator
    generator = CalDAVGenerator()
    
    # Create service
    service = EventConversionService(parser, extractor, generator)
    
    # Create a simple text document
    document_content = b"Team Meeting on January 15, 2025 at 2pm in Conference Room A"
    
    # Convert document
    ics_content = service.convert_document(document_content, "txt")
    
    # Verify ICS content is generated
    assert ics_content is not None
    assert "BEGIN:VCALENDAR" in ics_content
    assert "VERSION:2.0" in ics_content
    assert "BEGIN:VEVENT" in ics_content
    assert "SUMMARY:Team Meeting" in ics_content
    assert "LOCATION:Conference Room A" in ics_content
    assert "END:VEVENT" in ics_content
    assert "END:VCALENDAR" in ics_content
    
    # Verify extractor was called with parsed text
    extractor.extract_event_data.assert_called_once()
    call_args = extractor.extract_event_data.call_args[0][0]
    assert "Team Meeting" in call_args


def test_end_to_end_text_conversion():
    """
    Integration test for end-to-end text conversion.
    
    Tests the pipeline: extract → generate (no parsing)
    
    Validates: Requirements 1.2, 2.1, 3.1
    """
    # Mock LLM extractor
    extractor = Mock(spec=LLMExtractor)
    mock_event_data = EventData(
        event_name="Workshop",
        start_datetime=datetime(2025, 2, 1, 10, 0, 0),
        location="Online",
        description="Python workshop"
    )
    extractor.extract_event_data.return_value = mock_event_data
    
    # Real generator
    generator = CalDAVGenerator()
    
    # Parser should not be used
    parser = Mock(spec=DocumentParser)
    
    # Create service
    service = EventConversionService(parser, extractor, generator)
    
    # Plain text input
    text = "Python workshop on February 1, 2025 at 10am online"
    
    # Convert text
    ics_content = service.convert_text(text)
    
    # Verify parser was NOT called
    parser.parse.assert_not_called()
    
    # Verify ICS content is generated
    assert ics_content is not None
    assert "BEGIN:VCALENDAR" in ics_content
    assert "SUMMARY:Workshop" in ics_content
    assert "LOCATION:Online" in ics_content
    
    # Verify extractor was called with original text
    extractor.extract_event_data.assert_called_once_with(text)


def test_error_propagation_through_pipeline():
    """
    Integration test for error propagation through the pipeline.
    
    Tests that errors at each stage are properly propagated.
    
    Validates: Requirements 1.1, 2.1, 3.1
    """
    # Test parsing error propagation
    parser = DocumentParser()
    extractor = Mock(spec=LLMExtractor)
    generator = Mock(spec=CalDAVGenerator)
    
    service = EventConversionService(parser, extractor, generator)
    
    # Invalid document should raise ParsingError
    with pytest.raises(ParsingError):
        service.convert_document(b"", "unsupported_format")
    
    # Test extraction error propagation
    parser = Mock(spec=DocumentParser)
    parser.parse.return_value = "Some text"
    extractor = Mock(spec=LLMExtractor)
    extractor.extract_event_data.side_effect = ExtractionError("Missing event name")
    generator = Mock(spec=CalDAVGenerator)
    
    service = EventConversionService(parser, extractor, generator)
    
    with pytest.raises(ExtractionError) as exc_info:
        service.convert_document(b"test", "txt")
    assert "Missing event name" in str(exc_info.value)
    
    # Test validation error propagation
    parser = Mock(spec=DocumentParser)
    parser.parse.return_value = "Some text"
    extractor = Mock(spec=LLMExtractor)
    mock_event_data = EventData(
        event_name="Test",
        start_datetime=datetime(2025, 1, 10, 14, 0, 0)
    )
    extractor.extract_event_data.return_value = mock_event_data
    generator = Mock(spec=CalDAVGenerator)
    generator.generate_ics.side_effect = ValidationError("Invalid ICS")
    
    service = EventConversionService(parser, extractor, generator)
    
    with pytest.raises(ValidationError) as exc_info:
        service.convert_document(b"test", "txt")
    assert "Invalid ICS" in str(exc_info.value)
