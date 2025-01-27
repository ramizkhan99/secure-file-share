# Use Python 3.10 as base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PHASE=production
ENV VAULT_ADDR=http://vault:8200
ENV VAULT_TOKEN=root

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Run migrations and start server
# CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver_plus 0.0.0.0:8000 --cert-file localhost.crt --key-file localhost.key"]
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--reload", "--certfile=localhost.crt", "--keyfile=localhost.key"]
