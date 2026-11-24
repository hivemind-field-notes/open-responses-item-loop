# file: map_pair.py
import json

assistant = {
    "role": "assistant",
    "content": None,
    "tool_calls": [
        {
            "id": "call_p3_1",
            "type": "function",
            "function": {
                "name": "get_reading",
                "arguments": json.dumps({"pump_id": "p3"}),
            },
        }
    ],
}
tool = {
    "role": "tool",
    "tool_call_id": "call_p3_1",
    "content": json.dumps({"pump_id": "p3", "pressure_kpa": 210}),
}


def map_pair(assistant, tool):
    if assistant["role"] != "assistant" or tool["role"] != "tool":
        raise ValueError("expected an assistant/tool pair")
    if assistant.get("content"):
        raise ValueError("map assistant text as a separate message")
    if len(assistant["tool_calls"]) != 1:
        raise ValueError("this example maps exactly one call")
    source = assistant["tool_calls"][0]
    if source["type"] != "function":
        raise ValueError("expected a function tool call")
    if source["id"] != tool["tool_call_id"]:
        raise ValueError("tool result belongs to another call")
    call = {
        "type": "function_call",
        "id": "fc_p3_1",
        "status": "completed",
        "call_id": source["id"],
        "name": source["function"]["name"],
        "arguments": source["function"]["arguments"],
    }
    result = {
        "type": "function_call_output",
        "id": "fco_p3_1",
        "status": "completed",
        "call_id": tool["tool_call_id"],
        "output": tool["content"],
    }
    return call, result


call, result = map_pair(assistant, tool)
for item in (call, result):
    print(item["type"], item["id"], item["call_id"])
print("arguments:", call["arguments"])
print("output:", result["output"])
