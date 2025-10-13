# snap_integration.py
import os
import time
import requests
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv

load_dotenv()
snap_bp = Blueprint("snap_bp", __name__)

# --- Snapchat API Config ---
SNAP_CLIENT_ID = os.getenv("SNAP_CLIENT_ID")
SNAP_CLIENT_SECRET = os.getenv("SNAP_CLIENT_SECRET")
SNAP_REDIRECT_URI = os.getenv("SNAP_REDIRECT_URI")
SNAP_API_BASE = os.getenv("SNAP_API_BASE", "https://adsapi.snapchat.com/v1")
SNAP_CONVERSION_TOKEN = os.getenv("SNAP_CONVERSION_TOKEN")  # Conversions API token
NGROK_URL = os.getenv("NGROK_URL", "https://hatchable-presley-extrinsic.ngrok-free.dev")

if not SNAP_CONVERSION_TOKEN:
    print("⚠️ WARNING: SNAP_CONVERSION_TOKEN not set. Snap events will fail.")

# -----------------------------
# Step 0: Automatic webhook registration
# -----------------------------
def register_snap_webhook():
    """Register your ngrok webhook URL with Snapchat Messaging API."""
    url = f"{SNAP_API_BASE}/messaging/webhooks"
    headers = {
        "Authorization": f"Bearer {SNAP_CONVERSION_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "webhook_url": f"{NGROK_URL}/snap/webhook"
    }

    try:
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code in (200, 201):
            print("✅ Snapchat webhook registered successfully!")
        else:
            print(f"⚠️ Failed to register webhook: {res.status_code} - {res.text}")
    except Exception as e:
        print("❌ Error registering webhook:", e)

# -----------------------------
# Step 1: OAuth callback
# -----------------------------
@snap_bp.route("/snap/auth/callback")
def snap_auth_callback():
    """Handles Snapchat OAuth callback"""
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Missing 'code' in callback"}), 400

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": SNAP_CLIENT_ID,
        "client_secret": SNAP_CLIENT_SECRET,
        "redirect_uri": SNAP_REDIRECT_URI,
    }

    try:
        res = requests.post(f"{SNAP_API_BASE}/oauth2/token", data=data)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Step 2: Webhook for incoming messages
# -----------------------------
@snap_bp.route("/snap/webhook", methods=["POST"])
def snap_webhook():
    """
    Receive messages from Snapchat.
    Event format depends on Snapchat Messaging API.
    """
    event = request.json
    print("📩 Received Snap event:", event)

    user_text = event.get("message", {}).get("text", "")
    conversation_id = event.get("conversation_id")

    if not user_text or not conversation_id:
        return jsonify({"status": "ignored"}), 200

    # Call chatbot message handler
    from app import handle_user_message
    reply = handle_user_message(user_text)

    # Send reply back
    send_snap_message(conversation_id, reply)
    return jsonify({"status": "ok"}), 200

# -----------------------------
# Step 3: Send messages to Snapchat
# -----------------------------
def send_snap_message(conversation_id, text):
    """Send a text reply to Snapchat conversation"""
    if not SNAP_CONVERSION_TOKEN:
        print("⚠️ SNAP_CONVERSION_TOKEN missing. Cannot send message.")
        return {"error": "Missing SNAP_CONVERSION_TOKEN"}

    headers = {
        "Authorization": f"Bearer {SNAP_CONVERSION_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    url = f"{SNAP_API_BASE}/business/conversations/{conversation_id}/messages"

    try:
        res = requests.post(url, headers=headers, json=payload)
        print("📤 Sent Snap message:", res.status_code, res.text)
        return res.json()
    except Exception as e:
        print("❌ Error sending Snap message:", e)
        return {"error": str(e)}

# -----------------------------
# Step 4: Send conversion events
# -----------------------------
def send_snap_event(event_name, user_id=None):
    """Send a conversion event (chat_started, order_completed, etc.)"""
    if not SNAP_CONVERSION_TOKEN:
        print(f"⚠️ Cannot send Snap event '{event_name}', token missing")
        return

    headers = {
        "Authorization": f"Bearer {SNAP_CONVERSION_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "event_name": event_name,
        "event_time": int(time.time()),
        "user": {"external_id": user_id or "anonymous"},
        "custom_data": {"source": "dark_kitchen_bot"}
    }

    url = "https://tr.snapchat.com/v2/conversion"
    try:
        res = requests.post(url, headers=headers, json=payload)
        print(f"📡 Snap event '{event_name}' sent:", res.status_code)
        if res.status_code >= 400:
            print("⚠️ Snapchat API error:", res.text)
    except Exception as e:
        print("⚠️ Error sending event to Snap:", e)

# -----------------------------
# Auto-register webhook at startup
# -----------------------------
register_snap_webhook()
