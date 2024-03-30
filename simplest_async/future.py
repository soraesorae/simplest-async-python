from .loop import EventLoop
from typing import List, Callable

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

    def __init__(self, _loop: EventLoop):
        self._loop = _loop
        self._callbacks = []

    def _run_callbacks(self):
        raise NotImplementedError()

    def add_callback(self, _callback: Callable):
        self._callbacks.append(_callback)

    def set_result(self, _result):
        self._result = _result
        self._STATE = _FINISHED
        self._run_callbacks()

    def cancel(self):
        if self._STATE == _PENDING:
            self._STATE = _CANCELLED
            self._run_callbacks()

    def result(self):
        if self._STATE == _PENDING:
            raise ResultNotExist()
        elif self._STATE == _CANCELLED:
            raise FutureCancelled()
        return self._result

    def is_done(self) -> bool:
        if self._STATE == _PENDING:
            return False
        return True

    def __await__(self):
        if not self.is_done():
            yield self
        if not self.is_done():
            raise AwaitBeforeDone()
        return self.result()
