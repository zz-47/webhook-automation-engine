# dark_kitchen_chatbot/app.py
import json
import os
import threading
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# -------------------------------
# File paths
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDER_LOG_FILE = os.path.join(BASE_DIR, "orders_log.json")

# -------------------------------
# Global state
# -------------------------------
with open(MENU_FILE) as f:
    MENU = json.load(f)

# Sessions per user_id
sessions = {}
ORDER_LOCK = threading.Lock()
GLOBAL_ORDER_NUMBER = 0

# Load previous orders if exists
if os.path.exists(ORDER_LOG_FILE):
    with open(ORDER_LOG_FILE) as f:
        ORDERS_LOG = json.load(f)
else:
    ORDERS_LOG = []

# -------------------------------
# Helper functions
# -------------------------------
def format_menu():
    text = "🍽 **Welcome to Dark Kitchen!**\nHere's our menu:\n\n"
    for category, items in MENU.items():
        text += f"📌 *{category}*\n"
        for item, price in items.items():
            text += f"• {item}: ${price:.2f}\n"
        text += "\n"
    text += "To order, type: `order item1, item2`"
    return text

def format_order(order):
    text = "🛒 Items in your order:\n"
    for item in order:
        text += f"• {item}\n"
    return text

def log_order(order_data):
    ORDERS_LOG.append(order_data)
    with open(ORDER_LOG_FILE, "w") as f:
        json.dump(ORDERS_LOG, f, indent=2)

# -------------------------------
# Main chat endpoint
# -------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    global GLOBAL_ORDER_NUMBER
    data = request.json
    user_id = data.get("user_id")
    message = data.get("message", "").strip()

    # Initialize session if new user
    if user_id not in sessions or message.lower() == "menu":
        sessions[user_id] = {
            "step": "menu",
            "order": [],
            "name": "",
            "contact": "",
            "location": "",
            "payment": ""
        }

    session = sessions[user_id]
    step = session["step"]
    response = ""

    # -------------------------------
    # Step 1: Show menu
    # -------------------------------
    if step == "menu":
        response = format_menu()
        session["step"] = "ordering"

    # -------------------------------
    # Step 2: Take order
    # -------------------------------
    elif step == "ordering":
        if message.lower().startswith("order"):
            items = [i.strip().title() for i in message[5:].split(",")]
            valid_items = []
            invalid_items = []
            for item in items:
                if any(item in category for category in MENU.values()):
                    valid_items.append(item)
                else:
                    invalid_items.append(item)
            session["order"].extend(valid_items)

            response += "✅ Items added to your order:\n"
            for i in valid_items:
                response += f"• {i}\n"

            if invalid_items:
                response += "\n⚠️ These items were not found:\n"
                for i in invalid_items:
                    response += f"• {i}\n"
            response += "\nPlease provide your full name:"
            session["step"] = "name"
        else:
            response = "Please type your order starting with `order item1, item2`"

    # -------------------------------
    # Step 3: Collect name
    # -------------------------------
    elif step == "name":
        session["name"] = message
        response = f"Thanks {message}! Please provide your contact number:"
        session["step"] = "contact"

    # -------------------------------
    # Step 4: Collect contact
    # -------------------------------
    elif step == "contact":
        session["contact"] = message
        response = "Great! Now share your delivery address/location:"
        session["step"] = "location"

    # -------------------------------
    # Step 5: Collect location
    # -------------------------------
    elif step == "location":
        session["location"] = message
        response = "Almost done! Please specify payment method (Cash on Delivery / Card):"
        session["step"] = "payment"

    # -------------------------------
    # Step 6: Collect payment and confirm
    # -------------------------------
    elif step == "payment":
        session["payment"] = message
        # Increment global order number safely
        with ORDER_LOCK:
            GLOBAL_ORDER_NUMBER += 1
            order_number = GLOBAL_ORDER_NUMBER

        # Log order
        order_data = {
            "order_number": order_number,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "name": session["name"],
            "contact": session["contact"],
            "location": session["location"],
            "payment": session["payment"],
            "items": session["order"]
        }
        log_order(order_data)

        # Respond to user
        response = f"🎉 Your order #{order_number} is confirmed!\n\n"
        response += f"👤 Name: {session['name']}\n"
        response += f"📞 Contact: {session['contact']}\n"
        response += f"📍 Location: {session['location']}\n"
        response += f"💳 Payment: {session['payment']}\n"
        response += "🛒 Items:\n"
        for i in session["order"]:
            response += f"• {i}\n"
        response += "\nThank you for ordering! 🙌"

        # Reset session for next order
        sessions[user_id] = {"step": "menu", "order": [], "name": "", "contact": "", "location": "", "payment": ""}

    else:
        response = "Sorry, I didn't understand that."

    return jsonify({"response": response})

# -------------------------------
# Run Flask app
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
