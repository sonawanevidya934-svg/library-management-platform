# Base image: official lightweight Python 3.11
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

WORKDIR /app

# curl is needed by the HEALTHCHECK below
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Layer caching: copy requirements first so pip install is cached
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only what the running application needs
COPY app/ ./app/
COPY database/ ./database/
COPY run.py .

# Security best practice: run as a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# One worker + threads: the in-memory store is thread-safe but not shared across processes
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "run:app"]
