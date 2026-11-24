# file: scripted.py
import json
from copy import deepcopy


def call_item():
    return {
        "type": "function_call",
        "id": "fc_p3_1",
        "status": "completed",
        "call_id": "call_p3_1",
        "name": "get_reading",
        "arguments": '{"pump_id":"p3"}',
    }


def message_item(text):
    return {
        "type": "message",
        "id": "msg_answer_p3",
        "role": "assistant",
        "status": "completed",
        "phase": "final_answer",
        "content": [
            {"type": "output_text", "text": text, "annotations": []}
        ],
    }


def snapshot(body, number, fields):
    response = {
        "id": f"resp_{number}",
        "object": "response",
        "created_at": 0,
        "completed_at": None,
        "status": "completed",
        "incomplete_details": None,
        "model": body["model"],
        "previous_response_id": body.get("previous_response_id"),
        "instructions": body["instructions"],
        "output": [],
        "error": None,
        "tools": deepcopy(body["tools"]),
        "tool_choice": body["tool_choice"],
        "truncation": "disabled",
        "parallel_tool_calls": True,
        "text": {"format": {"type": "text"}},
        "top_p": 1,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "top_logprobs": 0,
        "temperature": 1,
        "reasoning": None,
        "usage": None,
        "max_output_tokens": None,
        "max_tool_calls": body.get("max_tool_calls"),
        "store": True,
        "background": False,
        "service_tier": "default",
        "metadata": {},
        "safety_identifier": None,
        "prompt_cache_key": None,
    }
    response.update(deepcopy(fields))
    if response["status"] == "completed":
        response["completed_at"] = 0
    return response


class ScriptedModel:
    def __init__(self, turns):
        self.turns = list(turns)
        self.requests = []
        self.contexts = {}

    def create(self, body):
        number = len(self.requests) + 1
        if number > len(self.turns):
            raise ValueError("script exhausted")
        previous = body.get("previous_response_id")
        if previous is None:
            context = []
        else:
            context = deepcopy(self.contexts[previous])
        context.extend(deepcopy(body["input"]))
        fields = self.turns[number - 1](deepcopy(context))
        response = snapshot(body, number, fields)
        self.requests.append(deepcopy(body))
        context.extend(deepcopy(response["output"]))
        self.contexts[response["id"]] = context
        return response


def ask(context):
    return {"output": [call_item()]}


def answer(context):
    call, result = context[-2:]
    if call["type"] != "function_call":
        raise ValueError("missing function_call")
    if result["type"] != "function_call_output":
        raise ValueError("missing function_call_output")
    if result["call_id"] != call["call_id"]:
        raise ValueError("call_id mismatch")
    data = json.loads(result["output"])
    text = f"Pump {data['pump_id']} pressure is {data['pressure_kpa']} kPa."
    return {"output": [message_item(text)]}
