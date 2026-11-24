# file: tool_request.py
import json


def request_fields(tool_choice="auto"):
    return {
        "tools": [{
            "type": "function",
            "name": "get_reading",
            "description": "Read a pump from the local fixture.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pump_id": {"type": "string"},
                },
                "required": ["pump_id"],
                "additionalProperties": False,
            },
            "strict": True,
        }],
        "tool_choice": tool_choice,
    }


if __name__ == "__main__":
    print(json.dumps(request_fields(), indent=2))
