# file: parse_call.py
import json
import re

from call_items import sample_call


NAME_PATTERN = r"^[a-zA-Z0-9_-]+$"


def parse_call(item):
    if not isinstance(item, dict):
        raise ValueError("expected an item object")
    if item.get("type") != "function_call":
        raise ValueError("expected function_call")
    if item.get("status") != "completed":
        raise ValueError("call is not completed")
    name = item.get("name")
    if not isinstance(name, str) or not 1 <= len(name) <= 64:
        raise ValueError("invalid function name")
    if re.fullmatch(NAME_PATTERN, name) is None:
        raise ValueError("invalid function name")
    if name != "get_reading":
        raise ValueError("unknown function")
    call_id = item.get("call_id")
    if not isinstance(call_id, str) or not 1 <= len(call_id) <= 64:
        raise ValueError("invalid call_id")
    raw = item.get("arguments")
    if not isinstance(raw, str):
        raise ValueError("arguments must be a JSON string")
    try:
        args = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError("arguments are not JSON") from None
    if not isinstance(args, dict) or set(args) != {"pump_id"}:
        raise ValueError("expected only pump_id")
    if not isinstance(args["pump_id"], str) or not args["pump_id"]:
        raise ValueError("pump_id must be a nonempty string")
    return args


if __name__ == "__main__":
    def case(label, **changes):
        return label, {**sample_call(), **changes}

    cases = [
        case("valid"),
        case("bad name", name="get reading"),
        case("unknown", name="other_function"),
        case("unfinished", status="in_progress"),
        case("bad JSON", arguments='{"pump_id":'),
        case("array", arguments='["p3"]'),
        case("extra key", arguments='{"pump_id":"p3","x":1}'),
        case("number", arguments='{"pump_id":3}'),
    ]
    for label, item in cases:
        try:
            args = parse_call(item)
        except ValueError as error:
            print(label + ": rejected:", error)
        else:
            print(label + ":", args["pump_id"])
