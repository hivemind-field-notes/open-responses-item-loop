# file: multiline.py
import json

from fold import fold
from message_stream import message_frames, message_stream
from sse import parse_sse


lines = []
for frame in message_frames():
    lines.append(": local fixture")
    lines.append("event: " + frame["type"])
    for line in json.dumps(frame, indent=2).splitlines():
        lines.append("data: " + line)
    lines.append("")
wire = "\r\n".join(lines) + "\r\n"
actual = fold(parse_sse(wire))
expected = fold(parse_sse(message_stream()))
print("same response:", actual == expected)
