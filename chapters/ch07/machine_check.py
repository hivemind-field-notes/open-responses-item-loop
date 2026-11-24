# file: machine_check.py
from machine import check_machine


def dump(title, lines):
    print(title)
    if lines:
        for line in lines:
            print(line)
    else:
        print("ok")


AFTER = [
    {
        "type": "response.output_item.done",
        "sequence_number": 0,
        "output_index": 0,
        "item": {
            "id": "msg_answer_p3",
            "type": "message",
            "status": "completed",
            "role": "assistant",
            "content": [],
        },
    },
    {
        "type": "response.output_text.delta",
        "sequence_number": 1,
        "item_id": "msg_answer_p3",
        "output_index": 0,
        "content_index": 0,
        "delta": " extra",
    },
]
dump(
    "after completed",
    check_machine(
        [AFTER[0]["item"]],
        "completed",
        AFTER,
    ),
)

dump(
    "incomplete not last",
    check_machine(
        [
            {"id": "msg_answer_p3", "status": "incomplete"},
            {"id": "msg_2", "status": "completed"},
        ],
        "incomplete",
    ),
)

dump(
    "incomplete vs completed",
    check_machine(
        [{"id": "msg_answer_p3", "status": "incomplete"}],
        "completed",
    ),
)
