from collections import deque
import heapq
import time
from .handle import Handle, TimerHandle
from .kqueue_select import KqueueSelect
from typing import List, Callable, Any


class EventLoop:
    _callback_queue: deque[Handle | TimerHandle]
    _timer_callback_heap: List[TimerHandle]
    _select: KqueueSelect

    def __init__(self) -> None:
        self._callback_queue = deque()
        self._timer_callback_heap = []
        self._select = KqueueSelect()

    def push_callback(self, _callback: Callable, *_args: Any) -> None:
        handle = Handle(_callback, *_args)
        self._callback_queue.append(handle)

    def push_timer_callback(
        self, _secs: float, _callback: Callable, *_args: Any
    ) -> None:
        current_ts = time.monotonic()
        t_handle = TimerHandle(current_ts + _secs, _callback, *_args)
        heapq.heappush(self._timer_callback_heap, t_handle)

    def _round(self) -> None:
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

    def stop(self) -> None:
        self._stop = True

    def run_until_stop(self) -> None:
        self._stop = False
        while not self._stop:
            self._round()


_cur_running_loop = EventLoop()


def get_running_loop() -> EventLoop:
    return _cur_running_loop
