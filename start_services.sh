#!/bin/sh

# Start Ollama in the background
echo "Starting Ollama..."
ollama serve &

# Wait for Ollama to start
sleep 5

# Pull and run the LLM model (if not already pulled)
OLLAMA_MODEL=${OLLAMA_MODEL:-"llama3.1:8b"}
echo "Ensuring model '$OLLAMA_MODEL' is available..."
ollama pull "$OLLAMA_MODEL"

# Start FastAPI after Ollama is ready
echo "Starting FastAPI..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
