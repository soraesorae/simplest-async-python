from collections import deque
import heapq
import time
from .handle import Handle, TimerHandle
from typing import List, Callable


class EventLoop:
    _callback_queue: deque[Handle | TimerHandle]
    _timer_callback_heap: List[TimerHandle]

    def __init__(self):
        self._callbacks = deque()
        self._timer_callback_heap = []

    def push_callback(self, _callback: Callable, *_args):
        handle = Handle(_callback, *_args)
        self._callbacks.append(handle)

    def push_timer_callback(self, _start_time: int, _callback: Callable, *_args):
        t_handle = TimerHandle(_start_time, _callback, *_args)
        heapq.heappush(self._timer_callback_heap, t_handle)

    def _round(self):
        current_ts = time.monotonic()

        while (
            len(self._timer_callback_heap) > 0
            and self._timer_callback_heap[0].start_time <= current_ts
        ):
            timer_callback_handle = heapq.heappop(self._timer_callback_heap)
            self._callback_queue.append(timer_callback_handle)

        queue_len = len(self._callback_queue)

        for _ in range(queue_len):
            handle = self._callback_queue.popleft()
            try:
                handle.run()
            except:
                pass

    def run_until_stop(self):
        while True:
            self._round()
