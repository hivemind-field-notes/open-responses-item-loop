# file: http_transport.py
import json
import os
import urllib.error
import urllib.request


TERMINAL_EVENTS = {
    "response.completed",
    "response.failed",
    "response.incomplete",
}


def _parse_sse_response(raw_text):
    terminal = None
    event_name = ""
    data_lines = []
    for line in raw_text.splitlines() + [""]:
        if line == "":
            if data_lines:
                payload = "\n".join(data_lines)
                if payload != "[DONE]":
                    obj = json.loads(payload)
                    kind = obj.get("type") or event_name
                    if kind in TERMINAL_EVENTS and "response" in obj:
                        terminal = obj["response"]
                event_name = ""
                data_lines = []
            continue
        if line.startswith(":"):
            continue
        if line.startswith("event:"):
            event_name = line[6:].strip()
        elif line.startswith("data:"):
            val = line[5:]
            data_lines.append(val[1:] if val.startswith(" ") else val)
    if terminal is None:
        raise ValueError("SSE stream ended without terminal response")
    return terminal


def send_response_request(
    payload, *, url=None, api_key=None, model=None, timeout=30
):
    target = url or os.environ.get("OPEN_RESPONSES_URL")
    if not target:
        raise ValueError("OPEN_RESPONSES_URL is required")
    body = dict(payload)
    env_model = model or os.environ.get("OPEN_RESPONSES_MODEL")
    if env_model:
        body["model"] = env_model
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    key = api_key or os.environ.get("OPEN_RESPONSES_API_KEY")
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(
        target,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            ctype = (resp.headers.get("Content-Type") or "").lower()
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {err.code}: {detail}") from err
    if "text/event-stream" in ctype or raw.lstrip().startswith("event:"):
        return _parse_sse_response(raw)
    return json.loads(raw)
