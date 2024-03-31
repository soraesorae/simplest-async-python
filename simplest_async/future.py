from .loop import EventLoop
from typing import List, Callable, Any

_PENDING = 0
_FINISHED = 1
_CANCELLED = -1


class ResultNotExist(Exception):
    pass


class FutureCancelled(Exception):
    pass


class AwaitBeforeDone(Exception):
    pass


class Future:
    _STATE = _PENDING
    _callbacks: List[Callable]
    _loop: EventLoop

    def __init__(self, _loop: EventLoop) -> None:
        self._loop = _loop
        self._callbacks = []

    def _run_callbacks(self) -> None:
        for callback in self._callbacks:
            self._loop.push_callback(callback, self)

    def add_callback(self, _callback: Callable) -> None:
        self._callbacks.append(_callback)

    def set_result(self, _result: Any) -> None:
        self._result = _result
        self._STATE = _FINISHED
        self._run_callbacks()

    def cancel(self) -> None:
        if self._STATE == _PENDING:
            self._STATE = _CANCELLED
            self._run_callbacks()

    def result(self) -> None:
        if self._STATE == _PENDING:
            raise ResultNotExist()
        elif self._STATE == _CANCELLED:
            raise FutureCancelled()
        return self._result

    def is_done(self) -> bool:
        if self._STATE == _PENDING:
            return False
        return True

    def __await__(self) -> Any:
        if not self.is_done():
            yield self
        if not self.is_done():
            raise AwaitBeforeDone()
        return self.result()
