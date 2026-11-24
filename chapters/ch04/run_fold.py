# file: run_fold.py
import json

from call_stream import call_stream
from fold import fold
from message_stream import message_stream
from sse import parse_sse


for label, make_stream in [
    ("message", message_stream),
    ("function_call", call_stream),
]:
    print(label)
    response = fold(parse_sse(make_stream()), trace=True)
    print("output:")
    print(json.dumps(response["output"], indent=2))
    print("status:", response["status"])
