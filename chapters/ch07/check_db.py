# file: check_db.py
import json
import sqlite3
import sys
from contextlib import closing

from fields import (
    INPUT, INPUT_TYPES, OUTPUT, OUTPUT_TYPES, check_item,
)
from machine import check_machine, check_terminal

SCHEMA = [
    "CREATE TABLE responses ("
    " response_order INTEGER PRIMARY KEY,"
    " response_id TEXT NOT NULL UNIQUE,"
    " status TEXT NOT NULL,"
    " payload TEXT NOT NULL)",
    "CREATE TABLE items ("
    " item_order INTEGER PRIMARY KEY,"
    " origin TEXT NOT NULL"
    " CHECK (origin IN ('input', 'model', 'tool')),"
    " direction TEXT NOT NULL"
    " CHECK (direction IN ('input', 'output')),"
    " response_id TEXT REFERENCES responses(response_id),"
    " output_index INTEGER,"
    " item_id TEXT,"
    " item_type TEXT NOT NULL,"
    " call_id TEXT,"
    " status TEXT,"
    " function_name TEXT,"
    " tool_output TEXT,"
    " payload TEXT NOT NULL,"
    " UNIQUE (response_id, output_index),"
    " UNIQUE (item_type, call_id),"
    " CHECK ("
    " (origin = 'model' AND direction = 'output'"
    " AND response_id IS NOT NULL"
    " AND output_index IS NOT NULL AND output_index >= 0)"
    " OR"
    " (origin IN ('input', 'tool') AND direction = 'input'"
    " AND response_id IS NULL AND output_index IS NULL)))",
    "CREATE TABLE events ("
    " response_id TEXT NOT NULL REFERENCES responses(response_id),"
    " event_order INTEGER NOT NULL CHECK (event_order >= 0),"
    " sequence_number INTEGER NOT NULL,"
    " event_type TEXT NOT NULL,"
    " item_id TEXT,"
    " payload TEXT NOT NULL,"
    " PRIMARY KEY (response_id, event_order),"
    " UNIQUE (response_id, sequence_number))",
]

CALL = {
    "id": "fc_p3_1",
    "type": "function_call",
    "call_id": "call_p3_1",
    "name": "get_reading",
    "arguments": '{"pump_id": "p3"}',
    "status": "completed",
}
RESULT = {
    "id": "fco_p3_1",
    "type": "function_call_output",
    "call_id": "call_p3_1",
    "output": '{"pump_id":"p3","pressure_kpa":210}',
    "status": "completed",
}
ANSWER = {
    "id": "msg_answer_p3",
    "type": "message",
    "status": "completed",
    "role": "assistant",
    "phase": "final_answer",
    "content": [
        {
            "type": "output_text",
            "text": "Pump p3 pressure is 210 kPa.",
            "annotations": [],
        }
    ],
}


def connect(path=":memory:"):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    if path == ":memory:":
        for stmt in SCHEMA:
            db.execute(stmt)
    return db


def put(db, rid, status, items, events, inputs=()):
    db.execute(
        "INSERT INTO responses"
        "(response_id, status, payload) VALUES (?,?,?)",
        (rid, status, json.dumps({"id": rid, "status": status})),
    )
    for item in inputs:
        origin = "tool" if item["type"] == "function_call_output" else "input"
        db.execute(
            "INSERT INTO items("
            "origin, direction, response_id, output_index,"
            " item_id, item_type, call_id, status,"
            " function_name, tool_output, payload)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                origin, "input", None, None, item.get("id"),
                item["type"], item.get("call_id"),
                item.get("status"), item.get("name"),
                item.get("output")
                if isinstance(item.get("output"), str) else None,
                json.dumps(item),
            ),
        )
    for i, item in enumerate(items):
        db.execute(
            "INSERT INTO items("
            "origin, direction, response_id, output_index,"
            " item_id, item_type, call_id, status,"
            " function_name, tool_output, payload)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                "model", "output", rid, i, item.get("id"),
                item["type"], item.get("call_id"),
                item.get("status"), item.get("name"),
                item.get("output")
                if isinstance(item.get("output"), str) else None,
                json.dumps(item),
            ),
        )
    for order, ev in enumerate(events):
        nested = ev.get("item") or {}
        db.execute(
            "INSERT INTO events("
            "response_id, event_order, sequence_number,"
            " event_type, item_id, payload)"
            " VALUES (?,?,?,?,?,?)",
            (
                rid, order, ev["sequence_number"], ev["type"],
                ev.get("item_id") or nested.get("id"),
                json.dumps(ev),
            ),
        )


