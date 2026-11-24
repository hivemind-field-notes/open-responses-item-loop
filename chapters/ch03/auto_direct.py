# file: auto_direct.py
from choice_demo import make_request
from scripted_model import scripted_model


for choice in ("auto", "required"):
    items = scripted_model(make_request(choice, "Say hello."))
    assert len(items) == 1
    print(choice + ":", items[0]["type"])
