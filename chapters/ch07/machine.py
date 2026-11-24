# file: machine.py
ENDS = (
    "response.completed",
    "response.failed",
    "response.incomplete",
)


def check_machine(items, response_status, events=()):
    lines = []
    final = {}
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        status = item.get("status")
        item_id = item.get("id")
        if isinstance(item_id, str):
            if item_id in final:
                lines.append(f"duplicate item id: {item_id}")
            final[item_id] = item
        label = item_id or f"item[{i}]"
        if status == "incomplete":
            if i != len(items) - 1:
                lines.append(f"{label} incomplete is not last")
            if response_status != "incomplete":
                lines.append(
                    f"{label} incomplete but "
                    f"response status is {response_status}"
                )
    closed = {}
    for ev in events:
        etype = ev.get("type", "")
        if not isinstance(etype, str) or not etype.startswith("response."):
            continue
        nested = ev.get("item")
        nested = nested if isinstance(nested, dict) else {}
        item_id = ev.get("item_id") or nested.get("id")
        if not isinstance(item_id, str):
            continue
        if item_id in closed:
            lines.append(
                f"{item_id} updated after {closed[item_id]}"
            )
        status = nested.get("status")
        if status in ("completed", "incomplete"):
            closed[item_id] = status
        if etype == "response.output_item.done":
            if item_id in final and nested != final[item_id]:
                lines.append(f"{item_id} done differs from stored item")
    return lines


def check_terminal(events, response_status):
    found = [ev for ev in events if ev.get("type") in ENDS]
    if not found:
        return ["missing terminal response event"]
    lines = []
    if len(found) != 1:
        lines.append("multiple terminal response events")
    last = found[-1]["type"]
    want = f"response.{response_status}"
    if last != want:
        lines.append(f"{last} vs status {response_status}")
    end = next(i for i, ev in enumerate(events) if ev is found[0])
    if any(
        str(ev.get("type", "")).startswith("response.")
        for ev in events[end + 1:]
    ):
        lines.append("response event after terminal event")
    for ev in found:
        snapshot = ev.get("response")
        if isinstance(snapshot, dict):
            if f"response.{snapshot.get('status')}" != ev["type"]:
                lines.append("terminal snapshot status mismatch")
    return lines
