# file: continue_demo.py
import json

from local_tools import dispatch
from request import make_request
from scripted import ScriptedModel, answer, ask


model = ScriptedModel([ask, answer])
first = model.create(make_request())
results = [dispatch(item) for item in first["output"]]
second = make_request(results, previous=first["id"])
print("previous_response_id:", second["previous_response_id"])
print(json.dumps(second["input"], indent=2))
response = model.create(second)
print(response["output"][0]["content"][0]["text"])
