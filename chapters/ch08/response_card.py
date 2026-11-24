# file: response_card.py
import json


def message(text):
    return {
        "type": "message",
        "id": "msg_answer_p3",
        "status": "completed",
        "role": "assistant",
        "phase": "final_answer",
        "content": [{
            "type": "output_text",
            "text": text,
            "annotations": [],
        }],
    }


def response(output, number=1):
    return {
        "id": f"resp_{number}",
        "object": "response",
        "created_at": 0,
        "completed_at": 0,
        "status": "completed",
        "incomplete_details": None,
        "model": "offline-pump",
        "previous_response_id": None,
        "instructions": None,
        "output": output,
        "error": None,
        "tools": [],
        "tool_choice": "auto",
        "truncation": "disabled",
        "parallel_tool_calls": False,
        "text": {"format": {"type": "text"}},
        "top_p": 1,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "top_logprobs": 0,
        "temperature": 1,
        "reasoning": None,
        "usage": None,
        "max_output_tokens": None,
        "max_tool_calls": None,
        "store": False,
        "background": False,
        "service_tier": "default",
        "metadata": {},
        "safety_identifier": None,
        "prompt_cache_key": None,
    }


if __name__ == "__main__":
    print(json.dumps(response([message("Ready.")]), indent=2))
