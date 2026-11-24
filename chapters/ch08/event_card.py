# file: event_card.py
from copy import deepcopy


def events(body):
    frames = []

    def emit(kind, **fields):
        frames.append({
            "type": "response." + kind,
            "sequence_number": len(frames),
            **deepcopy(fields),
        })

    start = deepcopy(body)
    start.update(status="in_progress", completed_at=None, output=[])
    emit("created", response=start)
    emit("in_progress", response=start)
    for index, item in enumerate(body["output"]):
        opening = deepcopy(item)
        opening["status"] = "in_progress"
        key = {"item_id": item["id"], "output_index": index}
        if item["type"] == "function_call":
            opening["arguments"] = ""
            emit("output_item.added", output_index=index, item=opening)
            emit("function_call_arguments.delta", **key,
                 delta=item["arguments"])
            emit("function_call_arguments.done", **key,
                 arguments=item["arguments"])
        else:
            opening["content"] = []
            emit("output_item.added", output_index=index, item=opening)
            for part_index, part in enumerate(item["content"]):
                at = {**key, "content_index": part_index}
                kind = part["type"]
                field = {"output_text": "text", "refusal": "refusal"}[kind]
                empty = {**part, field: ""}
                emit("content_part.added", **at, part=empty)
                emit(kind + ".delta", **at, delta=part[field])
                emit(kind + ".done", **at, **{field: part[field]})
                emit("content_part.done", **at, part=part)
        emit("output_item.done", output_index=index, item=item)
    emit(body["status"], response=body)
    return frames
