# Optimized Multi-stage Dockerfile for Railway / Coolify
# Reduced from ~6.5GB to ~1.5GB + HTTPS mirror fix

# ============================
# Builder stage
# ============================
FROM python:3.11-slim-bookworm AS builder

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Force Debian mirrors to HTTPS to avoid ISP/proxy hijack
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org|https://security.debian.org|g' /etc/apt/sources.list

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Download NLTK data in builder layer
RUN python -c "import nltk; nltk.download('wordnet', download_dir='/root/nltk_data'); nltk.download('omw-1.4', download_dir='/root/nltk_data')"


# ============================
# runtime stage
# ============================
FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Force Debian mirrors to HTTPS (same as builder)
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org|https://security.debian.org|g' /etc/apt/sources.list

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages and NLTK data from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /root/nltk_data /usr/local/share/nltk_data

# Copy application code
COPY . .

# Environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    NLTK_DATA=/usr/local/share/nltk_data \
    PATH=/root/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check (still respects PORT env)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run the application (keep shell form for ${PORT:-8000} expansion)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
