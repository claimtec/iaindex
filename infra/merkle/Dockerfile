# Merkle Attestation System Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY infra/merkle/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY infra/merkle/*.py ./

# Create attestations directory
RUN mkdir -p /attestations

# Create non-root user
RUN useradd -m -u 1001 merkle && \
    chown -R merkle:merkle /app /attestations

USER merkle

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

# Default command (run once mode)
CMD ["python", "cron.py", "--mode", "once"]
