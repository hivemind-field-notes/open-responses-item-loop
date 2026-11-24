# file: read_messages.py
import json

from assistant_message import assistant_text
from guidance_refusal import developer_message, refusal_message


ALLOWED = {
    "user": {"input_text"},
    "system": {"input_text"},
    "developer": {"input_text"},
    "assistant": {"output_text", "refusal"},
}


def inspect_message(item):
    if not isinstance(item, dict) or item.get("type") != "message":
        raise ValueError("expected a message object")
    role = item.get("role")
    if not isinstance(role, str) or role not in ALLOWED:
        raise ValueError("unsupported role")
    phase = item.get("phase", "-")
    if "phase" in item:
        if role != "assistant":
            raise ValueError("phase belongs to assistant messages")
        if phase not in ("commentary", "final_answer"):
            raise ValueError("unsupported phase")
    content = item.get("content")
    if not isinstance(content, list):
        raise ValueError("this reader expects a content array")
    rows = []
    for part in content:
        if not isinstance(part, dict):
            raise ValueError("expected a content-part object")
        kind = part.get("type")
        if not isinstance(kind, str) or kind not in ALLOWED[role]:
            raise ValueError(f"{role} cannot carry {kind}")
        field = "refusal" if kind == "refusal" else "text"
        if not isinstance(part.get(field), str):
            raise ValueError(f"{kind} requires a {field} string")
        if kind == "output_text":
            if not isinstance(part.get("annotations"), list):
                raise ValueError("output_text requires annotations")
        rows.append((role, kind, phase))
    return rows


if __name__ == "__main__":
    messages = [
        assistant_text("msg_p3_answer", "Pressure is 210 kPa."),
        developer_message(),
        refusal_message(),
    ]
    restored = json.loads(json.dumps(messages))
    for message in restored:
        for row in inspect_message(message):
            print(*row)
    bad = {
        "type": "message",
        "role": "user",
        "content": [
            {
                "type": "output_text",
                "text": "Pressure is 210 kPa.",
                "annotations": [],
            }
        ],
    }
    try:
        inspect_message(bad)
    except ValueError as error:
        print("rejected:", error)
