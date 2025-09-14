FROM python:3.11-slim

# Install system dependencies for ping
RUN apt-get update && apt-get install -y \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Set environment variables
ENV TIMEZONE=UTC
ENV CLEANUP_DAYS=30
ENV DATA_DIR=/app/data

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]