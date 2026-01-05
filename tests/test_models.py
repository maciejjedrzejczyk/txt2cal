"""Tests for data models."""

import pytest
from datetime import datetime, timedelta
from hypothesis import given, strategies as st

from src.models import EventData
from src.exceptions import ValidationError


class TestEventDataProperties:
    """Property-based tests for EventData model."""
    
    @given(
        event_name=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
        start_dt=st.datetimes(
            min_value=datetime(2000, 1, 1),
            max_value=datetime(2100, 12, 31)
        ),
        end_offset=st.integers(min_value=1, max_value=86400)  # 1 second to 1 day
    )
    def test_datetime_validation_valid_end_after_start(
        self, event_name, start_dt, end_offset
    ):
        """
        Property 7: Datetime Validation (valid case)
        
        For any EventData with end_datetime after start_datetime,
        validation should succeed.
        
        Feature: calendar-event-converter, Property 7: Datetime Validation
        Validates: Requirements 2.5
        """
        end_dt = start_dt + timedelta(seconds=end_offset)
        
        event = EventData(
            event_name=event_name,
            start_datetime=start_dt,
            end_datetime=end_dt
        )
        
        # Should not raise any exception
        event.validate()
    
    @given(
        event_name=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
        start_dt=st.datetimes(
            min_value=datetime(2000, 1, 1),
            max_value=datetime(2100, 12, 31)
        ),
        end_offset=st.integers(min_value=1, max_value=86400)  # 1 second to 1 day
    )
    def test_datetime_validation_invalid_end_before_start(
        self, event_name, start_dt, end_offset
    ):
        """
        Property 7: Datetime Validation (invalid case)
        
        For any EventData with end_datetime before start_datetime,
        validation should raise ValidationError.
        
        Feature: calendar-event-converter, Property 7: Datetime Validation
        Validates: Requirements 2.5
        """
        end_dt = start_dt - timedelta(seconds=end_offset)
        
        event = EventData(
            event_name=event_name,
            start_datetime=start_dt,
            end_datetime=end_dt
        )
        
        # Should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            event.validate()
        
        assert "End datetime must be after start datetime" in str(exc_info.value)
    
    @given(
        event_name=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
        start_dt=st.datetimes(
            min_value=datetime(2000, 1, 1),
            max_value=datetime(2100, 12, 31)
        )
    )
    def test_datetime_validation_no_end_datetime(self, event_name, start_dt):
        """
        Property 7: Datetime Validation (no end datetime)
        
        For any EventData without end_datetime, validation should succeed
        as end_datetime is optional.
        
        Feature: calendar-event-converter, Property 7: Datetime Validation
        Validates: Requirements 2.5
        """
        event = EventData(
            event_name=event_name,
            start_datetime=start_dt
        )
        
        # Should not raise any exception
        event.validate()


class TestEventDataValidation:
    """Unit tests for EventData validation."""
    
    def test_validate_requires_event_name(self):
        """Test that validation requires non-empty event name."""
        # Requirements: 2.3
        event = EventData(
            event_name="",
            start_datetime=datetime(2025, 1, 10, 14, 0)
        )
        
        with pytest.raises(ValidationError) as exc_info:
            event.validate()
        
        assert "Event name is required" in str(exc_info.value)
    
    def test_validate_requires_non_whitespace_event_name(self):
        """Test that validation requires non-whitespace event name."""
        # Requirements: 2.3
        event = EventData(
            event_name="   \n\t  ",
            start_datetime=datetime(2025, 1, 10, 14, 0)
        )
        
        with pytest.raises(ValidationError) as exc_info:
            event.validate()
        
        assert "Event name is required" in str(exc_info.value)
    
    def test_validate_requires_start_datetime(self):
        """Test that validation requires start_datetime."""
        # Requirements: 2.3
        event = EventData(
            event_name="Team Meeting",
            start_datetime=None  # type: ignore
        )
        
        with pytest.raises(ValidationError) as exc_info:
            event.validate()
        
        assert "Start datetime is required" in str(exc_info.value)
    
    def test_validate_end_before_start_raises_error(self):
        """Test that end_datetime before start_datetime raises error."""
        # Requirements: 2.5
        event = EventData(
            event_name="Team Meeting",
            start_datetime=datetime(2025, 1, 10, 14, 0),
            end_datetime=datetime(2025, 1, 10, 13, 0)
        )
        
        with pytest.raises(ValidationError) as exc_info:
            event.validate()
        
        assert "End datetime must be after start datetime" in str(exc_info.value)
    
    def test_validate_end_equal_to_start_raises_error(self):
        """Test that end_datetime equal to start_datetime raises error."""
        # Requirements: 2.5
        dt = datetime(2025, 1, 10, 14, 0)
        event = EventData(
            event_name="Team Meeting",
            start_datetime=dt,
            end_datetime=dt
        )
        
        with pytest.raises(ValidationError) as exc_info:
            event.validate()
        
        assert "End datetime must be after start datetime" in str(exc_info.value)
    
    def test_validate_success_with_valid_data(self):
        """Test that validation succeeds with valid data."""
        # Requirements: 2.3, 2.5
        event = EventData(
            event_name="Team Meeting",
            start_datetime=datetime(2025, 1, 10, 14, 0),
            end_datetime=datetime(2025, 1, 10, 15, 0),
            location="Conference Room A",
            description="Quarterly planning meeting"
        )
        
        # Should not raise any exception
        event.validate()
    
    def test_validate_success_without_optional_fields(self):
        """Test that validation succeeds without optional fields."""
        # Requirements: 2.3
        event = EventData(
            event_name="Team Meeting",
            start_datetime=datetime(2025, 1, 10, 14, 0)
        )
        
        # Should not raise any exception
        event.validate()
    
    def test_event_data_dataclass_fields(self):
        """Test that EventData has correct fields."""
        # Requirements: 2.3
        event = EventData(
            event_name="Test Event",
            start_datetime=datetime(2025, 1, 10, 14, 0),
            end_datetime=datetime(2025, 1, 10, 15, 0),
            location="Test Location",
            description="Test Description"
        )
        
        assert event.event_name == "Test Event"
        assert event.start_datetime == datetime(2025, 1, 10, 14, 0)
        assert event.end_datetime == datetime(2025, 1, 10, 15, 0)
        assert event.location == "Test Location"
        assert event.description == "Test Description"
    
    def test_event_data_optional_fields_default_to_none(self):
        """Test that optional fields default to None."""
        # Requirements: 2.3
        event = EventData(
            event_name="Test Event",
            start_datetime=datetime(2025, 1, 10, 14, 0)
        )
        
        assert event.location is None
        assert event.description is None
        assert event.end_datetime is None
