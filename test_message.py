import requests
import json

# -------------------------------
# Config
# -------------------------------
BASE_URL = "http://127.0.0.1:5000/chat"  # Local Flask endpoint

# -------------------------------
# Test Users & Messages
# -------------------------------
users = {
    "user1": [
        "menu",
        "order Cheeseburger, Fries, Ice Cream",
        "Alice Johnson",
        "+123456789",
        "10 Baker Street, Gotham",
        "Cash on Delivery"
    ],
    "user2": [
        "menu",
        "order Margherita, Pepsi, Onion Rings",
        "Bob Smith",
        "+987654321",
        "42 Wallaby Way, Sydney",
        "Card"
    ],
    "user3": [
        "menu",
        "order Veggie Burger, Water, Salad, Soda",
        "Charlie Brown",
        "+192837465",
        "221B Baker Street, London",
        "Cash on Delivery"
    ]
}

# -------------------------------
# Function to simulate chat
# -------------------------------
def send_message(user_id, message):
    payload = {"user_id": user_id, "message": message}
    response = requests.post(BASE_URL, json=payload)
    return response.json()["response"]

# -------------------------------
# Run test for each user
# -------------------------------
for user_id, messages in users.items():
    print(f"\n===== Testing session for {user_id} =====")
    for msg in messages:
        bot_response = send_message(user_id, msg)
        print(f">> User: {msg}")
        print(f">> Bot: {bot_response}")
        print("-" * 50)
