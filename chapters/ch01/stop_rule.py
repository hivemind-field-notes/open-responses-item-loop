# file: stop_rule.py

def ends_task(item):
    return (
        item.get("type") == "message"
        and item.get("role") == "assistant"
        and item.get("status") == "completed"
        and any(
            part.get("type") == "output_text"
            for part in item.get("content", [])
        )
    )


if __name__ == "__main__":
    for status in ("in_progress", "incomplete", "completed"):
        item = {
            "type": "message",
            "id": "msg_probe",
            "status": status,
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
        print(status, ends_task(item))
