# file: test_http_transport.py
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import unittest

from http_transport import send_response_request
from response_card import message, response
from transcript import TOOL, get_reading


class StubHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        req = json.loads(self.rfile.read(n).decode("utf-8"))
        last = req["input"][-1]
        if last["type"] == "function_call_output":
            val = json.loads(last["output"])
            ans = (
                f"Pump {val['pump_id']} pressure is "
                f"{val['pressure_kpa']} kPa."
            )
            body = response([message(ans)], 2)
            frame = {"type": "response.completed", "response": body}
            wire = (
                "event: response.completed\n"
                f"data: {json.dumps(frame)}\n\n"
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Content-Length", str(len(wire)))
            self.end_headers()
            self.wfile.write(wire)
            return
        call = {
            "type": "function_call",
            "id": "fc_p3_1",
            "status": "completed",
            "call_id": "call_p3_1",
            "name": "get_reading",
            "arguments": '{"pump_id":"p3"}',
        }
        wire = json.dumps(response([call], 1)).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(wire)))
        self.end_headers()
        self.wfile.write(wire)


class HttpTransportTests(unittest.TestCase):
    def test_two_turn_pump_loop_over_loopback_http(self):
        srv = ThreadingHTTPServer(("127.0.0.1", 0), StubHandler)
        port = srv.server_address[1]
        th = threading.Thread(target=srv.serve_forever, daemon=True)
        th.start()
        try:
            url = f"http://127.0.0.1:{port}/v1/responses"
            items = [{
                "type": "message",
                "role": "user",
                "content": [{
                    "type": "input_text",
                    "text": "What is the pressure reading for pump p3?",
                }],
            }]
            r1 = send_response_request(
                {"model": "offline-pump", "input": items, "tools": [TOOL]},
                url=url,
            )
            call = r1["output"][0]
            reading = get_reading(**json.loads(call["arguments"]))
            items.extend([call, {
                "type": "function_call_output",
                "call_id": call["call_id"],
                "output": json.dumps(reading),
            }])
            r2 = send_response_request(
                {"model": "offline-pump", "input": items, "tools": [TOOL]},
                url=url,
            )
            text = r2["output"][0]["content"][0]["text"]
            self.assertEqual(text, "Pump p3 pressure is 210 kPa.")
            print("HTTP transport loop:", text)
        finally:
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main()
