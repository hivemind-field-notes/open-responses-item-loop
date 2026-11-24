# file: check_join.py
import json

from scripted_model import QUESTION, READING, scripted_model

user = {
    "type": "message",
    "id": "msg_user_p3",
    "status": "completed",
    "role": "user",
    "content": [{"type": "input_text", "text": QUESTION}],
}
call = scripted_model([user])
for candidate in (call["id"], call["call_id"]):
    result = {
        "type": "function_call_output",
        "id": "fco_probe",
        "status": "completed",
        "call_id": candidate,
        "output": json.dumps(READING),
    }
    try:
        answer = scripted_model([user, call, result])
    except ValueError:
        print(candidate + ": rejected")
    else:
        print(candidate + ": " + answer["status"])
