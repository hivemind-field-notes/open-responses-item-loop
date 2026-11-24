# file: rollback.py
import sqlite3
from contextlib import closing

from pump_model import CALL, make_turn
from transcript import connect, create, save_response


with closing(connect(":memory:")) as db:
    create(db)
    response, events = make_turn("resp_test", CALL)
    events.append(dict(events[-1]))
    try:
        save_response(db, response, events)
    except sqlite3.IntegrityError:
        print("duplicate event: rolled back")
    counts = [
        db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        for table in ("responses", "items", "events")
    ]
    print("rows:", *counts)
