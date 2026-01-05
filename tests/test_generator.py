"""Tests for CalDAV generator."""

import pytest
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings
from icalendar import Calendar

from src.generator import CalDAVGenerator
from src.models import EventData
from src.exceptions import ValidationError


# Custom strategy for generating valid EventData
@st.composite
def event_data_strategy(draw):
    """Generate random valid EventData objects."""
    event_name = draw(st.text(min_size=1, max_size=200).filter(lambda x: x.strip()))
    # Generate datetimes without microseconds since iCalendar doesn't preserve them
    start_dt = draw(st.datetimes(
        min_value=datetime(2000, 1, 1),
        max_value=datetime(2100, 12, 31)
    )).replace(microsecond=0)
    
    # Optionally add end_datetime (after start)
    has_end = draw(st.booleans())
    if has_end:
        end_offset = draw(st.integers(min_value=1, max_value=86400))
        end_dt = start_dt + timedelta(seconds=end_offset)
    else:
        end_dt = None
    
    # Optionally add location
    has_location = draw(st.booleans())
    location = draw(st.text(min_size=1, max_size=200)) if has_location else None
    
    # Optionally add description
    has_description = draw(st.booleans())
    description = draw(st.text(min_size=1, max_size=500)) if has_description else None
    
    return EventData(
        event_name=event_name,
        start_datetime=start_dt,
        end_datetime=end_dt,
        location=location,
        description=description
    )


class TestCalDAVGeneratorProperties:
    """Property-based tests for CalDAVGenerator."""
    
    @given(event_data=event_data_strategy())
    @settings(max_examples=100)
    def test_ics_generation_round_trip(self, event_data):
        """
        Property 8: ICS Generation Round-Trip
        
        For any valid EventData object, generating an ICS file and then
        parsing it back using an iCalendar parser should produce a calendar
        event with equivalent data (same event name, datetime, location, description).
        
        Feature: calendar-event-converter, Property 8: ICS Generation Round-Trip
        Validates: Requirements 3.1, 3.4, 3.5
        """
        generator = CalDAVGenerator()
        
        # Generate ICS content
        ics_content = generator.generate_ics(event_data)
        
        # Parse it back
        cal = Calendar.from_ical(ics_content)
        
        # Extract the event
        events = [component for component in cal.walk() if component.name == "VEVENT"]
        assert len(events) == 1, "Should have exactly one event"
        
        parsed_event = events[0]
        
        # Verify event name (summary)
        assert parsed_event.get('summary') == event_data.event_name
        
        # Verify start datetime
        parsed_start = parsed_event.get('dtstart').dt
        # Handle both datetime and date objects
        if isinstance(parsed_start, datetime):
            assert parsed_start == event_data.start_datetime
        else:
            # If it's a date, compare just the date part
            assert parsed_start == event_data.start_datetime.date()
        
        # Verify end datetime
        parsed_end = parsed_event.get('dtend').dt
        expected_end = event_data.end_datetime if event_data.end_datetime else event_data.start_datetime + timedelta(hours=1)
        if isinstance(parsed_end, datetime):
            assert parsed_end == expected_end
        else:
            assert parsed_end == expected_end.date()
        
        # Verify location (if provided)
        if event_data.location:
            assert parsed_event.get('location') == event_data.location
        
        # Verify description (if provided)
        if event_data.description:
            assert parsed_event.get('description') == event_data.description
    
    @given(event_data=event_data_strategy())
    @settings(max_examples=100)
    def test_event_data_preservation(self, event_data):
        """
        Property 9: Event Data Preservation
        
        For any EventData object with specific field values, the generated
        ICS file content should contain those values in the appropriate
        VEVENT properties (SUMMARY, DTSTART, LOCATION, DESCRIPTION).
        
        Feature: calendar-event-converter, Property 9: Event Data Preservation
        Validates: Requirements 3.2
        """
        generator = CalDAVGenerator()
        
        # Generate ICS content
        ics_content = generator.generate_ics(event_data)
        
        # Parse the ICS to verify data preservation
        cal = Calendar.from_ical(ics_content)
        
        # Extract the event
        events = [component for component in cal.walk() if component.name == "VEVENT"]
        assert len(events) == 1, "Should have exactly one event"
        
        parsed_event = events[0]
        
        # Verify event name is preserved
        assert parsed_event.get('summary') == event_data.event_name
        
        # Verify start datetime is preserved
        parsed_start = parsed_event.get('dtstart').dt
        if isinstance(parsed_start, datetime):
            assert parsed_start == event_data.start_datetime
        
        # Verify end datetime is preserved (or defaulted)
        parsed_end = parsed_event.get('dtend').dt
        expected_end = event_data.end_datetime if event_data.end_datetime else event_data.start_datetime + timedelta(hours=1)
        if isinstance(parsed_end, datetime):
            assert parsed_end == expected_end
        
        # Verify location is preserved if provided
        if event_data.location:
            assert parsed_event.get('location') == event_data.location
        
        # Verify description is preserved if provided
        if event_data.description:
            assert parsed_event.get('description') == event_data.description
        
        # Verify required fields are present
        assert parsed_event.get('uid') is not None
        assert parsed_event.get('dtstamp') is not None
    
    @given(event_data=event_data_strategy())
    @settings(max_examples=100)
    def test_uid_uniqueness(self, event_data):
        """
        Property 10: UID Uniqueness
        
        For any two separate calls to generate_ics (even with identical EventData),
        the generated UIDs should be different, ensuring each event has a unique identifier.
        
        Feature: calendar-event-converter, Property 10: UID Uniqueness
        Validates: Requirements 3.3
        """
        generator = CalDAVGenerator()
        
        # Generate two ICS files with the same event data
        ics_content_1 = generator.generate_ics(event_data)
        ics_content_2 = generator.generate_ics(event_data)
        
        # Parse both
        cal_1 = Calendar.from_ical(ics_content_1)
        cal_2 = Calendar.from_ical(ics_content_2)
        
        # Extract UIDs
        events_1 = [component for component in cal_1.walk() if component.name == "VEVENT"]
        events_2 = [component for component in cal_2.walk() if component.name == "VEVENT"]
        
        assert len(events_1) == 1
        assert len(events_2) == 1
        
        uid_1 = str(events_1[0].get('uid'))
        uid_2 = str(events_2[0].get('uid'))
        
        # UIDs should be different
        assert uid_1 != uid_2, "Each generated event should have a unique UID"


