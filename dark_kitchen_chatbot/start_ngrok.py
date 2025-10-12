import os
from pyngrok import ngrok
import subprocess

# Get dynamic port same as app.py
PORT = int(os.environ.get("PORT", 5000))

# Only run ngrok for local development
if os.environ.get("RAILWAY_ENV") != "production":
    public_url = ngrok.connect(PORT)
    print(f"🚀 Ngrok Tunnel: {public_url} -> http://localhost:{PORT}")

# Start Flask locally
subprocess.run(["python", "app.py"])
