# file: pending.py
from contextlib import closing

from pump_model import CALL, RESULT, make_turn
from transcript import append_item, connect, create, save_response


QUERY = """
SELECT c.call_id,
       CASE WHEN o.item_order IS NULL THEN 'pending'
            ELSE 'recorded' END
FROM items AS c
LEFT JOIN items AS o
  ON o.call_id = c.call_id
 AND o.item_type = 'function_call_output'
WHERE c.item_type = 'function_call'
ORDER BY c.item_order
"""

with closing(connect(":memory:")) as db:
    create(db)
    response, events = make_turn("resp_test", CALL)
    save_response(db, response, events)
    print("before:", db.execute(QUERY).fetchall())
    with db:
        append_item(db, RESULT, "tool")
    print("after:", db.execute(QUERY).fetchall())
