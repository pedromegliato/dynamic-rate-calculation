# Build stage
FROM --platform=$BUILDPLATFORM python:3.10-slim as builder

ARG TARGETPLATFORM
ARG BUILDPLATFORM

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy project files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir fastapi uvicorn pydantic pydantic-settings python-dotenv mysql-connector-python sqlalchemy pymysql requests structlog redis fastapi-limiter tenacity circuitbreaker python-json-logger python-jose passlib python-dateutil pytz uvloop httptools

# Final stage
FROM --platform=$TARGETPLATFORM python:3.10-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Environment variables for uvicorn
ENV UVICORN_WORKERS=4 \
    UVICORN_THREADS=2 \
    UVICORN_TIMEOUT=120 \
    UVICORN_LIMIT_CONCURRENCY=1000 \
    UVICORN_TIMEOUT_KEEP_ALIVE=120

# Run application with optimized settings
CMD ["uvicorn", "app.main:app", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "--workers", "4", \
    "--limit-concurrency", "1000", \
    "--timeout-keep-alive", "120", \
    "--access-log"]
