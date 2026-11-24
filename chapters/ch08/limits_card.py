# file: limits_card.py
import json
import re

name = "get_reading"
call_id = "call_p3_1"
arguments = json.dumps({"pump_id": "p3"})

if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", name):
    raise ValueError("bad function name")
if not 1 <= len(call_id) <= 64:
    raise ValueError("bad call_id")

decoded = json.loads(arguments)
choice = {"type": "function", "name": name}

print(arguments)
print(decoded["pump_id"])
print(json.dumps(choice))
