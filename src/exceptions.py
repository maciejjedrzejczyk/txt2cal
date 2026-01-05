"""Custom exception classes for Calendar Event Converter.

This module defines a hierarchy of exceptions used throughout the application
to handle different types of errors that can occur during the conversion process.
All exceptions inherit from CalendarConverterError for easy catching of any
application-specific error.
"""


class CalendarConverterError(Exception):
    """Base exception for all application errors.
    
    This is the parent class for all custom exceptions in the Calendar Event
    Converter application. Catching this exception will catch all application-
    specific errors.
    
    Example:
        try:
            service.convert_document(file_content, file_type)
        except CalendarConverterError as e:
            logger.error(f"Conversion failed: {e}")
    """
    pass


class ParsingError(CalendarConverterError):
    """Document parsing failed.
    
    Raised when the system cannot extract text from a document file.
    This can occur due to:
    - Corrupted or invalid file format
    - Unsupported file type
    - Empty document with no extractable text
    - Encoding issues (for text files)
    
    Example:
        raise ParsingError("Failed to parse PDF: file is corrupted")
    """
    pass


class LLMError(CalendarConverterError):
    """LLM communication failed.
    
    Raised when the system cannot communicate with the LLM server.
    This can occur due to:
    - Network connectivity issues
    - LLM server not running or unreachable
    - API authentication failures
    - Timeout waiting for LLM response
    
    Example:
        raise LLMError("Failed to connect to LLM server at http://localhost:1234")
    """
    pass


class ExtractionError(CalendarConverterError):
    """Event data extraction failed.
    
    Raised when the LLM cannot extract required event information from text.
    This can occur due to:
    - Missing required fields (event name or start datetime)
    - Invalid datetime format in LLM response
    - LLM returning non-JSON response
    - Text not containing recognizable event information
    
    Example:
        raise ExtractionError("Missing required field: start_datetime")
    """
    pass


class ValidationError(CalendarConverterError):
    """Data validation failed.
    
    Raised when event data or generated ICS content fails validation.
    This can occur due to:
    - Empty or whitespace-only event name
    - Missing start datetime
    - End datetime before start datetime
    - ICS generation failures
    
    Example:
        raise ValidationError("End datetime must be after start datetime")
    """
    pass
