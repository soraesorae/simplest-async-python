from .loop import EventLoop
from .future import Future


class Task(Future):
    _loop: EventLoop

    def __init__(self, _loop: EventLoop):
        super().__init__(_loop)
