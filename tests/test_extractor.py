"""Tests for LLM extractor."""

import json
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.config import LLMConfig
from src.exceptions import ExtractionError, LLMError
from src.extractor import LLMExtractor
from src.models import EventData


# Feature: calendar-event-converter, Property 4: LLM Request Formation
@settings(max_examples=100, deadline=None)
@given(text=st.text(min_size=1, max_size=1000))
def test_property_llm_request_formation(text):
    """
    Property 4: LLM Request Formation
    
    For any parsed text content, the system should construct a valid OpenAI API 
    request with proper headers, authentication, and prompt structure.
    
    Validates: Requirements 2.1, 2.2
    """
    config = LLMConfig(
        api_base="http://test.example.com/v1",
        model="test-model",
        api_key="test-key",
        timeout=30
    )
    
    extractor = LLMExtractor(config)
    
    # Mock the OpenAI client to capture the request
    with patch.object(extractor.client.chat.completions, 'create') as mock_create:
        # Set up mock to return a valid response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "event_name": "Test Event",
            "start_datetime": "2025-01-10T14:00:00"
        })
        mock_create.return_value = mock_response
        
        try:
            extractor.extract_event_data(text)
        except (ExtractionError, LLMError):
            # Extraction might fail for random text, but we're testing request formation
            pass
        
        # Verify that the API was called
        assert mock_create.called, "LLM API should be called"
        
        # Verify the request structure
        call_args = mock_create.call_args
        assert call_args is not None
        
        # Check that model is specified
        assert 'model' in call_args.kwargs
        assert call_args.kwargs['model'] == config.model
        
        # Check that messages are properly structured
        assert 'messages' in call_args.kwargs
        messages = call_args.kwargs['messages']
        assert isinstance(messages, list)
        assert len(messages) >= 2  # At least system and user messages
        
        # Verify system message exists
        system_messages = [m for m in messages if m.get('role') == 'system']
        assert len(system_messages) > 0, "Should have system message"
        
        # Verify user message exists and contains the input text
        user_messages = [m for m in messages if m.get('role') == 'user']
        assert len(user_messages) > 0, "Should have user message"
        assert text in user_messages[0]['content'], "User message should contain input text"


# Feature: calendar-event-converter, Property 5: Event Data Extraction Completeness
@settings(max_examples=100, deadline=None)
@given(
    event_name=st.text(min_size=1, max_size=100).filter(lambda s: s.strip()),
    start_dt=st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31)
    )
)
def test_property_event_data_extraction_completeness(event_name, start_dt):
    """
    Property 5: Event Data Extraction Completeness
    
    For any LLM response containing valid event information, the extractor should 
    successfully parse and return an EventData object with at least event_name 
    and start_datetime populated.
    
    Validates: Requirements 2.3
    """
    config = LLMConfig(
        api_base="http://test.example.com/v1",
        model="test-model",
        api_key="test-key"
    )
    
    extractor = LLMExtractor(config)
    
    # Create a valid LLM response
    llm_response = {
        "event_name": event_name,
        "start_datetime": start_dt.strftime("%Y-%m-%dT%H:%M:%S")
    }
    
    # Mock the OpenAI client
    with patch.object(extractor.client.chat.completions, 'create') as mock_create:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(llm_response)
        mock_create.return_value = mock_response
        
        # Extract event data
        result = extractor.extract_event_data("Some text")
        
        # Verify EventData object is created with required fields
        assert isinstance(result, EventData)
        assert result.event_name == event_name
        assert result.start_datetime is not None
        # Allow some tolerance for datetime comparison (seconds precision)
        assert abs((result.start_datetime - start_dt).total_seconds()) < 1


# Feature: calendar-event-converter, Property 6: Missing Field Detection
@settings(max_examples=100, deadline=None)
@given(
    missing_field=st.sampled_from(["event_name", "start_datetime"]),
    event_name=st.text(min_size=1, max_size=100),
    start_dt=st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31)
    )
)
def test_property_missing_field_detection(missing_field, event_name, start_dt):
    """
    Property 6: Missing Field Detection
    
    For any LLM response missing required event fields (event_name or start_datetime), 
    the system should raise an ExtractionError specifying which fields are missing.
    
    Validates: Requirements 2.4
    """
    config = LLMConfig(
        api_base="http://test.example.com/v1",
        model="test-model",
        api_key="test-key"
    )
    
    extractor = LLMExtractor(config)
    
    # Create an incomplete LLM response (missing one required field)
    llm_response = {
        "event_name": event_name,
        "start_datetime": start_dt.strftime("%Y-%m-%dT%H:%M:%S")
    }
    # Remove the field that should be missing
    del llm_response[missing_field]
    
    # Mock the OpenAI client
    with patch.object(extractor.client.chat.completions, 'create') as mock_create:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(llm_response)
        mock_create.return_value = mock_response
        
        # Verify that ExtractionError is raised
        with pytest.raises(ExtractionError) as exc_info:
            extractor.extract_event_data("Some text")
        
        # Verify the error message mentions the missing field
        assert missing_field in str(exc_info.value).lower()


