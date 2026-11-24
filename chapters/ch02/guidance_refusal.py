# file: guidance_refusal.py
import json


def developer_message():
    return {
        "type": "message",
        "role": "developer",
        "content": [
            {
                "type": "input_text",
                "text": "Report readings; do not change controls.",
            }
        ],
    }


def refusal_message():
    return {
        "type": "message",
        "id": "msg_p3_refusal",
        "status": "completed",
        "role": "assistant",
        "content": [
            {
                "type": "refusal",
                "refusal": "I cannot disable the pressure interlock.",
            }
        ],
    }


if __name__ == "__main__":
    print(json.dumps(developer_message(), indent=2))
    print(json.dumps(refusal_message(), indent=2))
