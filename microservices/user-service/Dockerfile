# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
# Upgrade pip and install dependencies in one layer
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Prisma
RUN pip install prisma

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p /app/logs


# Generate Prisma client

RUN prisma generate

# Expose port
EXPOSE 8002

# Start with simple Python command (plus fiable)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8002"]