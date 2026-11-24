# file: assistant_message.py
import json


def assistant_text(item_id, text):
    return {
        "type": "message",
        "id": item_id,
        "status": "completed",
        "role": "assistant",
        "content": [
            {
                "type": "output_text",
                "text": text,
                "annotations": [],
            }
        ],
    }


if __name__ == "__main__":
    message = assistant_text(
        "msg_p3_answer",
        "The pressure at pump p3 is 210 kPa.",
    )
    print(json.dumps(message, indent=2))
