#!/bin/bash
# start.sh - start Flask bot with ngrok

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Run the bot
python dark_kitchen_chatbot/start_ngrok.py