def load(db, rid):
    row = db.execute(
        "SELECT status FROM responses WHERE response_id=?",
        (rid,),
    ).fetchone()
    if row is None:
        raise ValueError(f"unknown response: {rid}")
    items = [
        json.loads(r["payload"])
        for r in db.execute(
            "SELECT payload FROM items"
            " WHERE response_id=? AND direction='output'"
            " ORDER BY output_index",
            (rid,),
        )
    ]
    events = [
        json.loads(r["payload"])
        for r in db.execute(
            "SELECT payload FROM events"
            " WHERE response_id=?"
            " ORDER BY sequence_number",
            (rid,),
        )
    ]
    return row["status"], items, events, ()


def check_response(status, items, events, inputs=()):
    lines = []
    for item in [*items, *inputs]:
        if not isinstance(item, dict):
            lines.append("item must be an object")
            continue
        kind = item.get("type")
        req = OUTPUT.get(kind) if isinstance(kind, str) else None
        if req is None:
            lines.append(
                f"unsupported item type: {kind!r}"
            )
            continue
        lines.extend(
            check_item(item, req, OUTPUT_TYPES)
        )
    lines.extend(
        check_machine(items, status, events)
    )
    lines.extend(check_terminal(events, status))
    return lines


def check_database(path):
    with closing(connect(path)) as db:
        rids = [
            r["response_id"]
            for r in db.execute(
                "SELECT response_id FROM responses"
                " ORDER BY response_order"
            )
        ]
        if not rids:
            return ["database has no responses"]
        lines = []
        for rid in rids:
            lines.extend(check_response(*load(db, rid)))
        for r in db.execute(
            "SELECT payload FROM items"
            " WHERE origin = 'tool' ORDER BY item_order"
        ):
            item = json.loads(r["payload"])
            lines.extend(
                check_item(
                    item, INPUT["function_call_output"],
                    INPUT_TYPES,
                )
            )
        return lines


def report(title, lines):
    print(title)
    if lines:
        for line in lines:
            print(line)
    else:
        print("accept")


CALL_EVENTS = [
    {"type": "response.created", "sequence_number": 0},
    {"type": "response.in_progress", "sequence_number": 1},
    {
        "type": "response.output_item.added",
        "sequence_number": 2,
        "output_index": 0,
        "item": {**CALL, "status": "in_progress"},
    },
    {
        "type": "response.output_item.done",
        "sequence_number": 3,
        "output_index": 0,
        "item": CALL,
    },
    {"type": "response.completed", "sequence_number": 4},
]
TEXT_EVENTS = [
    {"type": "response.created", "sequence_number": 0},
    {"type": "response.in_progress", "sequence_number": 1},
    {
        "type": "response.output_item.added",
        "sequence_number": 2,
        "output_index": 0,
        "item": {**ANSWER, "status": "in_progress"},
    },
    {
        "type": "response.output_item.done",
        "sequence_number": 3,
        "output_index": 0,
        "item": ANSWER,
    },
    {"type": "response.completed", "sequence_number": 4},
]


def self_test():
    with closing(connect()) as db:
        put(db, "resp_1", "completed", [CALL], CALL_EVENTS)
        put(
            db, "resp_2", "completed",
            [ANSWER], TEXT_EVENTS, inputs=[RESULT],
        )
        pump = []
        for rid in ("resp_1", "resp_2"):
            pump.extend(check_response(*load(db, rid)))
        tool_rows = [
            json.loads(r["payload"])
            for r in db.execute(
                "SELECT payload FROM items WHERE origin='tool'"
            )
        ]
        for item in tool_rows:
            pump.extend(
                check_item(
                    item, OUTPUT["function_call_output"],
                    OUTPUT_TYPES,
                )
            )
        report("pump", pump)

        broken_call = dict(CALL)
        broken_call["call_id"] = "call_p3_broken"
        broken_call["status"] = "incomplete"
        put(
            db, "resp_broken", "completed",
            [broken_call, ANSWER], CALL_EVENTS,
        )
        report(
            "broken",
            check_response(*load(db, "resp_broken")),
        )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        report(sys.argv[1], check_database(sys.argv[1]))
    else:
        self_test()
