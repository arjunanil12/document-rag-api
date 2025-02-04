# Use an official lightweight Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy only the requirements file to leverage Docker's caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Make sure the start script is executable
RUN chmod +x /app/start_services.sh

# Expose the ports for FastAPI and Ollama
EXPOSE 8000
EXPOSE 11434

# Run the startup script
CMD ["/app/start_services.sh"]