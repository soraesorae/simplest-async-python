from typing import Callable


class Handle:
    _callback: Callable

    def __init__(self, _callback: Callable, *_args):
        self._callback = _callback
        self._args = _args

    def run(self):
        try:
            self._callback(*self._args)
        except:
            raise


class TimerHandle(Handle):
    _start_time: int

    def __init__(self, _start_time: int, _callback, *_args):
        super().__init__(_callback, *_args)
        self._start_time = _start_time

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, _start_time: int):
        self._start_time = _start_time
