"""REST API endpoints for Calendar Event Converter."""

import logging
from typing import Dict, Any
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import os

from src.service import EventConversionService
from src.exceptions import (
    ParsingError,
    LLMError,
    ExtractionError,
    ValidationError,
    CalendarConverterError
)


# Configure logging
logger = logging.getLogger(__name__)


class TextConversionRequest(BaseModel):
    """Request model for text conversion endpoint."""
    text: str = Field(..., description="Plain text containing event information")


class ConversionSuccessResponse(BaseModel):
    """Response model for successful conversion."""
    ics_content: str = Field(..., description="Generated ICS file content")
    filename: str = Field(..., description="Suggested filename for the ICS file")


class ConversionErrorResponse(BaseModel):
    """Response model for conversion errors."""
    error: str = Field(..., description="Error message")
    details: str = Field(..., description="Detailed error information")


def create_app(
    service: EventConversionService,
    max_file_size_bytes: int,
    max_text_length: int
) -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Args:
        service: Event conversion service instance
        max_file_size_bytes: Maximum allowed file size in bytes
        max_text_length: Maximum allowed text length in characters
        
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Calendar Event Converter API",
        description="Convert documents and text to CalDAV-compatible calendar events",
        version="1.0.0"
    )
    
    # Mount static files directory for serving HTML
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/", summary="Serve web UI", description="Serve the interactive web interface")
    async def serve_ui():
        """Serve the HTML UI page."""
        html_path = os.path.join(static_dir, "index.html")
        if os.path.exists(html_path):
            return FileResponse(html_path)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="UI not found"
            )
    
    @app.post(
        "/api/v1/convert/document",
        response_model=ConversionSuccessResponse,
        responses={
            400: {"model": ConversionErrorResponse, "description": "Bad request"},
            413: {"model": ConversionErrorResponse, "description": "File too large"},
            500: {"model": ConversionErrorResponse, "description": "Internal server error"}
        },
        summary="Convert document to ICS file",
        description="Upload a document (PDF, DOCX, or TXT) and convert it to a CalDAV-compatible ICS file"
    )
    async def convert_document(
        file: UploadFile = File(..., description="Document file to convert")
    ) -> ConversionSuccessResponse:
        """
        Convert uploaded document to ICS file.
        
        Args:
            file: Uploaded document file
            
        Returns:
            ConversionSuccessResponse with ICS content and filename
            
        Raises:
            HTTPException: For various error conditions
        """
        logger.info(f"Received document conversion request: {file.filename}")
        
        try:
            # Read file content
            file_content = await file.read()
            
            # Validate file size
            file_size = len(file_content)
            if file_size > max_file_size_bytes:
                logger.warning(f"File too large: {file_size} bytes")
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail={
                        "error": "File too large",
                        "details": f"File size {file_size} bytes exceeds maximum allowed size of {max_file_size_bytes} bytes"
                    }
                )
            
            # Determine file type from filename
            if file.filename:
                file_extension = file.filename.split('.')[-1].lower()
            else:
                file_extension = "txt"
            
            # Validate file type
            supported_types = ["pdf", "docx", "txt"]
            if file_extension not in supported_types:
                logger.warning(f"Unsupported file type: {file_extension}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "Unsupported file type",
                        "details": f"File type '{file_extension}' is not supported. Supported types: {', '.join(supported_types)}"
                    }
                )
            
            # Convert document
            ics_content = service.convert_document(file_content, file_extension)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"event_{timestamp}.ics"
            
            logger.info(f"Document conversion successful: {filename}")
            return ConversionSuccessResponse(
                ics_content=ics_content,
                filename=filename
            )
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except ParsingError as e:
            logger.error(f"Parsing error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Failed to parse document",
                    "details": "Please ensure the file is not corrupted and is a valid PDF, DOCX, or TXT file"
                }
            )
        except LLMError as e:
            logger.error(f"LLM error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Failed to communicate with LLM server",
                    "details": "Please check your connection and try again"
                }
            )
        except ExtractionError as e:
            logger.error(f"Extraction error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Could not extract event information",
                    "details": "Please ensure your text includes event name and date"
                }
            )
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Validation failed",
                    "details": str(e)
                }
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Internal server error",
                    "details": "An unexpected error occurred during conversion"
                }
            )
    
    @app.post(
        "/api/v1/convert/text",
        response_model=ConversionSuccessResponse,
        responses={
            400: {"model": ConversionErrorResponse, "description": "Bad request"},
            413: {"model": ConversionErrorResponse, "description": "Text too long"},
            500: {"model": ConversionErrorResponse, "description": "Internal server error"}
        },
        summary="Convert text to ICS file",
        description="Convert plain text containing event information to a CalDAV-compatible ICS file"
    )
    async def convert_text(
        request: TextConversionRequest
    ) -> ConversionSuccessResponse:
        """
        Convert plain text to ICS file.
        
        Args:
            request: Text conversion request with text field
            
        Returns:
            ConversionSuccessResponse with ICS content and filename
            
        Raises:
            HTTPException: For various error conditions
        """
        logger.info("Received text conversion request")
        
        try:
            # Validate text length
            text_length = len(request.text)
            if text_length > max_text_length:
                logger.warning(f"Text too long: {text_length} characters")
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail={
                        "error": "Text too long",
                        "details": f"Text length {text_length} characters exceeds maximum allowed length of {max_text_length} characters"
                    }
                )
            
            # Validate text is not empty
            if not request.text.strip():
                logger.warning("Empty text provided")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "Empty text",
                        "details": "Please provide text containing event information"
                    }
                )
            
            # Convert text
            ics_content = service.convert_text(request.text)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"event_{timestamp}.ics"
            
            logger.info(f"Text conversion successful: {filename}")
            return ConversionSuccessResponse(
                ics_content=ics_content,
                filename=filename
            )
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except LLMError as e:
            logger.error(f"LLM error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Failed to communicate with LLM server",
                    "details": "Please check your connection and try again"
                }
            )
        except ExtractionError as e:
            logger.error(f"Extraction error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Could not extract event information",
                    "details": "Please ensure your text includes event name and date"
                }
            )
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Validation failed",
                    "details": str(e)
                }
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Internal server error",
                    "details": "An unexpected error occurred during conversion"
                }
            )
    
    @app.get("/health", summary="Health check", description="Check if the API is running")
    async def health_check() -> Dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy"}
    
    @app.post(
        "/convert/document",
        summary="Convert document to ICS file (UI endpoint)",
        description="Upload a document and receive a downloadable ICS file"
    )
    async def ui_convert_document(
        file: UploadFile = File(..., description="Document file to convert")
    ) -> Response:
        """
        Convert uploaded document to ICS file for UI download.
        
        Args:
            file: Uploaded document file
            
        Returns:
            Response with ICS file content and download headers
            
        Raises:
            HTTPException: For various error conditions
        """
        logger.info(f"Received UI document conversion request: {file.filename}")
        
        try:
            # Read file content
            file_content = await file.read()
            
            # Validate file size
            file_size = len(file_content)
            if file_size > max_file_size_bytes:
                logger.warning(f"File too large: {file_size} bytes")
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail={
                        "error": "File too large",
                        "details": f"File size {file_size} bytes exceeds maximum allowed size of {max_file_size_bytes} bytes"
                    }
                )
            
            # Determine file type from filename
            if file.filename:
                file_extension = file.filename.split('.')[-1].lower()
            else:
                file_extension = "txt"
            
            # Validate file type
            supported_types = ["pdf", "docx", "txt"]
            if file_extension not in supported_types:
                logger.warning(f"Unsupported file type: {file_extension}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "Unsupported file type",
                        "details": f"File type '{file_extension}' is not supported. Supported types: {', '.join(supported_types)}"
                    }
                )
            
            # Convert document
            ics_content = service.convert_document(file_content, file_extension)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"event_{timestamp}.ics"
            
            logger.info(f"UI document conversion successful: {filename}")
            
            # Return ICS file with download headers
            return Response(
                content=ics_content,
                media_type="text/calendar",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except ParsingError as e:
            logger.error(f"Parsing error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Failed to parse document",
                    "details": "Please ensure the file is not corrupted and is a valid PDF, DOCX, or TXT file"
                }
            )
        except LLMError as e:
            logger.error(f"LLM error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Failed to communicate with LLM server",
                    "details": "Please check your connection and try again"
                }
            )
        except ExtractionError as e:
            logger.error(f"Extraction error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Could not extract event information",
                    "details": "Please ensure your text includes event name and date"
                }
            )
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Validation failed",
                    "details": str(e)
                }
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Internal server error",
                    "details": "An unexpected error occurred during conversion"
                }
            )
    
    @app.post(
        "/convert/text",
        summary="Convert text to ICS file (UI endpoint)",
        description="Convert plain text and receive a downloadable ICS file"
    )
    async def ui_convert_text(
        request: TextConversionRequest
    ) -> Response:
        """
        Convert plain text to ICS file for UI download.
        
        Args:
            request: Text conversion request with text field
            
        Returns:
            Response with ICS file content and download headers
            
        Raises:
            HTTPException: For various error conditions
        """
        logger.info("Received UI text conversion request")
        
        try:
            # Validate text length
            text_length = len(request.text)
            if text_length > max_text_length:
                logger.warning(f"Text too long: {text_length} characters")
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail={
                        "error": "Text too long",
                        "details": f"Text length {text_length} characters exceeds maximum allowed length of {max_text_length} characters"
                    }
                )
            
            # Validate text is not empty
            if not request.text.strip():
                logger.warning("Empty text provided")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "Empty text",
                        "details": "Please provide text containing event information"
                    }
                )
            
            # Convert text
            ics_content = service.convert_text(request.text)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"event_{timestamp}.ics"
            
            logger.info(f"UI text conversion successful: {filename}")
            
            # Return ICS file with download headers
            return Response(
                content=ics_content,
                media_type="text/calendar",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except LLMError as e:
            logger.error(f"LLM error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Failed to communicate with LLM server",
                    "details": "Please check your connection and try again"
                }
            )
        except ExtractionError as e:
            logger.error(f"Extraction error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Could not extract event information",
                    "details": "Please ensure your text includes event name and date"
                }
            )
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Validation failed",
                    "details": str(e)
                }
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Internal server error",
                    "details": "An unexpected error occurred during conversion"
                }
            )
    
    return app
