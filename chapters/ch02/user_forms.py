# file: user_forms.py
import json


def user_message(content):
    return {
        "type": "message",
        "role": "user",
        "content": content,
    }


if __name__ == "__main__":
    sentence = "What is the pressure at pump p3?"
    as_string = user_message(sentence)
    as_parts = user_message([
        {"type": "input_text", "text": sentence},
    ])
    print(json.dumps(as_string, indent=2))
    print(json.dumps(as_parts, indent=2))
