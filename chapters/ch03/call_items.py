# file: call_items.py
import json


def sample_call():
    return {
        "type": "function_call",
        "id": "fc_p3_1",
        "call_id": "call_p3_1",
        "name": "get_reading",
        "arguments": json.dumps(
            {"pump_id": "p3"}, separators=(",", ":")
        ),
        "status": "completed",
    }


if __name__ == "__main__":
    print(json.dumps(sample_call(), indent=2))
