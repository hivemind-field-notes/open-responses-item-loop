# file: run_ref.sh
set -eu
test ! -e reference.db
db=$(mktemp ./pump-reference.XXXXXX)
trap 'rm -f "$db"' EXIT
python3 sql_card.py "$db" <<'SQL'
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
SQL
python3 transcript.py pump "$db"
python3 transcript.py check "$db"
python3 sql_card.py "$db" <<'SQL'
SELECT response_order, status FROM responses ORDER BY response_order;
SELECT count(*) FROM items;
SELECT count(*) FROM events;
SQL
mv "$db" reference.db
