# file: transcript.py
import json
import re
import sqlite3
import sys

from drift_card import report
from event_card import events
from response_card import message, response


TOOL = {
    "type": "function",
    "name": "get_reading",
    "description": "Read a local pump fixture.",
    "parameters": {
        "type": "object",
        "properties": {"pump_id": {"type": "string"}},
        "required": ["pump_id"],
        "additionalProperties": False,
    },
    "strict": True,
}


def history(db):
    rows = db.execute("SELECT payload FROM items ORDER BY item_order")
    return [json.loads(row[0]) for row in rows]


def remember(db, origin, item, response_id=None, output_index=None):
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
            item.get("status"), item.get("name"), text,
            json.dumps(item, separators=(",", ":")),
        ),
    )


def get_reading(pump_id):
    if pump_id != "p3":
        raise ValueError("unknown pump")
    return {"pump_id": pump_id, "pressure_kpa": 210}


def scripted(items, turn):
    last = items[-1]
    if last["type"] == "function_call_output":
        value = json.loads(last["output"])
        text = (
            f"Pump {value['pump_id']} pressure is "
            f"{value['pressure_kpa']} kPa."
        )
        output = [message(text)]
    else:
        output = [{
            "type": "function_call",
            "id": "fc_p3_1",
            "status": "completed",
            "call_id": "call_p3_1",
            "name": "get_reading",
            "arguments": '{"pump_id":"p3"}',
        }]
    body = response(output, turn)
    body["tools"] = [TOOL]
    return body


def pump(db):
    if history(db):
        raise ValueError("database must be empty")
    remember(db, "input", {
        "type": "message",
        "id": "msg_user_p3",
        "role": "user",
        "content": [{
            "type": "input_text",
            "text": "What is the pressure reading for pump p3?",
        }],
    })
    for turn in range(1, 4):
        body = scripted(history(db), turn)
        rid = body["id"]
        db.execute(
            "INSERT INTO responses (response_id, status, payload)"
            " VALUES (?, ?, ?)",
            (rid, body["status"], json.dumps(body, separators=(",", ":"))),
        )
        for order, frame in enumerate(events(body)):
            nested = frame.get("item") or {}
            ev_item = frame.get("item_id") or nested.get("id")
            db.execute(
                "INSERT INTO events"
                " (response_id, event_order, sequence_number,"
                " event_type, item_id, payload)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (
                    rid, order, frame["sequence_number"],
                    frame["type"], ev_item,
                    json.dumps(frame, separators=(",", ":")),
                ),
            )
        for idx, item in enumerate(body["output"]):
            remember(db, "model", item, rid, idx)
        if body["status"] != "completed":
            raise ValueError("response did not complete")
        calls = [x for x in body["output"]
                 if x["type"] == "function_call"]
        if calls:
            for call in calls:
                if call["status"] != "completed":
                    raise ValueError("unfinished call")
                if call["name"] != "get_reading":
                    raise ValueError("unknown function")
                args = json.loads(call["arguments"])
                if not isinstance(args, dict) or set(args) != {"pump_id"}:
                    raise ValueError("expected only a pump_id argument")
                if not isinstance(args["pump_id"], str):
                    raise ValueError("pump_id must be a string")
                result = get_reading(**args)
                remember(db, "tool", {
                    "type": "function_call_output",
                    "id": "fco_p3_1",
                    "call_id": call["call_id"],
                    "status": "completed",
                    "output": json.dumps(result, separators=(",", ":")),
                })
            continue
        final = [item for item in body["output"]
                 if item["type"] == "message"
                 and item["status"] == "completed"
                 and item.get("phase") == "final_answer"]
        texts = [part["text"] for item in final
                 for part in item["content"]
                 if part["type"] == "output_text"]
        if texts:
            print("".join(texts))
            return
        if any(part["type"] == "refusal" for item in final
               for part in item["content"]):
            return
        raise ValueError("no final text")
    raise ValueError("turn limit")


def check(db):
    rows = list(db.execute(
        "SELECT response_order, response_id, status, payload"
        " FROM responses ORDER BY response_order"
    ))
    if not rows:
        raise ValueError("empty transcript")
    for _, identifier, status, raw in rows:
        body = json.loads(raw)
        missing = set(response([])) - body.keys()
        if missing:
            raise ValueError("missing: " + ", ".join(sorted(missing)))
        if body["object"] != "response":
            raise ValueError("wrong object")
        if (identifier, status) != (body["id"], body["status"]):
            raise ValueError("response columns disagree")
        if status != "completed":
            raise ValueError("reference run requires completed")
        for item in body["output"]:
            if not item.get("id") or item["status"] != "completed":
                raise ValueError("unfinished or unaddressable item")
            if item["type"] == "function_call":
                name = item["name"]
                if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", name):
                    raise ValueError("bad function name")
                if not 1 <= len(item["call_id"]) <= 64:
                    raise ValueError("bad call_id")
                json.loads(item["arguments"])
            elif item["type"] == "message":
                if item["role"] != "assistant":
                    raise ValueError("expected assistant")
                for part in item["content"]:
                    if part["type"] != "output_text":
                        raise ValueError("expected output_text")
                    if not isinstance(part["text"], str):
                        raise ValueError("text must be a string")
                    if not isinstance(part["annotations"], list):
                        raise ValueError("annotations must be a list")
            else:
                raise ValueError("unsupported reference item")
        stored = db.execute(
            "SELECT payload FROM items"
            " WHERE response_id=? AND direction='output'"
            " ORDER BY output_index", (identifier,),
        )
        if [json.loads(x[0]) for x in stored] != body["output"]:
            raise ValueError("stored items disagree")
        stored = db.execute(
            "SELECT sequence_number, payload FROM events"
            " WHERE response_id=?"
            " ORDER BY sequence_number", (identifier,),
        )
        frames = []
        for number, raw_frame in stored:
            frame = json.loads(raw_frame)
            if number != frame["sequence_number"]:
                raise ValueError("event columns disagree")
            frames.append(frame)
        if frames != events(body):
            raise ValueError("reference event sequence differs")
    print("accept")
    report()


if __name__ == "__main__":
    with sqlite3.connect(sys.argv[2]) as db:
        db.execute("PRAGMA foreign_keys = ON")
        try:
            {"pump": pump, "check": check}[sys.argv[1]](db)
        except (KeyError, TypeError, ValueError) as error:
            raise SystemExit(str(error)) from error
