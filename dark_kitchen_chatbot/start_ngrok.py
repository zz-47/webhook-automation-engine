import os
import sys
from pyngrok import ngrok
from app import app, get_free_port

# -------------------------------
# Dynamic Port
# -------------------------------
PORT = int(os.environ.get("PORT", get_free_port()))
HOST = "0.0.0.0"

# -------------------------------
# Start ngrok tunnel (only if not in production)
# -------------------------------
if os.environ.get("RAILWAY_ENV") != "production":
    public_url = ngrok.connect(PORT)
    print(f"🚀 Ngrok Tunnel: {public_url} -> http://localhost:{PORT}")

# -------------------------------
# Run Flask
# -------------------------------
print(f"🔹 Starting Dark Kitchen Bot on {HOST}:{PORT}")
app.run(host=HOST, port=PORT, debug=False)
