# file: pump_model.py
from copy import deepcopy

from transcript import encode


TOOL = {
    "type": "function",
    "name": "get_reading",
    "description": "Read a local pump fixture.",
    "parameters": {
        "type": "object",
        "properties": {"pump_id": {"type": "string"}},
        "required": ["pump_id"],
        "additionalProperties": False,
    },
    "strict": True,
}
USER = {
    "type": "message",
    "role": "user",
    "content": [{
        "type": "input_text",
        "text": "What is the pressure reading for pump p3?",
    }],
}
CALL = {
    "type": "function_call",
    "id": "fc_p3_1",
    "call_id": "call_p3_1",
    "name": "get_reading",
    "arguments": encode({"pump_id": "p3"}),
    "status": "completed",
}
READING = {"pump_id": "p3", "pressure_kpa": 210}
RESULT = {
    "type": "function_call_output",
    "call_id": "call_p3_1",
    "output": encode(READING),
}
FINAL = {
    "type": "message",
    "id": "msg_answer_p3",
    "role": "assistant",
    "status": "completed",
    "phase": "final_answer",
    "content": [{
        "type": "output_text",
        "text": "Pump p3 pressure is 210 kPa.",
        "annotations": [],
    }],
}


def make_turn(response_id, item):
    def snapshot(status, output):
        return {
            "id": response_id,
            "object": "response",
            "created_at": 0,
            "completed_at": 1 if status == "completed" else None,
            "status": status,
            "incomplete_details": None,
            "model": "offline-pump",
            "previous_response_id": None,
            "instructions": None,
            "output": output,
            "error": None,
            "tools": [TOOL],
            "tool_choice": "auto",
            "truncation": "disabled",
            "parallel_tool_calls": False,
            "text": {"format": {"type": "text"}},
            "top_p": 1,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "top_logprobs": 0,
            "temperature": 1,
            "reasoning": None,
            "usage": None,
            "max_output_tokens": None,
            "max_tool_calls": None,
            "store": False,
            "background": False,
            "service_tier": "default",
            "metadata": {},
            "safety_identifier": None,
            "prompt_cache_key": None,
        }

    events = []

    def emit(kind, **fields):
        events.append({
            "type": "response." + kind,
            "sequence_number": len(events),
            **deepcopy(fields),
        })

    initial = snapshot("in_progress", [])
    emit("created", response=initial)
    emit("in_progress", response=initial)
    started = deepcopy(item)
    started["status"] = "in_progress"
    if item["type"] == "function_call":
        started["arguments"] = ""
    else:
        started["content"] = []
    emit("output_item.added", output_index=0, item=started)
    location = {"item_id": item["id"], "output_index": 0}
    if item["type"] == "function_call":
        emit("function_call_arguments.delta", **location,
             delta=item["arguments"])
        emit("function_call_arguments.done", **location,
             arguments=item["arguments"])
    else:
        location["content_index"] = 0
        part = item["content"][0]
        blank = {"type": "output_text", "text": "", "annotations": []}
        emit("content_part.added", **location, part=blank)
        emit("output_text.delta", **location, delta=part["text"])
        emit("output_text.done", **location, text=part["text"])
        emit("content_part.done", **location, part=part)
    emit("output_item.done", output_index=0, item=item)
    response = snapshot("completed", [item])
    emit("completed", response=response)
    return response, events


class ScriptedModel:
    def __init__(self):
        self.turn = 0

    def respond(self, request):
        expected = ([USER], [USER, CALL, RESULT])
        if self.turn >= len(expected):
            raise ValueError("script is exhausted")
        if request != {
            "model": "offline-pump",
            "tools": [TOOL],
            "input": expected[self.turn],
        }:
            raise ValueError("unexpected request")
        item = (CALL, FINAL)[self.turn]
        self.turn += 1
        return make_turn(f"resp_{self.turn}", item)
