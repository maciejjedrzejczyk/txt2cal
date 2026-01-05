"""LLM-based event data extractor.

This module handles communication with Large Language Model (LLM) servers to
extract structured event information from unstructured text. It uses the OpenAI
API standard, making it compatible with various LLM providers.
"""

import json
from datetime import datetime
from typing import Any, Dict

from openai import OpenAI

from src.config import LLMConfig
from src.exceptions import ExtractionError, LLMError
from src.models import EventData


class LLMExtractor:
    """Extract structured event data from text using LLM.
    
    This class communicates with an LLM server using the OpenAI API standard
    to extract event information (name, datetime, location, description) from
    unstructured text. It crafts appropriate prompts, parses JSON responses,
    and validates the extracted data.
    
    The extractor is compatible with any OpenAI API-compatible LLM server,
    including LM Studio, OpenAI, and other providers.
    
    Example:
        >>> from src.config import LLMConfig
        >>> config = LLMConfig(
        ...     api_base="http://localhost:1234/v1",
        ...     model="ibm/granite-4-h-tiny"
        ... )
        >>> extractor = LLMExtractor(config)
        >>> text = "Team meeting tomorrow at 2pm in Conference Room A"
        >>> event = extractor.extract_event_data(text)
        >>> print(event.event_name)
        'Team meeting'
    """
    
    def __init__(self, config: LLMConfig):
        """Initialize LLM extractor with configuration.
        
        Args:
            config: LLM configuration containing API endpoint, model name,
                   API key, and timeout settings
        
        Example:
            >>> config = LLMConfig(
            ...     api_base="http://localhost:1234/v1",
            ...     model="ibm/granite-4-h-tiny",
            ...     timeout=30
            ... )
            >>> extractor = LLMExtractor(config)
        """
        self.config = config
        self.client = OpenAI(
            base_url=config.api_base,
            api_key=config.api_key,
            timeout=config.timeout
        )
    
    def extract_event_data(self, text: str) -> EventData:
        """Extract event information from text using LLM.
        
        This method sends the text to the LLM with a carefully crafted prompt
        that instructs it to extract event details in JSON format. It then
        parses the response, validates required fields, and creates an EventData
        object.
        
        The LLM is instructed to extract:
        - event_name (required): The name or title of the event
        - start_datetime (required): When the event starts (ISO 8601 format)
        - end_datetime (optional): When the event ends (ISO 8601 format)
        - location (optional): Where the event takes place
        - description (optional): Additional details about the event
        
        Args:
            text: Unstructured text containing event information
            
        Returns:
            EventData object with extracted and validated fields
            
        Raises:
            LLMError: If LLM communication fails (network, timeout, API errors)
            ExtractionError: If required event data cannot be extracted or is invalid
        
        Example:
            >>> extractor = LLMExtractor(config)
            >>> text = "Project kickoff on Jan 15, 2025 at 10am in Building 3"
            >>> event = extractor.extract_event_data(text)
            >>> print(f"{event.event_name} at {event.start_datetime}")
            'Project kickoff at 2025-01-15 10:00:00'
        """
        # Craft system prompt for event extraction
        system_prompt = """You are an event information extraction assistant. 
Extract event details from the provided text and return them in JSON format.

Required fields:
- event_name: The name or title of the event (string)
- start_datetime: When the event starts (ISO 8601 format: YYYY-MM-DDTHH:MM:SS)

Optional fields:
- end_datetime: When the event ends (ISO 8601 format: YYYY-MM-DDTHH:MM:SS)
- location: Where the event takes place (string)
- description: Additional details about the event (string)

Return ONLY valid JSON with these fields. Do not include any other text."""

        user_prompt = f"Extract event information from this text:\n\n{text}"
        
        try:
            # Make API request to LLM
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,  # Deterministic output for extraction
            )
            
            # Extract response content
            content = response.choices[0].message.content
            if not content:
                raise ExtractionError("LLM returned empty response")
            
            # Parse JSON response
            try:
                event_dict = json.loads(content)
            except json.JSONDecodeError as e:
                raise ExtractionError(f"Failed to parse LLM response as JSON: {e}")
            
            # Validate required fields are present
            if "event_name" not in event_dict:
                raise ExtractionError("Missing required field: event_name")
            if "start_datetime" not in event_dict:
                raise ExtractionError("Missing required field: start_datetime")
            
            # Parse datetime strings
            try:
                start_datetime = self._parse_datetime(event_dict["start_datetime"])
            except (ValueError, TypeError) as e:
                raise ExtractionError(f"Invalid start_datetime format: {e}")
            
            end_datetime = None
            if "end_datetime" in event_dict and event_dict["end_datetime"]:
                try:
                    end_datetime = self._parse_datetime(event_dict["end_datetime"])
                except (ValueError, TypeError) as e:
                    raise ExtractionError(f"Invalid end_datetime format: {e}")
            
            # Create EventData object
            event_data = EventData(
                event_name=event_dict["event_name"],
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                location=event_dict.get("location"),
                description=event_dict.get("description")
            )
            
            # Validate the event data
            event_data.validate()
            
            return event_data
            
        except ExtractionError:
            # Re-raise extraction errors as-is
            raise
        except Exception as e:
            # Wrap any other errors as LLMError
            raise LLMError(f"Failed to communicate with LLM: {e}")
    
    def _parse_datetime(self, dt_string: str) -> datetime:
        """Parse datetime string in ISO 8601 format.
        
        This method attempts to parse datetime strings using various ISO 8601
        formats with different precision levels. It tries formats with and
        without time components, with and without microseconds.
        
        Args:
            dt_string: Datetime string in ISO 8601 format (e.g., "2025-01-15T14:00:00")
            
        Returns:
            Parsed datetime object
            
        Raises:
            ValueError: If datetime string cannot be parsed with any supported format
        
        Example:
            >>> extractor = LLMExtractor(config)
            >>> dt = extractor._parse_datetime("2025-01-15T14:00:00")
            >>> print(dt)
            2025-01-15 14:00:00
        """
        # Try ISO 8601 format with various precision levels
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(dt_string, fmt)
            except ValueError:
                continue
        
        # If none of the formats work, raise error
        raise ValueError(f"Unable to parse datetime: {dt_string}")
