# file: reading_output.py
import json

from call_items import sample_call
from parse_call import parse_call


READINGS = {"p3": "p3: pressure=210 kPa"}


def get_reading(pump_id):
    if pump_id not in READINGS:
        raise ValueError("unknown pump")
    return READINGS[pump_id]


def execute_call(item):
    args = parse_call(item)
    reading = get_reading(args["pump_id"])
    return {
        "type": "function_call_output",
        "call_id": item["call_id"],
        "output": reading,
        "status": "completed",
    }


if __name__ == "__main__":
    print(json.dumps(execute_call(sample_call()), indent=2))
