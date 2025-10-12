import os
from pyngrok import ngrok

# Use dynamic port for both local and production fallback
PORT = int(os.environ.get("PORT", 5000))

# -------------------------------
# Start ngrok tunnel (local only)
# -------------------------------
if os.environ.get("RAILWAY_ENV") != "production":
    public_url = ngrok.connect(PORT)
    print(f"🚀 Public URL: {public_url} -> http://localhost:{PORT}")

# -------------------------------
# Start Flask app
# -------------------------------
FLASK_APP_PATH = os.path.join(os.path.dirname(__file__), "app.py")
os.system(f'python "{FLASK_APP_PATH}"')
