# file: display_refusal.py
from assistant_message import assistant_text
from guidance_refusal import refusal_message
from read_messages import inspect_message


def display(item):
    inspect_message(item)
    if item["role"] != "assistant":
        raise ValueError("display expects an assistant message")
    for part in item["content"]:
        if part["type"] == "refusal":
            print("REFUSAL:", part["refusal"])
        else:
            print("TEXT:", part["text"])


words = "I cannot disable the pressure interlock."
display(assistant_text("msg_plain", words))
display(refusal_message())
