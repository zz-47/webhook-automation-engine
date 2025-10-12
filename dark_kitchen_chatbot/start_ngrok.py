import os
import socket
from pyngrok import ngrok, conf

# -------------------------------
# Function to find a free port
# -------------------------------
def get_free_port(default_port=5000):
    """Return a free port, fallback to default."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", 0))
    free_port = sock.getsockname()[1]
    sock.close()
    return free_port or default_port

# -------------------------------
# Set PORT dynamically
# -------------------------------
PORT = int(os.environ.get("PORT", get_free_port()))
HOST = "0.0.0.0"

# -------------------------------
# Start ngrok tunnel (local only)
# -------------------------------
if os.environ.get("RAILWAY_ENV") != "production":
    # Ensure pyngrok uses a clean config
    conf.get_default().region = "us"
    try:
        public_url = ngrok.connect(PORT)
        print(f"🚀 Public URL: {public_url} -> http://localhost:{PORT}")
    except Exception as e:
        print(f"⚠️ Ngrok failed: {e}")

# -------------------------------
# Start Flask app
# -------------------------------
FLASK_APP_PATH = os.path.join(os.path.dirname(__file__), "app.py")
print(f"🔹 Starting Flask app on {HOST}:{PORT}")
os.system(f'python "{FLASK_APP_PATH}"')