# Unit tests

def test_extract_event_data_success():
    """Test successful event extraction with complete data."""
    config = LLMConfig(
        api_base="http://test.example.com/v1",
        model="test-model",
        api_key="test-key"
    )
    
    extractor = LLMExtractor(config)
    
    llm_response = {
        "event_name": "Team Meeting",
        "start_datetime": "2025-01-15T14:00:00",
        "end_datetime": "2025-01-15T15:00:00",
        "location": "Conference Room A",
        "description": "Quarterly planning meeting"
    }
    
    with patch.object(extractor.client.chat.completions, 'create') as mock_create:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(llm_response)
        mock_create.return_value = mock_response
        
        result = extractor.extract_event_data("Team meeting tomorrow at 2pm")
        
        assert result.event_name == "Team Meeting"
        assert result.start_datetime == datetime(2025, 1, 15, 14, 0, 0)
        assert result.end_datetime == datetime(2025, 1, 15, 15, 0, 0)
        assert result.location == "Conference Room A"
        assert result.description == "Quarterly planning meeting"


def test_extract_event_data_minimal():
    """Test successful event extraction with only required fields."""
    config = LLMConfig(
        api_base="http://test.example.com/v1",
        model="test-model",
        api_key="test-key"
    )
    
    extractor = LLMExtractor(config)
    
    llm_response = {
        "event_name": "Quick Sync",
        "start_datetime": "2025-01-20T10:00:00"
    }
    
    with patch.object(extractor.client.chat.completions, 'create') as mock_create:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(llm_response)
        mock_create.return_value = mock_response
        
        result = extractor.extract_event_data("Quick sync next week")
        
        assert result.event_name == "Quick Sync"
        assert result.start_datetime == datetime(2025, 1, 20, 10, 0, 0)
        assert result.end_datetime is None
        assert result.location is None
        assert result.description is None


def test_extract_event_data_llm_error():
    """Test LLM communication failure."""
    config = LLMConfig(
        api_base="http://test.example.com/v1",
        model="test-model",
        api_key="test-key"
    )
    
    extractor = LLMExtractor(config)
    
    with patch.object(extractor.client.chat.completions, 'create') as mock_create:
        mock_create.side_effect = Exception("Connection timeout")
        
        with pytest.raises(LLMError) as exc_info:
            extractor.extract_event_data("Some text")
        
        assert "Failed to communicate with LLM" in str(exc_info.value)


def test_extract_event_data_invalid_json():
    """Test handling of invalid JSON response from LLM."""
    config = LLMConfig(
        api_base="http://test.example.com/v1",
        model="test-model",
        api_key="test-key"
    )
    
    extractor = LLMExtractor(config)
    
    with patch.object(extractor.client.chat.completions, 'create') as mock_create:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is not valid JSON"
        mock_create.return_value = mock_response
        
        with pytest.raises(ExtractionError) as exc_info:
            extractor.extract_event_data("Some text")
        
        assert "Failed to parse LLM response as JSON" in str(exc_info.value)


def test_extract_event_data_empty_response():
    """Test handling of empty response from LLM."""
    config = LLMConfig(
        api_base="http://test.example.com/v1",
        model="test-model",
        api_key="test-key"
    )
    
    extractor = LLMExtractor(config)
    
    with patch.object(extractor.client.chat.completions, 'create') as mock_create:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = None
        mock_create.return_value = mock_response
        
        with pytest.raises(ExtractionError) as exc_info:
            extractor.extract_event_data("Some text")
        
        assert "empty response" in str(exc_info.value).lower()


def test_extract_event_data_invalid_datetime():
    """Test handling of invalid datetime format."""
    config = LLMConfig(
        api_base="http://test.example.com/v1",
        model="test-model",
        api_key="test-key"
    )
    
    extractor = LLMExtractor(config)
    
    llm_response = {
        "event_name": "Test Event",
        "start_datetime": "not-a-valid-datetime"
    }
    
    with patch.object(extractor.client.chat.completions, 'create') as mock_create:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(llm_response)
        mock_create.return_value = mock_response
        
        with pytest.raises(ExtractionError) as exc_info:
            extractor.extract_event_data("Some text")
        
        assert "Invalid start_datetime format" in str(exc_info.value)
