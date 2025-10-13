import os
import socket
from pyngrok import ngrok
from waitress import serve
from app import app

# -------------------------------
# Function to find free port
# -------------------------------
def get_free_port(default_port=5000):
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

# -------------------------------
# Configuration
# -------------------------------
PORT = int(os.environ.get("PORT", get_free_port()))
HOST = "0.0.0.0"
ENV = os.environ.get("ENV", "local")  # 'production' or 'local'

# -------------------------------
# Ngrok for local testing
# -------------------------------
if ENV == "local":
    public_url = ngrok.connect(PORT)
    print(f"🚀 Public URL: {public_url} -> http://localhost:{PORT}")

# -------------------------------
# Start Waitress server (Windows-friendly)
# -------------------------------
print(f"🔹 Starting Dark Kitchen Bot on {HOST}:{PORT}")
serve(app, host=HOST, port=PORT)
