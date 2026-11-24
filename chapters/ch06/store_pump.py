# file: store_pump.py
from contextlib import closing
from pathlib import Path
import json

from pump_model import READING, TOOL, USER, ScriptedModel
from transcript import append_item, connect, create, encode
from transcript import read_input, save_response


def get_reading(pump_id):
    if pump_id != "p3":
        raise ValueError("unknown pump")
    return dict(READING)


def main():
    path = Path("pump.sqlite3")
    if path.exists():
        raise SystemExit("pump.sqlite3 already exists")
    with closing(connect(path)) as db:
        create(db)
        with db:
            append_item(db, USER, "input")
        model = ScriptedModel()
        for turn in range(2):
            request = {
                "model": "offline-pump",
                "tools": [TOOL],
                "input": read_input(db),
            }
            response, events = model.respond(request)
            save_response(db, response, events)
            for item in response["output"]:
                if item["type"] != "function_call":
                    continue
                if item["status"] != "completed":
                    raise ValueError("unfinished call")
                if item["name"] != "get_reading":
                    raise ValueError("unknown tool")
                arguments = json.loads(item["arguments"])
                result = get_reading(**arguments)
                output = {
                    "type": "function_call_output",
                    "call_id": item["call_id"],
                    "output": encode(result),
                }
                with db:
                    append_item(db, output, "tool")
        for table in ("responses", "items", "events"):
            count = db.execute(
                f"SELECT count(*) FROM {table}"
            ).fetchone()[0]
            print(f"{table}: {count}")
        rows = db.execute(
            """SELECT item_order, origin, response_id, output_index
               FROM items ORDER BY item_order"""
        )
        for order, origin, response_id, index in rows:
            response_id = response_id or "-"
            index = "-" if index is None else index
            print(order, origin, response_id, index)


if __name__ == "__main__":
    main()
