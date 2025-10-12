import os
import json
from flask import Flask, request, jsonify
from datetime import datetime
from threading import Lock

app = Flask(__name__)

# -------------------------------
# Configuration
# -------------------------------
MENU_FILE = os.path.join(os.path.dirname(__file__), "menu.json")
ORDERS_FILE = os.path.join(os.path.dirname(__file__), "orders.json")

# Flask secret key for sessions
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey123")  # fallback for local dev

# Port for Railway deployment
PORT = int(os.getenv("PORT", 5000))
HOST = "0.0.0.0"

# -------------------------------
# Load Menu
# -------------------------------
with open(MENU_FILE) as f:
    MENU = json.load(f)

# -------------------------------
# Data Structures
# -------------------------------
user_sessions = {}  # store ongoing sessions per user_id
orders_lock = Lock()  # for thread-safe writing

# Ensure orders.json exists
if not os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "w") as f:
        json.dump([], f)

# -------------------------------
# Helper Functions
# -------------------------------
def save_order(order_data):
    with orders_lock:
        with open(ORDERS_FILE, "r") as f:
            orders = json.load(f)
        orders.append(order_data)
        with open(ORDERS_FILE, "w") as f:
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

    # Initialize session
    if user_id not in user_sessions:
        user_sessions[user_id] = {"items": [], "step": "menu"}

    session = user_sessions[user_id]

    # --- Step: Menu ---
    if message.lower() == "menu":
        session["step"] = "order"
        return jsonify({"response": format_menu()})

    # --- Step: Ordering ---
    if session["step"] == "order" and message.lower().startswith("order"):
        items = message[5:].split(",")
        added, invalid = process_order_items(user_id, items)
        session["step"] = "name"
        resp = ""
        if added:
            resp += "✅ Items added to your order:\n" + "\n".join(f"• {i}" for i in added) + "\n"
        if invalid:
            resp += "⚠️ These items were not found:\n" + "\n".join(f"• {i}" for i in invalid) + "\n"
        resp += "\nPlease provide your full name:"
        return jsonify({"response": resp})

    # --- Step: Name ---
    if session["step"] == "name":
        session["name"] = message
        session["step"] = "contact"
        return jsonify({"response": f"Thanks {message}! Please provide your contact number:"})

    # --- Step: Contact ---
    if session["step"] == "contact":
        session["contact"] = message
        session["step"] = "location"
        return jsonify({"response": "Great! Now share your delivery address/location:"})

    # --- Step: Location ---
    if session["step"] == "location":
        session["location"] = message
        session["step"] = "payment"
        return jsonify({"response": "Almost done! Please specify payment method (Cash on Delivery / Card):"})

    # --- Step: Payment ---
    if session["step"] == "payment":
        session["payment"] = message
        session["step"] = "completed"

        # Save order
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

        # Clear session
        user_sessions.pop(user_id)

        resp = f"🎉 Your order is confirmed!\n\n"
        resp += f"👤 Name: {order_data['name']}\n"
        resp += f"📞 Contact: {order_data['contact']}\n"
        resp += f"📍 Location: {order_data['location']}\n"
        resp += f"💳 Payment: {order_data['payment']}\n"
        resp += "🛒 Items:\n" + "\n".join(f"• {i}" for i in order_data["items"]) + "\n"
        resp += "\nThank you for ordering! 🙌"
        return jsonify({"response": resp})

    return jsonify({"response": "⚠️ Invalid input or step. Type 'menu' to start again."})

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
