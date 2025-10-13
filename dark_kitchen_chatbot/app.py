import os
import json
import time
import requests
from flask import Flask, request, jsonify, render_template
from datetime import datetime
from threading import Lock

app = Flask(__name__)

# -------------------------------
# Configuration
# -------------------------------
BASE_DIR = os.path.dirname(__file__)
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# 🔹 Snap App Config (replace with your real values)
SNAP_APP_ID = "b56d2d6b-bb46-42b6-b838-9640c4825680"
SNAP_API_TOKEN = "eyJhbGciOiJIUzI1NiIsImtpZCI6IkNhbnZhc1MyU0hNQUNQcm9kIiwidHlwIjoiSldUIn0.eyJhdWQiOiJjYW52YXMtY2FudmFzYXBpIiwiaXNzIjoiY2FudmFzLXMyc3Rva2VuIiwibmJmIjoxNzYwMjc2OTI5LCJzdWIiOiJiNTZkMmQ2Yi1iYjQ2LTQyYjYtYjgzOC05NjQwYzQ4MjU2ODB-UFJPRFVDVElPTn5iODhhNWQ4NC1hMGFjLTQzNTctYTRiZC1kOGNkMzU1ODI4NGQifQ.kw1-YRR5gh9Dbjc1srJ4SH7rMg4enh160--8NcWjKKg"
SNAP_CONVERSION_URL = "https://tr.snapchat.com/v2/conversion"

# -------------------------------
# Load Menu
# -------------------------------
with open(MENU_FILE, encoding="utf-8") as f:
    MENU = json.load(f)

# -------------------------------
# Data Structures
# -------------------------------
user_sessions = {}
orders_lock = Lock()

if not os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

# -------------------------------
# Helper: Send Snapchat Event
# -------------------------------
def send_snap_event(event_name, user_id=None):
    """Send event to Snapchat Conversion API."""
    headers = {
        "Authorization": f"Bearer {SNAP_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "event_type": event_name,
        "timestamp": int(time.time()),
        "event_conversion_type": "WEB",
        "uuid_c1": user_id or "anonymous",
        "page_url": "https://darkkitchen.example.com",
        "app_id": SNAP_APP_ID,
    }
    try:
        r = requests.post(SNAP_CONVERSION_URL, headers=headers, data=json.dumps(payload))
        print(f"[Snap] Sent event '{event_name}' → {r.status_code}: {r.text}")
    except Exception as e:
        print(f"[Snap] Failed to send event '{event_name}':", e)

# -------------------------------
# Helper Functions
# -------------------------------
def save_order(order_data):
    with orders_lock:
        orders = []
        if os.path.exists(ORDERS_FILE):
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                orders = json.load(f)
        orders.append(order_data)
        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def format_menu():
    msg = "🍽 **Welcome to Dark Kitchen!**\nHere's our menu:\n"
    for category, items in MENU.items():
        msg += f"\n📌 *{category}*\n"
        for name, price in items.items():
            msg += f"• {name}: €{price}\n"
    msg += "\nTo order, type: order item1, item2"
    return msg

def process_order_items(user_id, items_list):
    added_items = []
    invalid_items = []
    flat_menu = {name.lower(): name for cat in MENU.values() for name in cat}
    for item in items_list:
        key = item.strip().lower()
        if key in flat_menu:
            added_items.append(flat_menu[key])
        else:
            invalid_items.append(item.strip())
    if user_id not in user_sessions:
        user_sessions[user_id] = {"items": [], "step": "name"}
    user_sessions[user_id]["items"].extend(added_items)
    return added_items, invalid_items

def json_response(message):
    return app.response_class(
        response=json.dumps({"response": message}, ensure_ascii=False, indent=2),
        status=200,
        mimetype="application/json"
    )

# -------------------------------
# Flask Routes
# -------------------------------
@app.route("/", methods=["GET"])
def home():
    return "Dark Kitchen Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    user_id = data.get("user_id")
    message = data.get("message", "").strip()

    if not user_id or not message:
        return jsonify({"error": "Missing user_id or message"}), 400

    if user_id not in user_sessions:
        user_sessions[user_id] = {"items": [], "step": "menu"}
        send_snap_event("chat_started", user_id=user_id)  # 🔹 New Chat Started Event

    session = user_sessions[user_id]

    # Step: Show Menu
    if message.lower() == "menu":
        session["step"] = "order"
        return json_response(format_menu())

    # Step: Order items
    if session["step"] == "order" and message.lower().startswith("order"):
        items = message[5:].split(",")
        added, invalid = process_order_items(user_id, items)
        session["step"] = "name"
        resp = ""
        if added:
            resp += "✅ Items added:\n" + "\n".join(f"• {i}" for i in added) + "\n"
        if invalid:
            resp += "⚠️ Not found:\n" + "\n".join(f"• {i}" for i in invalid) + "\n"
        resp += "\nPlease provide your full name:"
        send_snap_event("order_started", user_id=user_id)  # 🔹 Order Started Event
        return json_response(resp)

    # Step: Collect Name
    if session["step"] == "name":
        session["name"] = message
        session["step"] = "contact"
        return json_response(f"Thanks {message}! Please provide your contact number:")

    # Step: Collect Contact
    if session["step"] == "contact":
        session["contact"] = message
        session["step"] = "location"
        return json_response("Great! Now share your delivery address/location:")

    # Step: Collect Location
    if session["step"] == "location":
        session["location"] = message
        session["step"] = "payment"
        return json_response("Almost done! Please specify payment method (Cash on Delivery / Card):")

    # Step: Collect Payment and Complete Order
    if session["step"] == "payment":
        session["payment"] = message
        session["step"] = "completed"

        order_data = {
            "order_number": int(datetime.now().timestamp()),
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "name": session["name"],
            "contact": session["contact"],
            "location": session["location"],
            "payment": session["payment"],
            "items": session["items"]
        }
        save_order(order_data)
        user_sessions.pop(user_id)
        send_snap_event("order_completed", user_id=user_id)  # 🔹 Order Completed Event

        resp = f"🎉 Order confirmed!\n\n"
        resp += f"👤 Name: {order_data['name']}\n"
        resp += f"📞 Contact: {order_data['contact']}\n"
        resp += f"📍 Location: {order_data['location']}\n"
        resp += f"💳 Payment: {order_data['payment']}\n"
        resp += "🛒 Items:\n" + "\n".join(f"• {i}" for i in order_data["items"]) + "\n"
        resp += "\nThank you for ordering! 🙌"
        return json_response(resp)

    return json_response("⚠️ Invalid input or step. Type 'menu' to start again.")

# -------------------------------
# Dashboard Route
# -------------------------------
@app.route("/dashboard", methods=["GET"])
def dashboard():
    orders = load_orders()
    total_orders = len(orders)
    return render_template("dashboard.html", orders=orders, total_orders=total_orders)

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
