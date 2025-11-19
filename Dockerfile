# Python slim base
FROM python:3.11-slim

# Install Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Install system deps + Tesseract OCR
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Set locale (avoid Unicode issues)
RUN sed -i 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# Workdir
WORKDIR /app

# Copy only requirements first (for better layer caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the app
COPY src /app/src
COPY README.md /app/README.md

# Expose app port
EXPOSE 8000

# Default envs — safe defaults (can override with -e)
ENV DRY_RUN=1 \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000

# Start with Gunicorn for production-ish serving
# (Flask dev server is fine locally, but Gunicorn is standard)
CMD ["sh", "-c", "gunicorn --workers 1 --threads 1 --timeout 120 -b 0.0.0.0:${PORT:-8000} src.app.server:app"]


