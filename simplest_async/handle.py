from typing import Callable, Any


class Handle:
    _callback: Callable

    def __init__(self, _callback: Callable, *_args: Any) -> None:
        self._callback = _callback
        self._args = _args

    def run(self) -> None:
        try:
            self._callback(*self._args)
        except:
            raise


class TimerHandle(Handle):
    _start_time: float

    def __init__(self, _start_time: float, _callback: Callable, *_args: Any) -> None:
        super().__init__(_callback, *_args)
        self._start_time = _start_time

    @property
    def start_time(self) -> float:
        return self._start_time

    @start_time.setter
    def start_time(self, _start_time: float) -> None:
        self._start_time = _start_time

    def __lt__(self, _rhs: Any) -> bool:
        return self._start_time < _rhs.start_time
