FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/

# Install Python dependencies with version pinning
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -U setuptools wheel && \
    pip install --no-cache-dir psycopg2-binary && \
    pip install --no-cache-dir fastapi==0.101.0 uvicorn==0.23.2 && \
    pip install --no-cache-dir pydantic==2.1.1 && \
    pip install --no-cache-dir pydantic-settings==2.0.3 && \
    pip install --no-cache-dir python-dotenv==1.0.0 && \
    pip install --no-cache-dir numpy==1.25.2 && \
    pip install --no-cache-dir pgvector

# Copy application files
COPY main.py /app/
COPY app /app/app/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV TOKENIZERS_PARALLELISM=false

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8001/ || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]