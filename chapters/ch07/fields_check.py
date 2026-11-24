# file: fields_check.py
from fields import INPUT, INPUT_TYPES, OUTPUT, OUTPUT_TYPES, check_item

BROKEN_MSG = {
    "type": "message",
    "role": "assistant",
    "content": [
        {"type": "output_text", "text": "ok", "annotations": []},
    ],
    "status": 1,
}
BROKEN_CALL = {
    "type": "function_call",
    "id": "fc_p3_1",
    "name": "get_reading",
    "arguments": '{"pump_id": "p3"}',
    "status": "completed",
}
BROKEN_OUT = {
    "type": "function_call_output",
    "id": "fco_p3_1",
    "call_id": "call_p3_1",
    "output": {"ok": True},
    "status": "completed",
}

VALID_MSG = {
    "id": "msg_answer_p3",
    "type": "message",
    "status": "completed",
    "role": "assistant",
    "content": [
        {"type": "output_text", "text": "ok", "annotations": []},
    ],
}
VALID_CALL = {
    "id": "fc_p3_1",
    "type": "function_call",
    "call_id": "call_p3_1",
    "name": "get_reading",
    "arguments": '{"pump_id": "p3"}',
    "status": "completed",
}
VALID_OUT = {
    "id": "fco_p3_1",
    "type": "function_call_output",
    "call_id": "call_p3_1",
    "output": '{"pump_id":"p3","pressure_kpa":210}',
    "status": "completed",
}

CASES = (
    ("broken", (BROKEN_MSG, BROKEN_CALL, BROKEN_OUT)),
    ("valid", (VALID_MSG, VALID_CALL, VALID_OUT)),
)

for title, items in CASES:
    print(title)
    lines = []
    for item in items:
        keys = OUTPUT[item["type"]]
        lines.extend(
            check_item(item, keys, OUTPUT_TYPES)
        )
    if lines:
        for line in lines:
            print(line)
    else:
        print("ok")
