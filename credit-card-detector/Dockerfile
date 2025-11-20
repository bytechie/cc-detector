# Multi-stage Dockerfile for Credit Card Detector
# Optimized for production with security best practices

# Base stage
FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    gnupg \
    git \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Dependencies stage
FROM base AS dependencies

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
COPY requirements-dev.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Development stage
FROM dependencies AS development

# Install development dependencies
RUN pip install -r requirements-dev.txt

# Copy source code
COPY . .

# Set permissions
RUN chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Default command for development
CMD ["python", "app.py", "--mode", "basic"]

# Production stage
FROM base AS production

# Install only production dependencies
WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY app.py ./
COPY skills/ ./skills/
COPY config/ ./config/
COPY README.md .

# Create necessary directories
RUN mkdir -p logs data plugins skills && \
    chown -R appuser:appuser /app

# Set up configuration
ENV FLASK_ENV=production \
    FLASK_APP=app

# Security: Remove unnecessary packages
RUN apt-get remove -y gcc g++ build-essential && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Production command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]

# Testing stage
FROM development AS testing

# Run tests
RUN python -m pytest tests/ -v --cov=skills

# Security scanning stage
FROM production AS security-scanner

# Install security scanning tools
RUN pip install bandit safety

# Run security scans
RUN bandit -r claude_subagent/ -f json -o bandit-report.json || true
RUN safety check --json --output safety-report.json || true

# Plugin builder stage
FROM base AS plugin-builder

WORKDIR /app

# Install plugin development tools
RUN pip install setuptools wheel twine

# Copy plugin template
COPY plugins/plugin_template/ ./plugin_template/
COPY scripts/build_plugin.py ./scripts/

# Default command for building plugins
CMD ["python", "scripts/build_plugin.py"]

# Final stage (default)
FROM production AS final