# file: fields.py
SNAPSHOT = "2026-04-24"

OUTPUT = {
    "message": (
        "id", "type", "status", "role", "content",
    ),
    "function_call": (
        "id", "type", "call_id", "name", "arguments",
        "status",
    ),
    "function_call_output": (
        "id", "type", "call_id", "output", "status",
    ),
}

INPUT = {
    "message": ("type", "role", "content"),
    "function_call": (
        "type", "call_id", "name", "arguments",
    ),
    "function_call_output": (
        "type", "call_id", "output",
    ),
}

OUTPUT_TYPES = {
    "id": str,
    "type": str,
    "status": str,
    "role": str,
    "content": list,
    "call_id": str,
    "name": str,
    "arguments": str,
    "output": (str, list),
}

INPUT_TYPES = dict(OUTPUT_TYPES)
INPUT_TYPES["content"] = (str, list)

STATUSES = (
    "in_progress", "completed", "incomplete",
)
ROLES = (
    "user", "assistant", "system", "developer",
)


def type_name(want):
    if isinstance(want, tuple):
        return " or ".join(t.__name__ for t in want)
    return want.__name__


def check_item(item, required, types):
    lines = []
    if not isinstance(item, dict):
        return ["item must be an object"]
    kind = item.get("type")
    if not isinstance(kind, str) or not kind:
        kind = "item"
    optional = ("id", "status")
    if kind == "message" and (
        types is OUTPUT_TYPES or item.get("role") == "assistant"
    ):
        optional += ("phase",)
    fields = dict.fromkeys((*required, *optional))
    for field in fields:
        if field not in required:
            if field not in item:
                continue
            if item[field] is None and field != "phase":
                continue
        if field not in item or item[field] is None:
            lines.append(
                f"{kind} missing field: {field}"
            )
            continue
        got = item[field]
        want = str if field == "phase" else types[field]
        if not isinstance(got, want):
            lines.append(
                f"{kind} mistyped field: {field} "
                f"(got {type(got).__name__}, "
                f"want {type_name(want)})"
            )
            continue
        constrained = types is OUTPUT_TYPES or kind != "message"
        if field == "status" and constrained and got not in STATUSES:
            allowed = list(STATUSES)
            lines.append(
                f"{kind} mistyped field: status "
                f"(got {got!r}, want {allowed})"
            )
        if field == "role" and got not in ROLES:
            allowed = list(ROLES)
            lines.append(
                f"{kind} mistyped field: role "
                f"(got {got!r}, want {allowed})"
            )
        if field == "phase" and got not in (
            "commentary", "final_answer",
        ):
            lines.append(f"{kind} invalid phase: {got!r}")
    return lines
