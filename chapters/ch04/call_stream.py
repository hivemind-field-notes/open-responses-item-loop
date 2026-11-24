# file: call_stream.py
from wire import begin, encode_sse, snapshot


def call_frames():
    emitter = begin()
    item = {
        "type": "function_call",
        "id": "fc_p3_1",
        "call_id": "call_p3_1",
        "name": "get_reading",
        "arguments": "",
        "status": "in_progress",
    }
    emitter.emit("output_item.added", output_index=0, item=item)
    location = {"item_id": item["id"], "output_index": 0}
    for chunk in ['{"pump_id":', '"p3"}']:
        emitter.emit("function_call_arguments.delta",
                     **location, delta=chunk)
        item["arguments"] += chunk
    emitter.emit("function_call_arguments.done", **location,
                 arguments=item["arguments"])
    item["status"] = "completed"
    emitter.emit("output_item.done", output_index=0, item=item)
    emitter.emit("completed", response=snapshot("completed", [item]))
    return emitter.frames


def call_stream(done=False):
    return encode_sse(call_frames(), done)


if __name__ == "__main__":
    for frame in call_frames():
        print(frame["sequence_number"], frame["type"])
