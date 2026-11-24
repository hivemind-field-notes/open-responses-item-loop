# file: message_cards.py
import json

messages = [
    {
        "type": "message",
        "role": role,
        "content": [{"type": "input_text", "text": text}],
    }
    for role, text in (
        ("system", "Use the local fixture."),
        ("developer", "Report pressure in kPa."),
        ("user", "What is the pressure reading for pump p3?"),
    )
]
messages.append({
    "type": "message",
    "role": "assistant",
    "phase": "commentary",
    "content": [{
        "type": "output_text",
        "text": "Checking pump p3.",
        "annotations": [],
    }],
})
messages.append({
    "type": "message",
    "role": "assistant",
    "phase": "final_answer",
    "content": [{
        "type": "refusal",
        "refusal": "I cannot perform that action.",
    }],
})
for item in messages:
    print(json.dumps(item))
