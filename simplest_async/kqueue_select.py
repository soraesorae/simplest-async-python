import select
import socket
from simplest_async.handle import Handle
from typing import List, Tuple, Dict, Callable

EVENT_READ = 1 << 0
EVENT_WRITE = 1 << 1


class KqueueSelect:
    _kqueue: select.kqueue
    _read_callback: Dict[int, Handle]
    _write_callback: Dict[int, Handle]

    def __init__(self):
        self._kqueue = select.kqueue()
        self._max_events = 0
        self._read_callback = {}
        self._write_callback = {}

    def add_file_read_event(self, fd: int, _read_callback=None, *_args):
        # KQ_FILTER_READ = -1
        # KQ_FILTER_WRITE = -2
        # -1 | -2 = -1
        kev = select.kevent(
            ident=fd, filter=select.KQ_FILTER_READ, flags=select.KQ_EV_ADD
        )
        self._kqueue.control([kev], 0, 0)
        self._max_events += 1
        handle = Handle(_read_callback, _args)
        self._read_callback[fd] = handle

    def add_file_write_event(self, fd: int, _write_callback=None, *_args):
        kev = select.kevent(
            ident=fd, filter=select.KQ_FILTER_WRITE, flags=select.KQ_EV_ADD
        )
        self._kqueue.control([kev], 0, 0)
        self._max_events += 1
        handle = Handle(_write_callback, _args)
        self._write_callback[fd] = handle

    def del_file_read_event(self, fd: int):
        kev = select.kevent(
            ident=fd, filter=select.KQ_FILTER_READ, flags=select.KQ_EV_DELETE
        )
        self._kqueue.control([kev], 0, 0)
        self._max_events -= 1
        del self._read_callback[fd]

    def del_file_write_event(self, fd: int):
        kev = select.kevent(
            ident=fd, filter=select.KQ_FILTER_WRITE, flags=select.KQ_EV_DELETE
        )
        self._kqueue.control([kev], 0, 0)
        self._max_events -= 1
        del self._write_callback[fd]

    def select(self, _timeout: float | None) -> List[Tuple[int, int]]:
        _max_events = max(self._max_events, 1)  # to prevent ignoring timeout
        evs = self._kqueue.control(None, _max_events, _timeout)
        fd_events = []
        for ev in evs:
            fd = ev.ident
            kq_filter = ev.filter  # ev.filter can be -1 or -2
            filter = 0
            if kq_filter & select.KQ_FILTER_READ:
                filter = EVENT_READ
            elif kq_filter & select.KQ_FILTER_WRITE:
                filter = EVENT_WRITE

            fd_events.append((fd, filter))
        return fd_events
