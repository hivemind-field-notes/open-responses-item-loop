# file: sol_terminal_status.py
from check_db import ANSWER, CALL, TEXT_EVENTS
from machine import check_machine


TERMINAL = {
    "response.completed",
    "response.failed",
    "response.incomplete",
}


def check_from_terminal_event(items, events):
    found = [ev for ev in events if ev["type"] in TERMINAL]
    if len(found) != 1:
        return [f"expected 1 terminal event, found {len(found)}"]
    derived = found[-1]["type"].removeprefix("response.")
    issues = check_machine(items, derived, events)
    return derived, issues


incomplete_events = [
    *TEXT_EVENTS[:-1],
    {"type": "response.incomplete", "sequence_number": 4},
]
derived, issues = check_from_terminal_event([ANSWER], incomplete_events)
print("derived status:", derived)
print("verdict:", "accept" if not issues else "; ".join(issues))
bad_item = dict(ANSWER, status="incomplete")
derived2, issues2 = check_from_terminal_event([bad_item, CALL], incomplete_events)
print("incomplete not last:", "; ".join(issues2))
