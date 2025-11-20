# Docker Development Guide

This guide explains how to use Docker for development in the Crypto Trading project.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

## Quick Start

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Services

The `docker-compose.yml` defines the following services:

### app
Main application container with Python 3.11 and all dependencies.

**Ports:**
- `8000`: REST API (when implemented)

**Volumes:**
- `.` → `/app`: Source code (live reload)
- `./data` → `/app/data`: Persistent data storage

**Usage:**
```bash
# Run tests
docker-compose exec app pytest

# Run linting
docker-compose exec app ruff check .

# Access shell
docker-compose exec app bash

# Install new package
docker-compose exec app pip install package-name
```

### db
PostgreSQL 15 database for storing trading data.

**Ports:**
- `5432`: PostgreSQL connection

**Connection:**
- Host: `localhost` (from host) or `db` (from other containers)
- User: `postgres`
- Password: `postgres`
- Database: `crypto_trading`

**Usage:**
```bash
# Connect to database
docker-compose exec db psql -U postgres -d crypto_trading

# Backup database
docker-compose exec db pg_dump -U postgres crypto_trading > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres crypto_trading < backup.sql
```

### redis
Redis 7 cache for performance optimization.

**Ports:**
- `6379`: Redis connection

**Usage:**
```bash
# Connect to Redis CLI
docker-compose exec redis redis-cli

# Monitor commands
docker-compose exec redis redis-cli MONITOR
```

## Development Workflow

### 1. Start Development Environment

```bash
docker-compose up -d
```

### 2. Run Tests

```bash
# All tests
docker-compose exec app pytest

# Specific test file
docker-compose exec app pytest tests/unit/test_abupy/test_core_bu.py

# With coverage
docker-compose exec app pytest --cov=abupy --cov-report=html
```

### 3. Code Quality Checks

```bash
# Linting
docker-compose exec app ruff check .

# Format code
docker-compose exec app ruff format .

# Type checking
docker-compose exec app mypy abupy/
```

### 4. Install Dependencies

```bash
# Install new package
docker-compose exec app pip install package-name

# Update requirements.txt
docker-compose exec app pip freeze > requirements.txt
```

### 5. Database Migrations

```bash
# Run migrations (when implemented)
docker-compose exec app alembic upgrade head

# Create new migration
docker-compose exec app alembic revision --autogenerate -m "description"
```

## Building Custom Images

```bash
# Build image
docker-compose build app

# Build without cache
docker-compose build --no-cache app

# Rebuild specific service
docker-compose up -d --build app
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs app

# Check container status
docker-compose ps

# Restart service
docker-compose restart app
```

### Permission issues

```bash
# Fix file permissions
docker-compose exec app chown -R $(id -u):$(id -g) /app
```

### Database connection issues

```bash
# Check if database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up -d db
```

### Clear all data

```bash
# Stop and remove everything including volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## Environment Variables

Create a `.env` file in the project root to override defaults:

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=crypto_trading

# Application
PYTHONPATH=/app
LOG_LEVEL=INFO
```

## Production Considerations

The current `Dockerfile` and `docker-compose.yml` are optimized for development.

For production:
- Use multi-stage builds
- Remove development dependencies
- Set proper security contexts
- Use secrets management
- Configure health checks
- Set resource limits

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Python Docker Best Practices](https://docs.docker.com/language/python/)
