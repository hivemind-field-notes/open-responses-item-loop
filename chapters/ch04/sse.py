# file: sse.py
import io
import json

from wire import TERMINAL, begin, encode_sse, snapshot


def parse_sse(text):
    name = None
    data = []
    for line in io.StringIO(text, newline=None):
        line = line.removesuffix("\n")
        if line == "":
            if not data:
                name = None
                continue
            payload = "\n".join(data)
            if payload == "[DONE]":
                raise ValueError("[DONE] before terminal event")
            frame = json.loads(payload)
            if not isinstance(frame, dict):
                raise ValueError("event body must be an object")
            if name is None or name != frame.get("type"):
                raise ValueError("event/type mismatch")
            yield frame
            if frame["type"] in TERMINAL:
                return
            name = None
            data = []
        elif not line.startswith(":"):
            key, separator, value = line.partition(":")
            if value.startswith(" "):
                value = value[1:]
            if key == "event":
                name = value
            elif key == "data":
                data.append(value)
    raise ValueError("stream ended before terminal event")


if __name__ == "__main__":
    emitter = begin()
    emitter.emit("completed", response=snapshot("completed", []))
    for trailer in [False, True]:
        frames = list(parse_sse(encode_sse(emitter.frames, trailer)))
        label = "with [DONE]:" if trailer else "without [DONE]:"
        print(label, frames[-1]["type"])
