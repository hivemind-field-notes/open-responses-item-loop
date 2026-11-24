# file: stops.py
from loop import run
from scripted import ScriptedModel, answer, ask, call_item


def cut_short(context):
    first = call_item()
    last = call_item()
    last.update(
        id="fc_2", call_id="call_2", status="incomplete",
        arguments='{"pump_id":',
    )
    return {
        "status": "incomplete",
        "incomplete_details": {"reason": "max_output_tokens"},
        "output": [first, last],
    }


def fail(context):
    return {
        "status": "failed",
        "error": {
            "code": "scripted_failure",
            "message": "scripted model stopped",
        },
        "output": [call_item()],
    }


def two_calls(context):
    first = call_item()
    second = call_item()
    second.update(id="fc_2", call_id="call_2")
    return {"output": [first, second]}


if __name__ == "__main__":
    cases = [
        ("success", [ask, answer], 1),
        ("cut short", [cut_short], 4),
        ("failed response", [fail], 4),
        ("batch over limit", [two_calls], 1),
    ]
    for label, turns, budget in cases:
        model = ScriptedModel(turns)
        result = run(model, max_tool_calls=budget)
        print(label + ":", result.reason)
        print("requests:", len(model.requests))
        print("tool calls:", result.tool_calls)
        if result.detail:
            print("detail:", result.detail)
