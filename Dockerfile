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

# Copy project configuration and package directories for editable install
COPY pyproject.toml .
COPY abupy/ abupy/
COPY crypto_quant_pro/ crypto_quant_pro/
COPY config/ config/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -e ".[dev]"

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
