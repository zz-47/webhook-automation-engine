import os
from pyngrok import ngrok
from app import app, PORT, HOST  # import directly from your Flask app

# -------------------------------
# Start ngrok tunnel (local only)
# -------------------------------
if os.environ.get("RAILWAY_ENV") != "production":
    public_url = ngrok.connect(PORT)
    print(f"🚀 Public URL: {public_url} -> http://localhost:{PORT}")

# -------------------------------
# Start Flask app
# -------------------------------
print(f"🔹 Starting Flask app on {HOST}:{PORT}")
app.run(host=HOST, port=PORT, debug=False)
