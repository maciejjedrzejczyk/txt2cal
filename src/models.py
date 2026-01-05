"""Data models for Calendar Event Converter.

This module defines the core data structures used throughout the application
for representing event information and configuration settings.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.exceptions import ValidationError


@dataclass
class EventData:
    """Structured event information extracted from text.
    
    This class represents a calendar event with all its associated metadata.
    It includes validation logic to ensure the event data is complete and
    consistent before being used to generate ICS files.
    
    Attributes:
        event_name: Name/title of the event (required)
        start_datetime: When the event starts (required)
        end_datetime: When the event ends (optional, defaults to start + 1 hour)
        location: Where the event takes place (optional)
        description: Additional details about the event (optional)
    
    Example:
        >>> from datetime import datetime
        >>> event = EventData(
        ...     event_name="Team Meeting",
        ...     start_datetime=datetime(2025, 1, 15, 14, 0),
        ...     location="Conference Room A",
        ...     description="Quarterly planning session"
        ... )
        >>> event.validate()  # Raises ValidationError if invalid
    """
    event_name: str
    start_datetime: datetime
    location: Optional[str] = None
    description: Optional[str] = None
    end_datetime: Optional[datetime] = None
    
    def validate(self) -> None:
        """Validate that required fields are present and valid.
        
        This method checks:
        - Event name is not empty or whitespace-only
        - Start datetime is present
        - End datetime (if provided) is after start datetime
        
        Raises:
            ValidationError: If any validation check fails
            
        Example:
            >>> event = EventData(event_name="", start_datetime=datetime.now())
            >>> event.validate()
            ValidationError: Event name is required
        """
        if not self.event_name or not self.event_name.strip():
            raise ValidationError("Event name is required")
        if not self.start_datetime:
            raise ValidationError("Start datetime is required")
        if self.end_datetime and self.end_datetime <= self.start_datetime:
            raise ValidationError("End datetime must be after start datetime")
