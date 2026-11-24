# file: run_pump.py
import json

from scripted_model import QUESTION, scripted_model
from stop_rule import ends_task


def get_reading(pump_id):
    if pump_id != "p3":
        raise ValueError("unknown pump")
    return {"pump_id": pump_id, "pressure_kpa": 210}


def main():
    history = [
        {
            "type": "message",
            "id": "msg_user_p3",
            "status": "completed",
            "role": "user",
            "content": [{"type": "input_text", "text": QUESTION}],
        }
    ]
    for turn in range(1, 4):
        item = scripted_model(history)
        history.append(item)
        print(f"turn {turn}: {item['type']} {item['status']}")
        if ends_task(item):
            for part in item["content"]:
                if part["type"] == "output_text":
                    print(part["text"])
            print("stop")
            return
        if item["type"] != "function_call":
            raise ValueError("unexpected scripted item")
        if item["status"] != "completed":
            raise ValueError("function call is not complete")
        if item["name"] != "get_reading":
            raise ValueError("unknown tool")
        arguments = json.loads(item["arguments"])
        reading = get_reading(**arguments)
        result = {
            "type": "function_call_output",
            "id": "fco_p3_1",
            "status": "completed",
            "call_id": item["call_id"],
            "output": json.dumps(reading),
        }
        history.append(result)
        print("tool result:", result["call_id"])
    raise RuntimeError("script exceeded the turn limit")


if __name__ == "__main__":
    main()
