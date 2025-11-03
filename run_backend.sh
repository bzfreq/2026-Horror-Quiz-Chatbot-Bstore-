#!/bin/bash

echo "================================================"
echo "   HORROR ORACLE - FLASK + LANGCHAIN BACKEND"
echo "================================================"
echo ""
echo "Starting the server..."
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run the Flask app
python app.py


