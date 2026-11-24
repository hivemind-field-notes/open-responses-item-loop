# file: pump.py
from loop import run
from scripted import ScriptedModel, answer, ask


model = ScriptedModel([ask, answer])
result = run(model, max_tool_calls=1)
print(result.answer)
print("stop:", result.reason)
print("requests:", len(model.requests))
print("tool calls:", result.tool_calls)
