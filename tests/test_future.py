from simplest_async import loop
from simplest_async import future


class TestFuture:
    async def coro(self):
        _loop = loop.EventLoop()
        fut = future.Future(_loop=_loop)
        await fut

    def test_set_reseult(self):
        co = self.coro()
        co.send(None)
