# file: wire.py
import json
from copy import deepcopy


TERMINAL = {
    "response.completed", "response.failed", "response.incomplete",
}
RESPONSE_EVENTS = TERMINAL | {
    "response.created", "response.queued", "response.in_progress",
}
TOOL = {
    "type": "function",
    "name": "get_reading",
    "description": "Read one local pump.",
    "parameters": {
        "type": "object",
        "properties": {"pump_id": {"type": "string"}},
        "required": ["pump_id"],
        "additionalProperties": False,
    },
    "strict": True,
}


def snapshot(status, output):
    return {
        "id": "resp_p3",
        "object": "response",
        "created_at": 0,
        "completed_at": 1 if status == "completed" else None,
        "status": status,
        "incomplete_details": None,
        "model": "offline-script",
        "previous_response_id": None,
        "instructions": None,
        "output": deepcopy(output),
        "error": None,
        "tools": [deepcopy(TOOL)],
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


class Emitter:
    def __init__(self):
        self.frames = []

    def emit(self, name, **fields):
        kind = name if name == "error" else "response." + name
        self.frames.append(deepcopy({
            "type": kind,
            "sequence_number": len(self.frames),
            **fields,
        }))


def begin():
    emitter = Emitter()
    for name, status in [
        ("created", "queued"),
        ("queued", "queued"),
        ("in_progress", "in_progress"),
    ]:
        emitter.emit(name, response=snapshot(status, []))
    return emitter


def encode_sse(frames, done=False):
    chunks = []
    for frame in frames:
        chunks.append("event: " + frame["type"] + "\n")
        chunks.append("data: " + json.dumps(frame) + "\n\n")
    if done:
        chunks.append("data: [DONE]\n\n")
    return "".join(chunks)


if __name__ == "__main__":
    for frame in begin().frames:
        print(frame["sequence_number"], frame["type"],
              frame["response"]["status"])
