# file: loop.py
from dataclasses import dataclass

from local_tools import dispatch
from request import make_request


@dataclass
class Result:
    answer: str
    reason: str
    detail: str = ""
    tool_calls: int = 0


def inspect_output(items):
    calls, texts, refusals = [], [], []
    for item in items:
        if item["status"] != "completed":
            raise ValueError("unfinished output item")
        if item["type"] == "function_call":
            calls.append(item)
        elif item["type"] == "message":
            if item["role"] != "assistant":
                raise ValueError("expected assistant output")
            for part in item["content"]:
                if part["type"] == "refusal":
                    refusals.append(part["refusal"])
                elif part["type"] == "output_text":
                    if item.get("phase") != "commentary":
                        texts.append(part["text"])
                else:
                    raise ValueError("unsupported content part")
        else:
            raise ValueError("unsupported output item")
    return calls, texts, refusals


def run(model, max_tool_calls=4):
    if type(max_tool_calls) is not int or max_tool_calls < 0:
        raise ValueError("max_tool_calls must be nonnegative")
    body = make_request()
    executed = 0
    seen = set()

    def stop(reason, detail="", answer=""):
        return Result(answer, reason, detail, executed)

    while True:
        try:
            response = model.create(body)
            status = response["status"]
            if status == "incomplete":
                details = response["incomplete_details"] or {}
                return stop("incomplete", details.get("reason", ""))
            if status == "failed":
                error = response["error"] or {}
                return stop("failed", error.get("message", ""))
            if status != "completed":
                return stop("failed", "unexpected response status")
            calls, texts, refusals = inspect_output(
                response["output"]
            )
            if refusals:
                return stop("failed", "refusal: " + " ".join(refusals))
            if calls:
                ids = [item["call_id"] for item in calls]
                if len(set(ids)) != len(ids) or seen.intersection(ids):
                    return stop("failed", "repeated call_id")
                if executed + len(calls) > max_tool_calls:
                    return stop("max_tool_calls")
                results = []
                for item in calls:
                    results.append(dispatch(item))
                    executed += 1
                    seen.add(item["call_id"])
                body = make_request(results, previous=response["id"])
                continue
            if texts:
                return stop(
                    "completed output_text", answer="\n".join(texts)
                )
            return stop("failed", "no actionable output")
        except (KeyError, TypeError, ValueError) as error:
            return stop("failed", str(error))
