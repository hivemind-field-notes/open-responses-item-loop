# file: next_input.py
import json
from contextlib import closing

from transcript import connect, read_input


with closing(connect("pump.sqlite3")) as db:
    row = db.execute(
        """SELECT item_order FROM items
           WHERE item_type = 'function_call_output' AND call_id = ?""",
        ("call_p3_1",),
    ).fetchone()
    if row is None:
        raise SystemExit("missing output for call_p3_1")
    print(json.dumps(read_input(db, through=row[0]), indent=2))
