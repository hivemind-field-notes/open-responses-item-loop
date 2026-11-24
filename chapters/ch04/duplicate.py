# file: duplicate.py
from copy import deepcopy

from fold import fold
from message_stream import message_frames
from sse import parse_sse
from wire import encode_sse


frames = message_frames()
frames.insert(6, deepcopy(frames[5]))
for number, frame in enumerate(frames):
    frame["sequence_number"] = number
try:
    fold(parse_sse(encode_sse(frames)))
except ValueError as error:
    print("rejected:", error)
