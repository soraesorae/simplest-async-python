from collections import deque
import heapq
from .handle import Handle, TimerHandle
from typing import List, Callable


class EventLoop:
    _callback_queue: deque[Handle | TimerHandle]
    _timer_callback_queue: List[TimerHandle]

    def __init__(self):
        self._callbacks = deque()

    def push_callback(self, _callback: Callable, *_args):
        handle = Handle(_callback, *_args)
        self._callbacks.append(handle)

    def push_timer_callback(self, _start_time: int, _callback: Callable, *_args):
        t_handle = TimerHandle(_start_time, _callback, *_args)
        heapq.heappush(self._timer_callback_queue, t_handle)
