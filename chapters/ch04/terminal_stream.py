# file: terminal_stream.py
from sse import parse_sse
from wire import begin, encode_sse, snapshot


def terminal_frames(status):
    emitter = begin()
    response = snapshot(status, [])
    if status == "failed":
        emitter.emit("error", error={
            "type": "model_error",
            "code": None,
            "message": "Scripted model failure.",
            "param": None,
        })
        response["error"] = {
            "code": "model_error",
            "message": "Scripted model failure.",
        }
    elif status == "incomplete":
        response["incomplete_details"] = {
            "reason": "max_output_tokens",
        }
    emitter.emit(status, response=response)
    return emitter.frames


if __name__ == "__main__":
    for status in ["completed", "failed", "incomplete"]:
        frames = list(parse_sse(encode_sse(terminal_frames(status))))
        final = frames[-1]
        print(final["type"], final["response"]["status"])
