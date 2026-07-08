# =============================================================================
# pipeline/Dockerfile
# Production multi-stage image for the AI pipeline
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: build — install Python deps into a venv
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS build

# Build-time dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip wheel && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2: runtime — lean image with only what's needed
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

LABEL maintainer="pipeline-ai"
LABEL description="Missing Person Face Recognition AI Pipeline"

# Runtime system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libpq5 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for security
RUN groupadd -r pipeline && useradd -r -g pipeline pipeline

WORKDIR /app

# Copy virtualenv from build stage
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy pipeline source code
COPY . /app/pipeline/

# Copy model and data directories (expected as Docker volumes in production)
# Models are read-only mounts; data is a read-write volume.
VOLUME ["/app/models", "/app/data"]

# Create working directories
RUN mkdir -p \
    /app/data/embeddings/backup \
    /app/data/faiss/backup \
    /app/data/registered_faces \
    /app/data/uploads/images \
    /app/data/uploads/videos \
    /app/data/uploads/temp \
    && chown -R pipeline:pipeline /app/data

# Switch to non-root
USER pipeline

# Health check — verifies the pipeline process is importable
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "from pipeline.database.connection import health_check; exit(0 if health_check() else 1)"

# Entrypoint: override CMD in docker-compose for specific modes
# e.g. CMD ["python", "-m", "pipeline.main"]
CMD ["python", "-c", "print('AI Pipeline container ready. Override CMD to start.')"]
