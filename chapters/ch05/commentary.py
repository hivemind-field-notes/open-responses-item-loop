# file: commentary.py
from loop import run
from scripted import ScriptedModel, answer, ask, message_item


def with_commentary(context):
    note = message_item("I will read the stored value.")
    note.update(id="msg_note", phase="commentary")
    return {"output": [note] + ask(context)["output"]}


model = ScriptedModel([with_commentary, answer])
result = run(model, max_tool_calls=1)
print(result.answer)
print("stop:", result.reason)
print("requests:", len(model.requests))
