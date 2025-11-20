# Dockerfile for Crypto Trading System
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage cache
COPY requirements.txt .
COPY requirements-dev.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-dev.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p logs data/db data/cache

# Expose ports
# 8000: REST API
# 8501: Streamlit/Dashboard (if used)
EXPOSE 8000 8501

# Default command (can be overridden in docker-compose)
CMD ["python", "-m", "pytest"]
