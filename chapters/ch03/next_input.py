# file: next_input.py
from call_items import sample_call
from reading_output import execute_call
from tool_request import request_fields


user = {
    "type": "message",
    "role": "user",
    "content": [{"type": "input_text", "text": "Read p3."}],
}
call = sample_call()
result = execute_call(call)
request = {
    "model": "offline-pump",
    "input": [user, call, result],
    **request_fields(),
}
for item in request["input"]:
    print(item["type"], item.get("call_id", "-"))
