# file: drift.py
from textwrap import fill

from fields import SNAPSHOT

FLAGS = [
    (
        "media-type", "spec",
        "Clients MUST send request bodies encoded "
        "as application/json.",
        "POST /responses requestBody content lists "
        "application/json and "
        "application/x-www-form-urlencoded.",
    ),
    (
        "error-object", "spec",
        "Example error uses type "
        "invalid_request_error with message, type, "
        "param, code. The type table lists "
        "server_error, invalid_request, not_found, "
        "model_error, too_many_requests.",
        "ResponseResource.error uses Error, which "
        "requires code, message and permits extra keys. "
        "Streaming ErrorPayload requires type, code, "
        "message, param; code and param may be null.",
    ),
    (
        "extending-items", "spec",
        "Every Item MUST include id, type, status. "
        "Typical status values include "
        "in_progress, completed, and failed.",
        "ItemParam message requires type, role, "
        "content; function_call requires call_id, "
        "type, name, arguments. Output enums are "
        "in_progress, completed, incomplete. "
        "ItemField is Message, FunctionCall, "
        "FunctionCallOutput, ReasoningBody, "
        "CompactionBody.",
    ),
    (
        "response-status", "spec",
        "A stream MUST include a terminal "
        "response.completed, response.failed, or "
        "response.incomplete event.",
        "ResponseResource.status is a free string.",
    ),
    (
        "reasoning-summary-events", "openapi description",
        "The event descriptions say the type is "
        "always response.reasoning_summary.delta "
        "and response.reasoning_summary.done.",
        "The enum values are "
        "response.reasoning_summary_text.delta and "
        "response.reasoning_summary_text.done.",
    ),
    (
        "message-role", "openapi description",
        "The Message role description lists "
        "unknown, user, assistant, system, critic, "
        "discriminator, developer, or tool.",
        "MessageRole enum is user, assistant, "
        "system, developer.",
    ),
    (
        "servers-url", "spec",
        "The specification is a multi-provider "
        "contract. Extension item types use an "
        "implementor slug prefix.",
        "servers[0].url is "
        "https://api.openai.com/v1.",
    ),
    (
        "response-example", "openapi required",
        "ResponseResource.required includes "
        "reasoning, incomplete_details, "
        "previous_response_id, instructions, "
        "error, max_output_tokens, max_tool_calls, "
        "safety_identifier, prompt_cache_key.",
        "The published example sets reasoning to "
        "{} (Reasoning requires effort, summary) "
        "and omits incomplete_details, "
        "previous_response_id, instructions, "
        "error, max_output_tokens, max_tool_calls, "
        "safety_identifier, prompt_cache_key.",
    ),
]

print(f"snapshot {SNAPSHOT}")
for name, source, claim, openapi in FLAGS:
    print(name)
    for label, text in ((source, claim), ("openapi", openapi)):
        print(fill(
            text, width=80, initial_indent=f"  {label}: ",
            subsequent_indent="    ",
        ))
