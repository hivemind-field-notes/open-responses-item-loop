# file: call_snapshots.py
from call_items import sample_call


finished = sample_call()
started = {
    **finished,
    "arguments": "",
    "status": "in_progress",
}
print("added:", started["status"], repr(started["arguments"]))
print("done:", finished["status"], repr(finished["arguments"]))
