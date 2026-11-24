# file: scripted_model.py
import json

QUESTION = "What is the pressure reading for pump p3?"
READING = {"pump_id": "p3", "pressure_kpa": 210}

SCRIPT = (
    {
        "type": "function_call",
        "id": "fc_p3_1",
        "status": "completed",
        "call_id": "call_p3_1",
        "name": "get_reading",
        "arguments": json.dumps({"pump_id": "p3"}),
    },
    {
        "type": "message",
        "id": "msg_answer_p3",
        "status": "completed",
        "role": "assistant",
        "phase": "final_answer",
        "content": [
            {
                "type": "output_text",
                "text": "Pump p3 pressure is 210 kPa.",
                "annotations": [],
            }
        ],
    },
)


def scripted_model(input_items):
    if not input_items:
        raise ValueError("missing user item")
    user = input_items[0]
    expected = [{"type": "input_text", "text": QUESTION}]
    if (
        user.get("type") != "message"
        or user.get("role") != "user"
        or user.get("content") != expected
    ):
        raise ValueError("this script expects the pump p3 question")

    if len(input_items) == 1:
        return json.loads(json.dumps(SCRIPT[0]))
    if len(input_items) != 3 or input_items[1] != SCRIPT[0]:
        raise ValueError("expected user, function call, tool result")

    result = input_items[2]
    if (
        result.get("type") != "function_call_output"
        or result.get("call_id") != "call_p3_1"
        or result.get("status") != "completed"
    ):
        raise ValueError("tool result does not match call_p3_1")
    if json.loads(result["output"]) != READING:
        raise ValueError("tool result differs from the fixed reading")
    return json.loads(json.dumps(SCRIPT[1]))
