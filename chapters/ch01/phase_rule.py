# file: phase_rule.py
from stop_rule import ends_task


def ends_final_answer(item):
    return ends_task(item) and item.get("phase") == "final_answer"


for phase in ("commentary", "final_answer"):
    item = {
        "type": "message",
        "id": "msg_" + phase,
        "status": "completed",
        "role": "assistant",
        "phase": phase,
        "content": [
            {
                "type": "output_text",
                "text": "Pump p3 pressure is 210 kPa.",
                "annotations": [],
            }
        ],
    }
    print(phase, ends_final_answer(item))
