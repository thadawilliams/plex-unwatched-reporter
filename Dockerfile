FROM python:3.11-slim

WORKDIR /app

# Install Docker CLI for shutdown functionality
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -fsSL https://get.docker.com -o get-docker.sh && \
    sh get-docker.sh && \
    rm get-docker.sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir flask==3.0.0 plexapi

# Copy the single application file
COPY app.py .

# Create necessary directories
RUN mkdir -p /config /reports

# Expose port
EXPOSE 4080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:4080/health')" || exit 1

# Start the application
CMD ["python", "-u", "app.py"]
