# file: request.py
import json
from copy import deepcopy


TOOL = {
    "type": "function",
    "name": "get_reading",
    "description": "Read a pump's stored reading.",
    "parameters": {
        "type": "object",
        "properties": {"pump_id": {"type": "string"}},
        "required": ["pump_id"],
        "additionalProperties": False,
    },
    "strict": True,
}

QUESTION = {
    "type": "message",
    "role": "user",
    "content": [
        {"type": "input_text", "text": "What is the pressure reading for pump p3?"}
    ],
}


def make_request(items=None, previous=None):
    body = {
        "model": "offline-pump",
        "instructions": "Use get_reading. Report the stored reading.",
        "input": deepcopy([QUESTION] if items is None else items),
        "tools": [deepcopy(TOOL)],
        "tool_choice": "auto",
        "stream": True,
    }
    if previous is not None:
        body["previous_response_id"] = previous
    return body


if __name__ == "__main__":
    print(json.dumps(make_request(), indent=2))
