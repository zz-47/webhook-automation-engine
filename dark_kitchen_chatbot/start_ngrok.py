import os
from pyngrok import ngrok

# -------------------------------
# Get dynamic Flask port
# -------------------------------
PORT = int(os.environ.get("PORT", 5000))

# -------------------------------
# Start ngrok tunnel
# -------------------------------
public_url = ngrok.connect(PORT)
print(f"🚀 Public URL: {public_url} -> http://localhost:{PORT}")

# -------------------------------
# Start Flask app
# -------------------------------
FLASK_APP_PATH = os.path.join(os.path.dirname(__file__), "app.py")
os.system(f'python "{FLASK_APP_PATH}"')
