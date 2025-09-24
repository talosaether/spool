# Movie Catalog - Hexagonal Architecture Demo
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Add current directory to Python path for imports
ENV PYTHONPATH=/app

# Expose port for web API
EXPOSE 5000

# Default command runs the web API
CMD ["python", "movie_web_adapter.py"]