class TestCalDAVGeneratorUnit:
    """Unit tests for CalDAVGenerator."""
    
    def test_generate_ics_with_complete_event_data(self):
        """Test ICS generation with complete EventData.
        
        Requirements: 3.1, 3.2, 3.3
        """
        generator = CalDAVGenerator()
        
        event_data = EventData(
            event_name="Team Meeting",
            start_datetime=datetime(2025, 1, 10, 14, 0),
            end_datetime=datetime(2025, 1, 10, 15, 0),
            location="Conference Room A",
            description="Quarterly planning meeting"
        )
        
        ics_content = generator.generate_ics(event_data)
        
        # Verify basic structure
        assert 'BEGIN:VCALENDAR' in ics_content
        assert 'VERSION:2.0' in ics_content
        assert 'BEGIN:VEVENT' in ics_content
        assert 'END:VEVENT' in ics_content
        assert 'END:VCALENDAR' in ics_content
        
        # Verify required fields
        assert 'SUMMARY:Team Meeting' in ics_content
        assert 'DTSTART:20250110T140000' in ics_content
        assert 'DTEND:20250110T150000' in ics_content
        assert 'LOCATION:Conference Room A' in ics_content
        assert 'DESCRIPTION:Quarterly planning meeting' in ics_content
        assert 'UID:' in ics_content
        assert 'DTSTAMP:' in ics_content
    
    def test_generate_ics_with_minimal_event_data(self):
        """Test ICS generation with minimal EventData (only required fields).
        
        Requirements: 3.1, 3.2, 3.3
        """
        generator = CalDAVGenerator()
        
        event_data = EventData(
            event_name="Quick Meeting",
            start_datetime=datetime(2025, 1, 10, 14, 0)
        )
        
        ics_content = generator.generate_ics(event_data)
        
        # Verify basic structure
        assert 'BEGIN:VCALENDAR' in ics_content
        assert 'VERSION:2.0' in ics_content
        assert 'BEGIN:VEVENT' in ics_content
        assert 'END:VEVENT' in ics_content
        assert 'END:VCALENDAR' in ics_content
        
        # Verify required fields
        assert 'SUMMARY:Quick Meeting' in ics_content
        assert 'DTSTART:20250110T140000' in ics_content
        assert 'UID:' in ics_content
        assert 'DTSTAMP:' in ics_content
        
        # Optional fields should not be present
        assert 'LOCATION:' not in ics_content
        assert 'DESCRIPTION:' not in ics_content
    
    def test_default_end_datetime_behavior(self):
        """Test that end_datetime defaults to start_datetime + 1 hour.
        
        Requirements: 3.1, 3.2, 3.3
        """
        generator = CalDAVGenerator()
        
        event_data = EventData(
            event_name="Meeting",
            start_datetime=datetime(2025, 1, 10, 14, 0)
        )
        
        ics_content = generator.generate_ics(event_data)
        
        # Parse the ICS to verify end datetime
        cal = Calendar.from_ical(ics_content)
        events = [component for component in cal.walk() if component.name == "VEVENT"]
        
        assert len(events) == 1
        event = events[0]
        
        start = event.get('dtstart').dt
        end = event.get('dtend').dt
        
        # End should be 1 hour after start
        expected_end = datetime(2025, 1, 10, 15, 0)
        assert end == expected_end
        assert end == start + timedelta(hours=1)
    
    def test_generate_ics_validates_event_data(self):
        """Test that generate_ics validates event data before generation.
        
        Requirements: 3.1
        """
        generator = CalDAVGenerator()
        
        # Create invalid event data (empty event name)
        event_data = EventData(
            event_name="",
            start_datetime=datetime(2025, 1, 10, 14, 0)
        )
        
        # Should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            generator.generate_ics(event_data)
        
        assert "Event name is required" in str(exc_info.value)
    
    def test_generate_ics_with_end_before_start_raises_error(self):
        """Test that invalid datetime raises ValidationError.
        
        Requirements: 3.1
        """
        generator = CalDAVGenerator()
        
        # Create event with end before start
        event_data = EventData(
            event_name="Invalid Meeting",
            start_datetime=datetime(2025, 1, 10, 15, 0),
            end_datetime=datetime(2025, 1, 10, 14, 0)
        )
        
        # Should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            generator.generate_ics(event_data)
        
        assert "End datetime must be after start datetime" in str(exc_info.value)

