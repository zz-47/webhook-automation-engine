import os
import socket
from pyngrok import ngrok
from waitress import serve

# -------------------------------
# Ensure app.py is in the same folder
# -------------------------------
try:
    from app import app
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "Cannot find 'app.py'. Make sure app.py is in the same folder as start_server.py"
    )

# -------------------------------
# Function to find a free port
# -------------------------------
def get_free_port(default_port=5000):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 0))  # Bind to a free port
        port = s.getsockname()[1]
        s.close()
        return port
    except Exception:
        return default_port

# -------------------------------
# Configuration
# -------------------------------
PORT = int(os.environ.get("PORT", get_free_port()))
HOST = "0.0.0.0"
ENV = os.environ.get("ENV", "local")  # 'production' or 'local'

# -------------------------------
# Ngrok for local testing
# -------------------------------
if ENV.lower() == "local":
    try:
        public_url = ngrok.connect(PORT)
        print(f"🚀 Public URL: {public_url} -> http://localhost:{PORT}")
    except Exception as e:
        print(f"⚠️ Ngrok could not start: {e}")

# -------------------------------
# Start Waitress server
# -------------------------------
print(f"🔹 Starting Dark Kitchen Bot on {HOST}:{PORT} in {ENV} mode...")
serve(app, host=HOST, port=PORT)
