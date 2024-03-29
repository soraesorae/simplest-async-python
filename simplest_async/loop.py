from collections import deque


class EventLoop:
    _callbacks: deque

    def __init__(self):
        self._callbacks = deque()

    def push_callback(self, _callback):
        self._callbacks.append(_callback)