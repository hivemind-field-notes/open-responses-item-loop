# file: choice_demo.py
from scripted_model import scripted_model
from tool_request import request_fields


def make_request(choice, text="Read p3."):
    return {
        "model": "offline-pump",
        "input": [{
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": text}],
        }],
        **request_fields(choice),
    }


if __name__ == "__main__":
    choices = [
        ("auto", "auto"),
        ("required", "required"),
        ("none", "none"),
        ("named", {"type": "function", "name": "get_reading"}),
    ]
    for label, choice in choices:
        items = scripted_model(make_request(choice))
        has_call = any(i["type"] == "function_call" for i in items)
        print(f"{label}: function_call={has_call}")
