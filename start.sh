#!/bin/bash
# start.sh - starts your Flask bot via start_ngrok.py

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Run the bot
python dark_kitchen_chatbot/start_ngrok.py
