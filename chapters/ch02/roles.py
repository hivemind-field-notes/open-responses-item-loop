# file: roles.py
sentences = {
    "system": "Use plain English.",
    "developer": "Report pressure in kPa.",
    "user": "What is the pressure at pump p3?",
    "assistant": "The pressure at pump p3 is 210 kPa.",
}

for role, sentence in sentences.items():
    item = {
        "type": "message",
        "role": role,
        "content": sentence,
    }
    print(item["type"], item["role"])
