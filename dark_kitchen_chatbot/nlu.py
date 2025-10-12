# Lightweight intent detection using keywords
def detect_intent(text):
    text = text.lower()
    if any(word in text for word in ["order", "want", "add", "get"]):
        return "order_food"
    elif any(word in text for word in ["cancel", "remove"]):
        return "cancel_order"
    elif any(word in text for word in ["change", "edit"]):
        return "edit_order"
    elif any(word in text for word in ["hi", "hello", "hey"]):
        return "greet"
    elif any(word in text for word in ["yes"]):
        return "yes"
    elif any(word in text for word in ["no"]):
        return "no"
    else:
        return "unknown"
