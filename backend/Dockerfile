FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including build tools
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies with retry
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install PDF parsing dependency
RUN pip install --no-cache-dir PyPDF2

# Copy backend application code
COPY backend/app/ ./app/

# Copy backend data files
COPY backend/data/ ./data/

# Copy entrypoint script
COPY backend/docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Create directories for uploads and data
RUN mkdir -p uploads data question_pdfs

# Copy question bank files from project root
COPY question_bank_config.json /app/question_bank_config.json
COPY question_bank_light.json /app/question_bank_light.json

# Copy PDF import script from project root
COPY import_pdf_questions.py /app/import_pdf_questions.py

# Expose port
EXPOSE 8000

# Use entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
