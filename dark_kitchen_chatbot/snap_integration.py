# snap_integration.py
import os
import requests
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
snap_bp = Blueprint("snap_bp", __name__)

# --- Snapchat API Config ---
SNAP_CLIENT_ID = os.getenv("SNAP_CLIENT_ID")
SNAP_CLIENT_SECRET = os.getenv("SNAP_CLIENT_SECRET")
SNAP_REDIRECT_URI = os.getenv("SNAP_REDIRECT_URI")
SNAP_API_BASE = os.getenv("SNAP_API_BASE", "https://adsapi.snapchat.com/v1")
SNAP_CONVERSION_TOKEN = os.getenv("SNAP_CONVERSION_TOKEN")  # Put your Conversions API token here

# --- Step 1: OAuth callback ---
@snap_bp.route("/snap/auth/callback")
def snap_auth_callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Missing code"}), 400

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": SNAP_CLIENT_ID,
        "client_secret": SNAP_CLIENT_SECRET,
        "redirect_uri": SNAP_REDIRECT_URI,
    }
    res = requests.post(f"{SNAP_API_BASE}/oauth2/token", data=data)
    return jsonify(res.json()), res.status_code

# --- Step 2: Webhook for incoming messages ---
@snap_bp.route("/snap/webhook", methods=["POST"])
def snap_webhook():
    event = request.json
    print("📩 Received Snap event:", event)

    # Extract user message text
    user_text = event.get("message", {}).get("text", "")
    if not user_text:
        return jsonify({"status": "ignored"})

    # Import your chatbot handler
    from app import handle_user_message
    reply = handle_user_message(user_text)

    # Send reply back via Snapchat Messaging API
    conversation_id = event.get("conversation_id")
    if conversation_id:
        send_snap_message(conversation_id, reply)

    return jsonify({"status": "ok"})

# --- Step 3: Send messages to Snapchat ---
def send_snap_message(conversation_id, text):
    """Send text reply via Snapchat Messaging API"""
    headers = {
        "Authorization": f"Bearer {SNAP_CONVERSION_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    url = f"{SNAP_API_BASE}/business/conversations/{conversation_id}/messages"

    try:
        res = requests.post(url, headers=headers, json=payload)
        print("📤 Sent message:", res.status_code, res.text)
        return res.json()
    except Exception as e:
        print("❌ Error sending Snap message:", e)
        return {"error": str(e)}

# --- Step 4: Send custom Snap conversion events ---
def send_snap_event(event_name, user_id=None):
    """Send custom conversion events (chat_started, order_completed, etc.)"""
    headers = {
        "Authorization": f"Bearer {SNAP_CONVERSION_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "event_type": event_name.upper(),
        "event_conversion_type": "WEB",
        "timestamp": int(datetime.utcnow().timestamp()),
        "user": {
            "external_id": user_id or "unknown"
        },
        "custom_data": {
            "source": "dark_kitchen_bot"
        }
    }

    url = "https://tr.snapchat.com/v2/conversion"
    try:
        res = requests.post(url, headers=headers, json=payload)
        print(f"📡 Snap event '{event_name}' sent:", res.status_code)
        print(res.text)
        return res.json()
    except Exception as e:
        print("⚠️ Error sending event to Snap:", e)
        return {"error": str(e)}
