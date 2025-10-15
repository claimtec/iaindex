#!/bin/bash
# Run script for IA Index Verification API

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run the application
if [ "$1" = "dev" ]; then
    echo "Starting development server..."
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
elif [ "$1" = "prod" ]; then
    echo "Starting production server..."
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
else
    echo "Usage: ./run.sh [dev|prod]"
    echo "  dev  - Run development server with auto-reload"
    echo "  prod - Run production server with 4 workers"
fi
