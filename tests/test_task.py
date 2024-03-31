from simplest_async import loop
from simplest_async import future
from simplest_async import task
import time


class TestTask:
    async def coro_sleep(self, _secs: float):
        self._start_time = time.time()
        await task.sleep(_secs)
        self._end_time = time.time()
        loop.get_running_loop().stop()

    def test_sleep(self):
        _loop = loop.get_running_loop()
        coro = self.coro_sleep(3.0)
        _ = task.Task(coro, _loop)
        _loop.run_until_stop()
        td = self._end_time - self._start_time
        assert 2.99 <= td <= 3.01
