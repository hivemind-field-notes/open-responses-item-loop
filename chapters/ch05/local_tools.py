# file: local_tools.py
import json


READINGS = {"p3": '{"pump_id":"p3","pressure_kpa":210}'}


def get_reading(pump_id):
    if type(pump_id) is not str or pump_id not in READINGS:
        raise ValueError("unknown pump")
    return READINGS[pump_id]


TOOLS = {"get_reading": get_reading}


def dispatch(item):
    if item["type"] != "function_call":
        raise ValueError("expected function_call")
    if item["status"] != "completed":
        raise ValueError("unfinished function_call")
    call_id = item["call_id"]
    if type(call_id) is not str or not 1 <= len(call_id) <= 64:
        raise ValueError("invalid call_id")
    name = item["name"]
    if name not in TOOLS:
        raise ValueError("unknown tool")
    arguments = json.loads(item["arguments"])
    if type(arguments) is not dict:
        raise ValueError("arguments must be an object")
    if set(arguments) != {"pump_id"}:
        raise ValueError("expected only pump_id")
    value = TOOLS[name](**arguments)
    return {
        "type": "function_call_output",
        "call_id": call_id,
        "output": value,
    }


if __name__ == "__main__":
    call = {
        "type": "function_call",
        "id": "fc_p3_1",
        "status": "completed",
        "call_id": "call_p3_1",
        "name": "get_reading",
        "arguments": '{"pump_id":"p3"}',
    }
    print(json.dumps(dispatch(call), sort_keys=True))
