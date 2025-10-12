import os
from pyngrok import ngrok

# -------------------------------
# Start ngrok tunnel
# -------------------------------
public_url = ngrok.connect(5000)
print(f"🚀 Public URL: {public_url} -> http://localhost:5000")

# -------------------------------
# Determine Flask app path
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLASK_APP_DIR = BASE_DIR  # <-- remove extra dark_kitchen_chatbot
FLASK_APP_PATH = os.path.join(FLASK_APP_DIR, "app.py")

# -------------------------------
# Change working directory to Flask app folder
# -------------------------------
os.chdir(FLASK_APP_DIR)

# -------------------------------
# Start Flask
# -------------------------------
os.system(f'python "{FLASK_APP_PATH}"')
