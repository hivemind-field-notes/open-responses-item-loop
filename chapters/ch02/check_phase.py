# file: check_phase.py
from assistant_message import assistant_text
from read_messages import inspect_message
from user_forms import user_message


items = [
    user_message([{"type": "input_text", "text": "Read p3."}]),
    assistant_text("msg_p3_phase", "Checking the reading."),
]
for item in items:
    item["phase"] = "commentary"
    try:
        rows = inspect_message(item)
    except ValueError as error:
        print("rejected:", error)
    else:
        print("accepted:", rows[0][2])
