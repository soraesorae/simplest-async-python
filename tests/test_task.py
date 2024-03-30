from simplest_async import loop
from simplest_async import future
from simplest_async import task
import time


class TestTask:
    async def coro_sleep(self, _secs: float, _loop: loop.EventLoop):
        self._start_time = time.time()
        await task.sleep(_secs, _loop)
        self._end_time = time.time()
        _loop.stop()

    def test_sleep(self):
        _loop = loop.EventLoop()
        coro = self.coro_sleep(3, _loop)
        _ = task.Task(coro, _loop)
        _loop.run_until_stop()
        td = self._end_time - self._start_time
        assert 2.99 <= td <= 3.01
