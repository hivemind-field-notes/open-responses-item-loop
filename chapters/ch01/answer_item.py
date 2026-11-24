# file: answer_item.py
import json

item = {
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
}
print(json.dumps(item, indent=2))
