FROM python:3.9-slim

# Create a non-root user
RUN useradd -m -s /bin/bash sandbox

# Set up a working directory
WORKDIR /app

# Switch to non-root user
USER sandbox

# Set Python path
ENV PYTHONPATH=/app

# Set resource limits
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create a directory for code execution
RUN mkdir -p /app/code

# Set up a basic Python environment
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Set up entrypoint
COPY sandbox/entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"] 