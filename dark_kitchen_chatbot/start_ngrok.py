from pyngrok import ngrok
import os
import subprocess
import sys

# -------------------------------
# Flask port
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
# Assuming app.py is in the same folder
subprocess.run([sys.executable, "app.py", str(PORT)])
