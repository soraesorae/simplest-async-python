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

    def add_file_read_event(
        self, _fd: int, _read_callback: Callable, *_args: Any
    ) -> None:
        self._select.add_file_read_event(_fd, _read_callback, *_args)

    def add_file_write_event(
        self, _fd: int, _write_callback: Callable, *_args: Any
    ) -> None:
        self._select.add_file_write_event(_fd, _write_callback, *_args)

    def _round(self) -> None:
        current_ts = time.monotonic()

        while (
            len(self._timer_callback_heap) > 0
            and self._timer_callback_heap[0].start_time <= current_ts
        ):
            timer_callback_handle = heapq.heappop(self._timer_callback_heap)
            self._callback_queue.append(timer_callback_handle)

        timeout = None
        if self._callback_queue:
            timeout = 0.0
        elif self._timer_callback_heap:
            timeout = max(0.0, self._timer_callback_heap[0].start_time - current_ts)

        events = self._select.select(timeout)
        # event -> _callback_queue

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
