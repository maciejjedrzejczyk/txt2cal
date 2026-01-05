"""Event conversion service orchestrating the conversion pipeline.

This module provides the main service layer that orchestrates the complete
conversion pipeline from input (document or text) to output (ICS file).
It coordinates the parser, extractor, and generator components.
"""

import logging
from typing import Optional

from src.parser import DocumentParser
from src.extractor import LLMExtractor
from src.generator import CalDAVGenerator
from src.exceptions import (
    ParsingError,
    LLMError,
    ExtractionError,
    ValidationError,
    CalendarConverterError
)


# Configure logging
logger = logging.getLogger(__name__)


class EventConversionService:
    """Orchestrate the conversion pipeline from input to ICS file.
    
    This service coordinates the three main processing components:
    1. DocumentParser: Extracts text from documents
    2. LLMExtractor: Extracts structured event data from text
    3. CalDAVGenerator: Generates ICS files from event data
    
    It provides two conversion methods:
    - convert_document: Full pipeline (parse → extract → generate)
    - convert_text: Partial pipeline (extract → generate)
    
    The service handles errors at each stage and provides comprehensive logging
    for debugging and monitoring.
    
    Example:
        >>> from src.parser import DocumentParser
        >>> from src.extractor import LLMExtractor
        >>> from src.generator import CalDAVGenerator
        >>> from src.config import LLMConfig
        >>> 
        >>> parser = DocumentParser()
        >>> extractor = LLMExtractor(LLMConfig(...))
        >>> generator = CalDAVGenerator()
        >>> service = EventConversionService(parser, extractor, generator)
        >>> 
        >>> # Convert document
        >>> with open("meeting.pdf", "rb") as f:
        ...     ics = service.convert_document(f.read(), "pdf")
        >>> 
        >>> # Convert text
        >>> text = "Team meeting tomorrow at 2pm"
        >>> ics = service.convert_text(text)
    """
    
    def __init__(
        self,
        parser: DocumentParser,
        extractor: LLMExtractor,
        generator: CalDAVGenerator
    ):
        """Initialize service with injected dependencies.
        
        This constructor uses dependency injection to allow for easy testing
        and flexibility in component configuration.
        
        Args:
            parser: Document parser for extracting text from files
            extractor: LLM extractor for extracting event data from text
            generator: CalDAV generator for creating ICS files
        
        Example:
            >>> service = EventConversionService(
            ...     parser=DocumentParser(),
            ...     extractor=LLMExtractor(config),
            ...     generator=CalDAVGenerator()
            ... )
        """
        self.parser = parser
        self.extractor = extractor
        self.generator = generator
    
    def convert_document(self, file_content: bytes, file_type: str) -> str:
        """Convert document to ICS file.
        
        This method orchestrates the full conversion pipeline:
        1. Parse document to extract text content
        2. Extract structured event data from text using LLM
        3. Generate CalDAV-compatible ICS file from event data
        
        Each step is logged for debugging and monitoring. Errors at any stage
        are caught and re-raised with appropriate error types.
        
        Args:
            file_content: Raw bytes of the document file
            file_type: MIME type or file extension (e.g., 'pdf', 'docx', 'txt')
            
        Returns:
            ICS file content as a UTF-8 string
            
        Raises:
            ParsingError: If document parsing fails
            LLMError: If LLM communication fails
            ExtractionError: If event data extraction fails
            ValidationError: If event data validation or ICS generation fails
            CalendarConverterError: For unexpected errors
        
        Example:
            >>> service = EventConversionService(parser, extractor, generator)
            >>> with open("event.pdf", "rb") as f:
            ...     ics_content = service.convert_document(f.read(), "pdf")
            >>> with open("event.ics", "w") as f:
            ...     f.write(ics_content)
        """
        logger.info(f"Starting document conversion for file type: {file_type}")
        
        try:
            # Step 1: Parse document to extract text
            logger.debug("Parsing document...")
            text = self.parser.parse(file_content, file_type)
            logger.debug(f"Extracted {len(text)} characters of text")
            
            # Step 2: Extract event data from text
            logger.debug("Extracting event data from text...")
            event_data = self.extractor.extract_event_data(text)
            logger.debug(f"Extracted event: {event_data.event_name}")
            
            # Step 3: Generate ICS file
            logger.debug("Generating ICS file...")
            ics_content = self.generator.generate_ics(event_data)
            logger.info("Document conversion completed successfully")
            
            return ics_content
            
        except ParsingError as e:
            logger.error(f"Parsing error: {e}")
            raise
        except LLMError as e:
            logger.error(f"LLM error: {e}")
            raise
        except ExtractionError as e:
            logger.error(f"Extraction error: {e}")
            raise
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during document conversion: {e}")
            raise CalendarConverterError(f"Unexpected error: {e}") from e
    
    def convert_text(self, text: str) -> str:
        """Convert plain text to ICS file.
        
        This method treats the input text as already-parsed content and
        skips the document parsing step. It orchestrates:
        1. Extract structured event data from text using LLM
        2. Generate CalDAV-compatible ICS file from event data
        
        This is useful when the input is already in text format (e.g., from
        a text field in the UI or API) and doesn't need parsing.
        
        Args:
            text: Plain text containing event information
            
        Returns:
            ICS file content as a UTF-8 string
            
        Raises:
            LLMError: If LLM communication fails
            ExtractionError: If event data extraction fails
            ValidationError: If event data validation or ICS generation fails
            CalendarConverterError: For unexpected errors
        
        Example:
            >>> service = EventConversionService(parser, extractor, generator)
            >>> text = "Project kickoff meeting on Jan 15 at 10am in Building 3"
            >>> ics_content = service.convert_text(text)
            >>> with open("event.ics", "w") as f:
            ...     f.write(ics_content)
        """
        logger.info("Starting text conversion")
        
        try:
            # Step 1: Extract event data from text
            logger.debug("Extracting event data from text...")
            event_data = self.extractor.extract_event_data(text)
            logger.debug(f"Extracted event: {event_data.event_name}")
            
            # Step 2: Generate ICS file
            logger.debug("Generating ICS file...")
            ics_content = self.generator.generate_ics(event_data)
            logger.info("Text conversion completed successfully")
            
            return ics_content
            
        except LLMError as e:
            logger.error(f"LLM error: {e}")
            raise
        except ExtractionError as e:
            logger.error(f"Extraction error: {e}")
            raise
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during text conversion: {e}")
            raise CalendarConverterError(f"Unexpected error: {e}") from e
