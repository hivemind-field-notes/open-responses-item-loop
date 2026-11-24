# file: rule_card.py
def table(title, headers, rows):
    print(title)
    print(" | ".join(headers))
    for row in rows:
        print(" | ".join(row))
    print()


table("TOOL CHOICE", ("choice", "allowed output"), (
    ("auto", "direct answer or tool calls"),
    ("required", "at least one tool call"),
    ("none", "no tool calls"),
    ("named function", "call the named function"),
))
table("ITEM STATUS", ("from", "to / constraint"), (
    ("in_progress", "completed"),
    ("in_progress", "incomplete; last item, response incomplete"),
    ("completed", "no further updates"),
    ("incomplete", "terminal"),
))
table("EVENT ORDER: response. prefix; * means repeat as needed",
      ("message", "function_call"), (
    ("created", "created"),
    ("in_progress", "in_progress"),
    ("output_item.added", "output_item.added"),
    ("content_part.added", "function_call_arguments.delta*"),
    ("output_text.delta*", "function_call_arguments.done"),
    ("output_text.done", "output_item.done"),
    ("content_part.done", "completed"),
    ("output_item.done", ""),
    ("completed", ""),
))
