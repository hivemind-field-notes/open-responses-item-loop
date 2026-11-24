# file: status_record.py
import json
import sqlite3


item = {
    "type": "function_call",
    "id": "fc_p3_1",
    "call_id": "call_p3_1",
    "name": "get_reading",
    "arguments": '{"pump_id":"p3"}',
    "status": "completed",
}
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE saved (payload TEXT NOT NULL)")
with db:
    db.execute("INSERT INTO saved VALUES (?)", (json.dumps(item),))
row = db.execute("SELECT payload FROM saved").fetchone()
stored = json.loads(row[0])
count = db.execute("SELECT count(*) FROM saved").fetchone()[0]
print("item status:", stored["status"])
print("stored rows:", count)
print("tool results:", int(stored["type"] == "function_call_output"))
db.close()
