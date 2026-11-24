# file: split_input.py
from read_messages import inspect_message
from user_forms import user_message


message = user_message([
    {"type": "input_text", "text": "Use the local reading."},
    {"type": "input_text", "text": "Report its pressure."},
])
for row in inspect_message(message):
    print(*row)
