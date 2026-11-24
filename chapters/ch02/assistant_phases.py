# file: assistant_phases.py
import json

from assistant_message import assistant_text
from read_messages import inspect_message


commentary = assistant_text(
    "msg_p3_commentary", "I will check the stored reading."
)
commentary["phase"] = "commentary"
answer = assistant_text(
    "msg_p3_final", "The pressure at pump p3 is 210 kPa."
)
answer["phase"] = "final_answer"

messages = [commentary, answer]
restored = json.loads(json.dumps(messages))
for message in restored:
    for role, kind, phase in inspect_message(message):
        print(role, kind, phase, message["status"])
print("round trip equal:", restored == messages)
