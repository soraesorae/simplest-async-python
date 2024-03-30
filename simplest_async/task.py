from .loop import EventLoop
from .future import Future, FutureCancelled
from typing import Coroutine


class Task(Future):
    _loop: EventLoop
    _coroutine: Coroutine
    _current_wait_fut: Future | None

    def __init__(self, _coroutine: Coroutine, _loop: EventLoop):
        super().__init__(_loop)
        # TODO: check _coroutine is Coroutine
        self._coroutine = _coroutine
        self._current_wait_fut = None
        self._loop.push_callback(self._step)

    def cancel(self):
        if self._current_wait_fut is not None:
            self._current_wait_fut.cancel()
        self._is_cancelled = True

    def _step(self):
        try:
            res = self._coroutine.send(None)
        except StopIteration as e:
            super().set_result(e.value)
        except FutureCancelled:
            pass
        else:
            if isinstance(res, Future):
                self._current_wait_fut = res
                res.add_callback(self._wakeup)
            else:
                self._loop.push_callback(self._step)

    def _wakeup(self, _fut: Future):
        try:
            _fut.result()
        except:
            pass
        else:
            self._step()


async def sleep(_secs: float, _loop: EventLoop):
    fut = Future(_loop)
    _loop.push_timer_callback(_secs, fut.set_result, None)
    await fut
