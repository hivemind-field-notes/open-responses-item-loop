# file: error_output.py
import json

from call_items import sample_call
from parse_call import parse_call
from reading_output import get_reading


def execute_with_error(item):
    args = parse_call(item)
    try:
        reading = get_reading(args["pump_id"])
    except ValueError as error:
        payload = {"ok": False, "error": str(error)}
    else:
        payload = {"ok": True, "reading": reading}
    return {
        "type": "function_call_output",
        "call_id": item["call_id"],
        "output": json.dumps(payload, separators=(",", ":")),
        "status": "completed",
    }


call = sample_call()
call["arguments"] = json.dumps({"pump_id": "p9"})
result = execute_with_error(call)
assert result["call_id"] == call["call_id"]
assert result["status"] == "completed"
print(result["status"])
print(result["output"])
