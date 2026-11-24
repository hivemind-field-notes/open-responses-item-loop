# file: join_results.py
from call_items import sample_call


def join_results(calls, results):
    ids = [call["call_id"] for call in calls]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate call_id")
    by_id = {}
    for result in results:
        call_id = result["call_id"]
        if call_id not in ids:
            raise ValueError("unknown call_id")
        if call_id in by_id:
            raise ValueError("duplicate output")
        by_id[call_id] = result
    if len(by_id) != len(ids):
        raise ValueError("missing output")
    return [by_id[call_id] for call_id in ids]


first = sample_call()
second = {
    **sample_call(),
    "id": "fc_p4_1",
    "call_id": "call_p4_1",
    "arguments": '{"pump_id":"p4"}',
}
calls = [first, second]
results = [
    {
        "type": "function_call_output",
        "call_id": call_id,
        "output": reading,
        "status": "completed",
    }
    for call_id, reading in [
        ("call_p4_1", "p4: pressure=185 kPa"),
        ("call_p3_1", "p3: pressure=210 kPa"),
    ]
]
for result in join_results(calls, results):
    print(result["call_id"], result["output"])
try:
    join_results(calls, results + [results[0]])
except ValueError as error:
    print("rejected:", error)
