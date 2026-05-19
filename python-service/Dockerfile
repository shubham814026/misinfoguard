FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Tesseract OCR with multilingual support
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-spa \
    tesseract-ocr-fra \
    tesseract-ocr-deu \
    tesseract-ocr-hin \
    tesseract-ocr-ara \
    tesseract-ocr-chi-sim \
    libtesseract-dev \
    poppler-utils \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy multilingual model for 100+ language support
RUN pip install --no-cache-dir https://github.com/explosion/spacy-models/releases/download/xx_ent_wiki_sm-3.7.0/xx_ent_wiki_sm-3.7.0-py3-none-any.whl

# Copy application files
COPY . .

# Create uploads directory and set ownership to non-root user
RUN useradd -m -u 1001 appuser && mkdir -p uploads && chown -R appuser:appuser /app

# Run as non-root user for security
USER appuser

# Expose port
EXPOSE 8000

# Start server (--reload removed: it's a dev-only flag, not suitable for containers)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
