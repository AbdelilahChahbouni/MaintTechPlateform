# ==============================================================
# MAINTTECH JOBS MAROC - PRODUCTION DOCKERFILE
# Multi-arch ready, security-hardened, non-root user
# ==============================================================

FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=5000

WORKDIR /app

# Install system dependencies (curl for healthcheck, libpq for PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y gcc libpq-dev \
    && apt-get autoremove -y

# Copy application source code
COPY . .

# Create non-root user for security compliance in cloud containers
RUN useradd -m -u 1000 -s /bin/bash mainttech && \
    mkdir -p /app/uploads/cvs /app/uploads/avatars && \
    chmod +x /app/docker-entrypoint.sh && \
    chown -R mainttech:mainttech /app

USER mainttech

# Healthcheck for AWS ECS, GCP Cloud Run, Kubernetes, Docker Swarm
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE 5000

ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default command: Gunicorn WSGI production server with 4 workers
CMD ["gunicorn", "--workers=4", "--threads=2", "--bind=0.0.0.0:5000", "--access-logfile=-", "--error-logfile=-", "app:create_app()"]
