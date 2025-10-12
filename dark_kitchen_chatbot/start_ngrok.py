from pyngrok import ngrok
import os
import subprocess
import sys

# -------------------------------
# Flask port
# -------------------------------
PORT = int(os.environ.get("PORT", 5050))

# -------------------------------
# Start ngrok tunnel
# -------------------------------
public_url = ngrok.connect(PORT)
print(f"🚀 Public URL: {public_url} -> http://localhost:{PORT}")

# -------------------------------
# Start Flask app
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLASK_APP_PATH = os.path.join(BASE_DIR, "app.py")  # Adjust if app.py is in this folder

subprocess.run([sys.executable, FLASK_APP_PATH, str(PORT)])
