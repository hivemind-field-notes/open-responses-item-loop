# file: drift_card.py
FLAGS = (
    "media-type",
    "error-object",
    "extending-items",
    "response-status",
    "reasoning-summary-events",
    "message-role",
    "servers-url",
    "response-example",
)


def report():
    for flag in FLAGS:
        print("drift: " + flag)


if __name__ == "__main__":
    report()
