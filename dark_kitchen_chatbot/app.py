import os
import json
import socket
from flask import Flask, request, jsonify
from datetime import datetime
from threading import Lock

app = Flask(__name__)

# -------------------------------
# Configuration
# -------------------------------
BASE_DIR = os.path.dirname(__file__)
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# -------------------------------
# Function to find a free port
# -------------------------------
def get_free_port(default_port=5000):
    """Return a free port, fallback to default_port if all fails."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("", 0))
        free_port = sock.getsockname()[1]
        sock.close()
        return free_port or default_port
    except:
        return default_port

# Dynamic port: Railway or fallback to free port
PORT = int(os.environ.get("PORT", get_free_port()))
HOST = "0.0.0.0"

# -------------------------------
# Load Menu
# -------------------------------
with open(MENU_FILE, "r", encoding="utf-8") as f:
    MENU = json.load(f)

# -------------------------------
# Data Structures
# -------------------------------
user_sessions = {}  # store ongoing sessions per user_id
orders_lock = Lock()  # thread-safe file writes

# Ensure orders.json exists
if not os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

# -------------------------------
# Helper Functions
# -------------------------------
def save_order(order_data):
    with orders_lock:
        orders = []
        if os.path.exists(ORDERS_FILE):
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                try:
                    orders = json.load(f)
                except json.JSONDecodeError:
                    orders = []
        orders.append(order_data)
        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(orders, f, indent=2)

def format_menu():
    msg = "🍽 **Welcome to Dark Kitchen!**\nHere's our menu:\n"
    for category, items in MENU.items():
        msg += f"\n📌 *{category}*\n"
        for name, price in items.items():
            msg += f"• {name}: ${price}\n"
    msg += "\nTo order, type: `order item1, item2`"
    return msg

def process_order_items(user_id, items_list):
    added_items, invalid_items = [], []
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

    session = user_sessions[user_id]

    # Step 1: Show menu
    if message.lower() == "menu":
        session["step"] = "order"
        return jsonify({"response": format_menu()})

    # Step 2: Add items
    if session["step"] == "order" and message.lower().startswith("order"):
        items = message[5:].split(",")
        added, invalid = process_order_items(user_id, items)
        session["step"] = "name"
        resp = ""
        if added:
            resp += "✅ Items added:\n" + "\n".join(f"• {i}" for i in added) + "\n"
        if invalid:
            resp += "⚠️ Items not found:\n" + "\n".join(f"• {i}" for i in invalid) + "\n"
        resp += "\nPlease provide your full name:"
        return jsonify({"response": resp})

    # Step 3: Name
    if session["step"] == "name":
        session["name"] = message
        session["step"] = "contact"
        return jsonify({"response": f"Thanks {message}! Please provide your contact number:"})

    # Step 4: Contact
    if session["step"] == "contact":
        session["contact"] = message
        session["step"] = "location"
        return jsonify({"response": "Great! Now share your delivery address/location:"})

    # Step 5: Location
    if session["step"] == "location":
        session["location"] = message
        session["step"] = "payment"
        return jsonify({"response": "Almost done! Specify payment method (Cash on Delivery / Card):"})

    # Step 6: Payment & Complete
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

        resp = (
            f"🎉 Your order is confirmed!\n\n"
            f"👤 Name: {order_data['name']}\n"
            f"📞 Contact: {order_data['contact']}\n"
            f"📍 Location: {order_data['location']}\n"
            f"💳 Payment: {order_data['payment']}\n"
            "🛒 Items:\n" + "\n".join(f"• {i}" for i in order_data["items"]) + "\n"
            "\nThank you for ordering! 🙌"
        )
        return jsonify({"response": resp})

    return jsonify({"response": "⚠️ Invalid input or step. Type 'menu' to start again."})

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    print(f"🔹 Starting Dark Kitchen Bot on {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=False)
