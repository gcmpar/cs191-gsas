# Stage 1: Base build stage
FROM python:3.12.7-slim AS builder
 
# Install build dependencies for mysqlclient and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create the app directory
RUN mkdir /app
 
# Set the working directory
WORKDIR /app
 
# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 
 
# Install dependencies first for caching benefit
RUN pip install --upgrade pip 
COPY requirements.txt /app/ 
RUN pip install --no-cache-dir -r requirements.txt
 
# Stage 2: Production stage
FROM python:3.12.7-slim

# Install runtime dependencies for mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*
 
RUN useradd -m -r appuser && \
   mkdir /app && \
   chown -R appuser /app
 
# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
 
# Set the working directory
WORKDIR /app
 
# Copy application code
COPY --chown=appuser:appuser . .
 
# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser
 
# Expose the application port
EXPOSE 8000

# Collect static files, run migrations, then start gunicorn
# NOTE: Keep GUNICORN_WORKERS at 1 if using Django Select2 without caching layer
CMD ["/bin/sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate --noinput && python -m gunicorn --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS} gsas.wsgi:application"]
