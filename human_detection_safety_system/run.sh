#!/bin/bash
# Human Detection Safety System Startup Script

echo "🚨 Starting Human Detection Safety System..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Run the system
python main.py "$@"
