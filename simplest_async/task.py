from .loop import EventLoop
from .future import Future
from typing import Coroutine


class Task(Future):
    _loop: EventLoop
    _coroutine: Coroutine
    _current_wait_fut: Future | None

    def __init__(self, _loop: EventLoop, _coroutine: Coroutine):
        super().__init__(_loop)
        # TODO: check _coroutine is Coroutine
        self._coroutine = _coroutine
        self._current_wait_fut = None

    def _step(self):
        try:
            res = self._coroutine.send(None)
        except StopIteration as e:
            pass
        else:
            if isinstance(res, Future):
                self._current_wait_fut = res
                res.add_callback(self._wakeup)

    def _wakeup(self, _fut: Future):
        raise NotImplementedError()
