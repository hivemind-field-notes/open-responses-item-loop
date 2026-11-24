# file: user_item.py
import json

item = {
    "type": "message",
    "id": "msg_user_p3",
    "status": "completed",
    "role": "user",
    "content": [
        {
            "type": "input_text",
            "text": "What is the pressure reading for pump p3?",
        }
    ],
}
print(json.dumps(item, indent=2))
