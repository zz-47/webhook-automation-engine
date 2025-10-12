import os
from pyngrok import ngrok
from app import app  # your Flask app

PORT = int(os.environ.get("PORT", 5000))
HOST = "0.0.0.0"

# Only use ngrok for local development
if os.environ.get("RAILWAY_ENV") != "production":
    public_url = ngrok.connect(PORT)
    print(f"🚀 Public URL: {public_url} -> http://localhost:{PORT}")

app.run(host=HOST, port=PORT)
