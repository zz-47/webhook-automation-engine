import os
from pyngrok import ngrok
from app import app, HOST, PORT

# Only start ngrok if NOT in production
if os.environ.get("RAILWAY_ENV") != "production":
    public_url = ngrok.connect(PORT)
    print(f"🚀 Public URL: {public_url} -> http://localhost:{PORT}")

# Start Flask app
app.run(host=HOST, port=PORT)
