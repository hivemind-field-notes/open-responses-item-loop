# file: run_budget.py
from loop import run
from scripted import ScriptedModel, answer, ask, call_item


def again(context):
    item = call_item()
    item.update(id="fc_2", call_id="call_2")
    return {"output": [item]}


model = ScriptedModel([ask, again, answer])
result = run(model, max_tool_calls=1)
print("stop:", result.reason)
print("requests:", len(model.requests))
print("tool calls:", result.tool_calls)
