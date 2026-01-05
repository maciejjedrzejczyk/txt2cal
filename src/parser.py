"""Document parser for extracting text from various file formats.

This module provides a unified interface for parsing different document formats
(PDF, DOCX, TXT) and extracting their text content. It uses a factory pattern
to select the appropriate parser based on file type.
"""

from typing import Union
import io

from pypdf import PdfReader
from docx import Document

from src.exceptions import ParsingError


class DocumentParser:
    """Parser for extracting text content from various document formats.
    
    This class provides a unified interface for parsing PDF, DOCX, and TXT files.
    It automatically selects the appropriate parsing method based on the file type
    and handles errors gracefully.
    
    Supported formats:
    - PDF: Uses pypdf library to extract text from all pages
    - DOCX: Uses python-docx library to extract text from all paragraphs
    - TXT: Direct UTF-8 decoding
    
    Example:
        >>> parser = DocumentParser()
        >>> with open("document.pdf", "rb") as f:
        ...     text = parser.parse(f.read(), "pdf")
        >>> print(text)
        'Extracted text from PDF...'
    """
    
    def parse(self, file_content: bytes, file_type: str) -> str:
        """Extract text from document content.
        
        This method uses a factory pattern to select the appropriate parser
        based on the file type. It normalizes the file type (removes leading
        dots, converts to lowercase) and supports both file extensions and
        MIME types.
        
        Args:
            file_content: Raw bytes of the document
            file_type: MIME type or file extension (e.g., 'pdf', 'docx', 'txt',
                      'application/pdf', '.pdf')
            
        Returns:
            Extracted text content as a string
            
        Raises:
            ParsingError: If document cannot be parsed or file type is unsupported
        
        Example:
            >>> parser = DocumentParser()
            >>> text = parser.parse(pdf_bytes, "pdf")
            >>> text = parser.parse(docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        """
        # Normalize file type to lowercase and remove leading dot if present
        file_type = file_type.lower().lstrip('.')
        
        # Factory pattern for file type selection
        try:
            if file_type in ['pdf', 'application/pdf']:
                return self._parse_pdf(file_content)
            elif file_type in ['docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                return self._parse_docx(file_content)
            elif file_type in ['txt', 'text/plain']:
                return self._parse_txt(file_content)
            else:
                raise ParsingError(f"Unsupported file type: {file_type}")
        except ParsingError:
            # Re-raise ParsingError as-is
            raise
        except Exception as e:
            # Wrap any other exception in ParsingError
            raise ParsingError(f"Failed to parse document: {str(e)}") from e
    
    def _parse_pdf(self, file_content: bytes) -> str:
        """Parse PDF file and extract text.
        
        Extracts text from all pages of a PDF document using the pypdf library.
        Pages are joined with newlines to preserve document structure.
        
        Args:
            file_content: Raw bytes of PDF file
            
        Returns:
            Extracted text content from all pages
            
        Raises:
            ParsingError: If PDF parsing fails or PDF contains no extractable text
        
        Example:
            >>> parser = DocumentParser()
            >>> text = parser._parse_pdf(pdf_bytes)
        """
        try:
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)
            
            # Extract text from all pages
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            result = '\n'.join(text_parts)
            
            if not result.strip():
                raise ParsingError("PDF file contains no extractable text")
            
            return result
        except ParsingError:
            raise
        except Exception as e:
            raise ParsingError(f"Failed to parse PDF: {str(e)}") from e
    
    def _parse_docx(self, file_content: bytes) -> str:
        """Parse DOCX file and extract text.
        
        Extracts text from all paragraphs of a DOCX document using the python-docx
        library. Paragraphs are joined with newlines to preserve document structure.
        
        Args:
            file_content: Raw bytes of DOCX file
            
        Returns:
            Extracted text content from all paragraphs
            
        Raises:
            ParsingError: If DOCX parsing fails or DOCX contains no extractable text
        
        Example:
            >>> parser = DocumentParser()
            >>> text = parser._parse_docx(docx_bytes)
        """
        try:
            docx_file = io.BytesIO(file_content)
            doc = Document(docx_file)
            
            # Extract text from all paragraphs
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            result = '\n'.join(text_parts)
            
            if not result.strip():
                raise ParsingError("DOCX file contains no extractable text")
            
            return result
        except ParsingError:
            raise
        except Exception as e:
            raise ParsingError(f"Failed to parse DOCX: {str(e)}") from e
    
    def _parse_txt(self, file_content: bytes) -> str:
        """Parse TXT file with UTF-8 decoding.
        
        Decodes text file content using UTF-8 encoding. This is the simplest
        parser as it just performs character decoding.
        
        Args:
            file_content: Raw bytes of TXT file
            
        Returns:
            Decoded text content
            
        Raises:
            ParsingError: If TXT decoding fails or file is empty
        
        Example:
            >>> parser = DocumentParser()
            >>> text = parser._parse_txt(txt_bytes)
        """
        try:
            text = file_content.decode('utf-8')
            
            if not text.strip():
                raise ParsingError("TXT file is empty")
            
            return text
        except UnicodeDecodeError as e:
            raise ParsingError(f"Failed to decode TXT file as UTF-8: {str(e)}") from e
        except Exception as e:
            raise ParsingError(f"Failed to parse TXT: {str(e)}") from e
