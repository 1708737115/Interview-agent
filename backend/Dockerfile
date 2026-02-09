FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including build tools
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with retry
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install PDF parsing dependency
RUN pip install --no-cache-dir PyPDF2

# Copy application code
COPY app/ ./app/

# Copy data files
COPY data/ ./data/

# Copy entrypoint script
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Create directories for uploads and data
RUN mkdir -p uploads data question_pdfs

# Copy base question bank
COPY question_bank_config.json /app/question_bank_config.json

# Copy PDF import script
COPY import_pdf_questions.py /app/import_pdf_questions.py

# Expose port
EXPOSE 8000

# Use entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
