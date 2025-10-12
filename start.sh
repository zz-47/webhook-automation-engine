#!/bin/bash

# Activate virtual environment
source /app/.venv/bin/activate

# Start ngrok in background
python /app/dark_kitchen_chatbot/start_ngrok.py &

# Start Flask app
python /app/dark_kitchen_chatbot/app.py
