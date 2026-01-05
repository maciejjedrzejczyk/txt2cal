FROM python:3.11-slim

# Install uv package manager
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY config/ ./config/

# Install dependencies using uv
RUN uv pip install --system -e .

# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
