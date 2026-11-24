# file: message_stream.py
from wire import begin, encode_sse, snapshot


def message_frames():
    emitter = begin()
    item = {
        "type": "message",
        "id": "msg_p3",
        "status": "in_progress",
        "role": "assistant",
        "phase": "final_answer",
        "content": [],
    }
    emitter.emit("output_item.added", output_index=0, item=item)
    location = {
        "item_id": item["id"],
        "output_index": 0,
        "content_index": 0,
    }
    part = {"type": "output_text", "text": "", "annotations": []}
    emitter.emit("content_part.added", **location, part=part)
    for chunk in ["Pump p3 pressure ", "is 210 kPa."]:
        emitter.emit("output_text.delta", **location, delta=chunk)
        part["text"] += chunk
    emitter.emit("output_text.done", **location, text=part["text"])
    emitter.emit("content_part.done", **location, part=part)
    item["content"] = [part]
    item["status"] = "completed"
    emitter.emit("output_item.done", output_index=0, item=item)
    emitter.emit("completed", response=snapshot("completed", [item]))
    return emitter.frames


def message_stream(done=False):
    return encode_sse(message_frames(), done)


if __name__ == "__main__":
    for frame in message_frames():
        print(frame["sequence_number"], frame["type"])
