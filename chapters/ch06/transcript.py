# file: transcript.py
import json
import sqlite3
from contextlib import closing


SCHEMA = """
CREATE TABLE responses (
    response_order INTEGER PRIMARY KEY,
    response_id TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE TABLE items (
    item_order INTEGER PRIMARY KEY,
    origin TEXT NOT NULL
        CHECK (origin IN ('input', 'model', 'tool')),
    direction TEXT NOT NULL
        CHECK (direction IN ('input', 'output')),
    response_id TEXT REFERENCES responses(response_id),
    output_index INTEGER,
    item_id TEXT,
    item_type TEXT NOT NULL,
    call_id TEXT,
    status TEXT,
    function_name TEXT,
    tool_output TEXT,
    payload TEXT NOT NULL,
    UNIQUE (response_id, output_index),
    UNIQUE (item_type, call_id),
    CHECK (
        (origin = 'model' AND direction = 'output'
            AND response_id IS NOT NULL
            AND output_index IS NOT NULL AND output_index >= 0)
        OR
        (origin IN ('input', 'tool') AND direction = 'input'
            AND response_id IS NULL AND output_index IS NULL)
    )
);
CREATE TABLE events (
    response_id TEXT NOT NULL REFERENCES responses(response_id),
    event_order INTEGER NOT NULL CHECK (event_order >= 0),
    sequence_number INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    item_id TEXT,
    payload TEXT NOT NULL,
    PRIMARY KEY (response_id, event_order),
    UNIQUE (response_id, sequence_number)
);
"""


def connect(path):
    db = sqlite3.connect(path)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def create(db):
    db.executescript(SCHEMA)


def encode(value):
    return json.dumps(value, separators=(",", ":"))


def append_item(db, item, origin, response_id=None, output_index=None):
    direction = "output" if origin == "model" else "input"
    text = item.get("output")
    if not isinstance(text, str):
        text = None
    db.execute(
        """INSERT INTO items
           (origin, direction, response_id, output_index, item_id,
            item_type, call_id, status, function_name, tool_output,
            payload)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            origin, direction, response_id, output_index,
            item.get("id"), item["type"], item.get("call_id"),
            item.get("status"), item.get("name"), text, encode(item),
        ),
    )


def save_response(db, response, events):
    response_id = response["id"]
    with db:
        db.execute(
            """INSERT INTO responses (response_id, status, payload)
               VALUES (?, ?, ?)""",
            (response_id, response["status"], encode(response)),
        )
        for index, item in enumerate(response["output"]):
            append_item(db, item, "model", response_id, index)
        for order, event in enumerate(events):
            nested = event.get("item") or {}
            ev_item_id = event.get("item_id") or nested.get("id")
            db.execute(
                """INSERT INTO events
                   (response_id, event_order, sequence_number,
                    event_type, item_id, payload)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    response_id, order, event["sequence_number"],
                    event["type"], ev_item_id, encode(event),
                ),
            )


def read_input(db, through=None):
    query = "SELECT payload FROM items"
    params = ()
    if through is not None:
        query += " WHERE item_order <= ?"
        params = (through,)
    query += " ORDER BY item_order"
    return [json.loads(row[0]) for row in db.execute(query, params)]


if __name__ == "__main__":
    with closing(connect(":memory:")) as db:
        create(db)
        for name in ("responses", "items", "events"):
            row = db.execute(
                "SELECT sql FROM sqlite_schema WHERE name = ?",
                (name,),
            ).fetchone()
            print(row[0] + ";")
