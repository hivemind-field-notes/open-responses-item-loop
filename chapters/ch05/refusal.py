# file: refusal.py
from loop import run
from scripted import ScriptedModel, call_item, message_item


def refuse(context):
    item = message_item("")
    item["content"] = [
        {"type": "refusal", "refusal": "No reading is available."}
    ]
    return {"output": [call_item(), item]}


model = ScriptedModel([refuse])
result = run(model)
print("stop:", result.reason)
print("detail:", result.detail)
print("tool calls:", result.tool_calls)
