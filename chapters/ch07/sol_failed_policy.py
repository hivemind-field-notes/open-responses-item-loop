# file: sol_failed_policy.py
from fields import OUTPUT, OUTPUT_TYPES, STATUSES, check_item


EXTENDED_STATUSES = (*STATUSES, "failed")


def check_failed_policy(items):
    lines = []
    for i, item in enumerate(items):
        status = item.get("status")
        if status not in EXTENDED_STATUSES:
            lines.extend(check_item(item, OUTPUT[item["type"]], OUTPUT_TYPES))
        if status == "failed" and i != len(items) - 1:
            lines.append(f"{item['id']} failed is not last")
    lines.append("policy: failed is terminal and must be last")
    return lines


items = [
    {
        "id": "fc_p3_1",
        "type": "function_call",
        "call_id": "call_p3_1",
        "name": "get_reading",
        "arguments": '{"pump_id": "p3"}',
        "status": "failed",
    },
    {
        "id": "msg_answer_p3",
        "type": "message",
        "status": "completed",
        "role": "assistant",
        "content": [{
            "type": "output_text",
            "text": "Pump p3 pressure is 210 kPa.",
            "annotations": [],
        }],
    },
]
for line in check_failed_policy(items):
    print(line)
