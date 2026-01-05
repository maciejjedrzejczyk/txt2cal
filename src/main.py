"""Main application entry point for Calendar Event Converter."""

import logging
import sys
from pathlib import Path

from src.config import load_config
from src.parser import DocumentParser
from src.extractor import LLMExtractor
from src.generator import CalDAVGenerator
from src.service import EventConversionService
from src.api import create_app
from src.exceptions import CalendarConverterError


def setup_logging(log_level: str = "INFO") -> None:
    """Configure application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def create_application():
    """
    Create and configure the FastAPI application with all dependencies.
    
    Returns:
        Configured FastAPI application instance
        
    Raises:
        CalendarConverterError: If application initialization fails
    """
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting Calendar Event Converter application...")
        
        # Load configuration
        logger.info("Loading configuration...")
        config_path = Path("config/config.yaml")
        config = load_config(config_path)
        logger.info(f"Configuration loaded: LLM={config.llm.model}, Server={config.server.host}:{config.server.port}")
        
        # Initialize components
        logger.info("Initializing components...")
        
        # Create document parser
        parser = DocumentParser()
        logger.debug("DocumentParser initialized")
        
        # Create LLM extractor
        extractor = LLMExtractor(config.llm)
        logger.debug(f"LLMExtractor initialized with model: {config.llm.model}")
        
        # Create CalDAV generator
        generator = CalDAVGenerator()
        logger.debug("CalDAVGenerator initialized")
        
        # Create event conversion service
        service = EventConversionService(
            parser=parser,
            extractor=extractor,
            generator=generator
        )
        logger.debug("EventConversionService initialized")
        
        # Calculate max file size in bytes
        max_file_size_bytes = config.limits.max_file_size_mb * 1024 * 1024
        
        # Create FastAPI application
        logger.info("Creating FastAPI application...")
        app = create_app(
            service=service,
            max_file_size_bytes=max_file_size_bytes,
            max_text_length=config.limits.max_text_length
        )
        
        # Add custom exception handlers
        @app.exception_handler(CalendarConverterError)
        async def calendar_converter_error_handler(request, exc):
            """Handle CalendarConverterError exceptions."""
            logger.error(f"CalendarConverterError: {exc}")
            from fastapi import status
            from fastapi.responses import JSONResponse
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Application error",
                    "details": str(exc)
                }
            )
        
        logger.info("Application initialization complete")
        logger.info(f"Ready to accept requests on {config.server.host}:{config.server.port}")
        
        return app
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}", exc_info=True)
        raise CalendarConverterError(f"Application initialization failed: {e}") from e


# Create the application instance
app = create_application()


if __name__ == "__main__":
    """Run the application using uvicorn when executed directly."""
    import uvicorn
    from src.config import load_config
    
    # Load configuration to get server settings
    config = load_config(Path("config/config.yaml"))
    
    # Run the server
    uvicorn.run(
        "src.main:app",
        host=config.server.host,
        port=config.server.port,
        reload=False,  # Disable reload in production
        log_level="info"
    )
