import os
from pyngrok import ngrok, conf
import subprocess
import socket

# -------------------------------
# Function to get a free port
# -------------------------------
def get_free_port(default_port=5000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", 0))
    free_port = sock.getsockname()[1]
    sock.close()
    return free_port or default_port

# -------------------------------
# Set host and port
# -------------------------------
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", get_free_port()))

# -------------------------------
# Ngrok only for non-production
# -------------------------------
if os.environ.get("RAILWAY_ENV") != "production":
    # Optional: set ngrok cached path to avoid repeated downloads
    conf.get_default().ngrok_path = "/tmp/ngrok"
    public_url = ngrok.connect(PORT)
    print(f"🚀 Public URL: {public_url} -> http://localhost:{PORT}")

# -------------------------------
# Start Flask app
# -------------------------------
FLASK_APP_PATH = os.path.join(os.path.dirname(__file__), "app.py")

# Use subprocess to start Flask in the same console
subprocess.run(["python", FLASK_APP_PATH])
