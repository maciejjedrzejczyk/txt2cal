"""CalDAV ICS file generator.

This module generates CalDAV-compatible ICS (iCalendar) files from structured
event data. It uses the icalendar library to create properly formatted calendar
files that can be imported into any calendar application.
"""

from datetime import datetime, timedelta
from uuid import uuid4
from icalendar import Calendar, Event

from src.models import EventData
from src.exceptions import ValidationError


class CalDAVGenerator:
    """Generate CalDAV-compatible ICS files from event data.
    
    This class creates ICS (iCalendar) files that conform to the CalDAV standard
    (RFC 5545). The generated files include all required components (VCALENDAR,
    VEVENT) and properties (UID, DTSTAMP, DTSTART, DTEND, SUMMARY) along with
    optional properties (LOCATION, DESCRIPTION).
    
    The generator ensures:
    - Unique event identifiers (UID) using UUID
    - Proper datetime formatting
    - Default end time (start + 1 hour) if not provided
    - Valid ICS structure
    
    Example:
        >>> from datetime import datetime
        >>> from src.models import EventData
        >>> generator = CalDAVGenerator()
        >>> event = EventData(
        ...     event_name="Team Meeting",
        ...     start_datetime=datetime(2025, 1, 15, 14, 0),
        ...     location="Conference Room A"
        ... )
        >>> ics_content = generator.generate_ics(event)
        >>> print(ics_content)
        BEGIN:VCALENDAR
        VERSION:2.0
        ...
    """
    
    def generate_ics(self, event_data: EventData) -> str:
        """Generate CalDAV-compatible ICS file content.
        
        This method creates a complete ICS file with:
        - VCALENDAR component with VERSION 2.0
        - VEVENT component with all event details
        - Unique UID generated using UUID
        - Current timestamp (DTSTAMP)
        - Start and end datetimes (DTSTART, DTEND)
        - Event summary/name (SUMMARY)
        - Optional location (LOCATION)
        - Optional description (DESCRIPTION)
        
        If end_datetime is not provided, it defaults to start_datetime + 1 hour.
        
        Args:
            event_data: Structured event information with validated fields
            
        Returns:
            ICS file content as a UTF-8 string
            
        Raises:
            ValidationError: If event data is invalid or ICS generation fails
        
        Example:
            >>> generator = CalDAVGenerator()
            >>> event = EventData(
            ...     event_name="Workshop",
            ...     start_datetime=datetime(2025, 2, 20, 9, 0),
            ...     end_datetime=datetime(2025, 2, 20, 16, 0),
            ...     location="Tech Hub",
            ...     description="Python for Data Science"
            ... )
            >>> ics = generator.generate_ics(event)
            >>> with open("event.ics", "w") as f:
            ...     f.write(ics)
        """
        # Validate event data first
        event_data.validate()
        
        # Create calendar
        cal = Calendar()
        cal.add('prodid', '-//Calendar Event Converter//EN')
        cal.add('version', '2.0')
        
        # Create event
        event = Event()
        
        # Add UID (unique identifier) - generates a new UUID for each event
        event.add('uid', str(uuid4()))
        
        # Add timestamp (current UTC time)
        event.add('dtstamp', datetime.utcnow())
        
        # Add start datetime
        event.add('dtstart', event_data.start_datetime)
        
        # Add end datetime (default to start + 1 hour if not provided)
        if event_data.end_datetime:
            event.add('dtend', event_data.end_datetime)
        else:
            event.add('dtend', event_data.start_datetime + timedelta(hours=1))
        
        # Add summary (event name)
        event.add('summary', event_data.event_name)
        
        # Add location if provided
        if event_data.location:
            event.add('location', event_data.location)
        
        # Add description if provided
        if event_data.description:
            event.add('description', event_data.description)
        
        # Add event to calendar
        cal.add_component(event)
        
        # Generate ICS content
        try:
            ics_content = cal.to_ical().decode('utf-8')
            return ics_content
        except Exception as e:
            raise ValidationError(f"Failed to generate ICS file: {str(e)}")
