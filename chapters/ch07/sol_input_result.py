# file: sol_input_result.py
from fields import INPUT, INPUT_TYPES, OUTPUT, OUTPUT_TYPES, check_item


def check_client_items(items):
    lines = []
    for item in items:
        kind = item["type"]
        if kind == "function_call_output":
            req, types = INPUT[kind], INPUT_TYPES
        else:
            req, types = OUTPUT[kind], OUTPUT_TYPES
        lines.extend(check_item(item, req, types))
    return lines


valid_result = {
    "type": "function_call_output",
    "call_id": "call_p3_1",
    "output": '{"pump_id":"p3","pressure_kpa":210}',
}
missing_id_call = {
    "type": "function_call",
    "call_id": "call_p3_1",
    "name": "get_reading",
    "arguments": '{"pump_id": "p3"}',
    "status": "completed",
}
print("result:", check_client_items([valid_result]) or ["accept"])
print("call:", check_client_items([missing_id_call]) or ["accept"])
