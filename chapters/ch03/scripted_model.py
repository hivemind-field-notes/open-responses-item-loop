# file: scripted_model.py
from call_items import sample_call


def direct_message():
    return {
        "type": "message",
        "id": "msg_direct_1",
        "role": "assistant",
        "status": "completed",
        "phase": "final_answer",
        "content": [{
            "type": "output_text",
            "text": "No tool was called.",
            "annotations": [],
        }],
    }


def scripted_model(request):
    choice = request["tool_choice"]
    if choice == "none":
        use_tool = False
    elif choice == "auto":
        text = " ".join(
            part["text"]
            for item in request["input"]
            if item.get("type") == "message"
            for part in item["content"]
            if part["type"] == "input_text"
        )
        use_tool = "p3" in text
    elif choice == "required":
        use_tool = True
    elif choice == {"type": "function", "name": "get_reading"}:
        use_tool = True
    else:
        raise ValueError("unsupported tool_choice")
    if use_tool:
        names = {
            tool["name"] for tool in request["tools"]
            if tool["type"] == "function"
        }
        if "get_reading" not in names:
            raise ValueError("get_reading is not declared")
        return [sample_call()]
    return [direct_message()]
