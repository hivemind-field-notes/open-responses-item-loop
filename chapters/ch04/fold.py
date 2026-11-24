# file: fold.py
from copy import deepcopy

from wire import RESPONSE_EVENTS, TERMINAL


ITEM_EVENTS = {
    "response.output_item.added", "response.output_item.done",
    "response.content_part.added", "response.content_part.done",
    "response.output_text.delta", "response.output_text.done",
    "response.function_call_arguments.delta",
    "response.function_call_arguments.done",
}


def at(values, index):
    if type(index) is not int or not 0 <= index < len(values):
        raise ValueError("bad index")
    return values[index]


def append_at(values, index, value):
    if type(index) is not int or index != len(values):
        raise ValueError("bad append index")
    values.append(deepcopy(value))


def same(actual, expected):
    if actual != expected:
        raise ValueError("snapshot mismatch")


def fold(frames, trace=False):
    output = []
    response_id = None
    last = None
    for frame in frames:
        number = frame["sequence_number"]
        if type(number) is not int:
            raise ValueError("sequence_number must be an integer")
        if last is not None and number <= last:
            raise ValueError("sequence_number did not increase")
        last = number
        kind = frame["type"]
        if trace:
            print(number, kind)
        if kind in RESPONSE_EVENTS:
            response = deepcopy(frame["response"])
            if response_id is not None:
                same(response["id"], response_id)
            response_id = response["id"]
            same(response["output"], output)
            if kind in TERMINAL:
                same(response["status"], kind.split(".")[1])
                response["output"] = deepcopy(output)
                return response
            continue
        if kind == "error" or ":" in kind:
            continue
        if kind not in ITEM_EVENTS:
            raise ValueError("unsupported event: " + kind)
        index = frame["output_index"]
        if kind == "response.output_item.added":
            append_at(output, index, frame["item"])
            continue
        item = at(output, index)
        same(item["status"], "in_progress")
        if "item_id" in frame:
            same(frame["item_id"], item["id"])
        if kind == "response.output_item.done":
            final = frame["item"]
            if final["status"] not in {"completed", "incomplete"}:
                raise ValueError("item did not reach a terminal status")
            same(final, {**item, "status": final["status"]})
            output[index] = deepcopy(final)
        elif kind == "response.function_call_arguments.delta":
            same(item["type"], "function_call")
            item["arguments"] += frame["delta"]
        elif kind == "response.function_call_arguments.done":
            same(item["type"], "function_call")
            same(item["arguments"], frame["arguments"])
        elif kind == "response.content_part.added":
            same(item["type"], "message")
            append_at(item["content"], frame["content_index"],
                      frame["part"])
        elif kind in {
            "response.output_text.delta", "response.output_text.done",
            "response.content_part.done",
        }:
            same(item["type"], "message")
            part = at(item["content"], frame["content_index"])
            same(part["type"], "output_text")
            if kind == "response.output_text.delta":
                part["text"] += frame["delta"]
            elif kind == "response.output_text.done":
                same(part["text"], frame["text"])
            else:
                same(part, frame["part"])
    raise ValueError("no terminal response")
