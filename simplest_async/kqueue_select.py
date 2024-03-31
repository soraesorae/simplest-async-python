import select
import socket
from typing import List, Tuple, Dict, Callable

EVENT_READ = 1 << 0
EVENT_WRITE = 1 << 1


class KqueueSelect:
    _kqueue: select.kqueue
    _read_callback: Handle
    _write_callback: Handle

    def __init__(self):
        self._kqueue = select.kqueue()
        self._max_events = 0
        self._file_info = {}

    def add_file_event(self, fd: int, filter: int, data=None):
        # KQ_FILTER_READ = -1
        # KQ_FILTER_WRITE = -2
        # -1 | -2 = -1
        if filter & EVENT_READ:
            kev = select.kevent(
                ident=fd, filter=select.KQ_FILTER_READ, flags=select.KQ_EV_ADD
            )
            self._kqueue.control([kev], 0, 0)
            self._max_events += 1
        if filter & EVENT_WRITE:
            kev = select.kevent(
                ident=fd, filter=select.KQ_FILTER_WRITE, flags=select.KQ_EV_ADD
            )
            self._kqueue.control([kev], 0, 0)
            self._max_events += 1

    def del_file_event(self, fd, filter: int, data=None):
        if filter & EVENT_READ:
            kev = select.kevent(
                ident=fd, filter=select.KQ_FILTER_READ, flags=select.KQ_EV_DELETE
            )
            self._kqueue.control([kev], 0, 0)
            self._max_events += 1
        if filter & EVENT_WRITE:
            kev = select.kevent(
                ident=fd, filter=select.KQ_FILTER_WRITE, flags=select.KQ_EV_DELETE
            )
            self._kqueue.control([kev], 0, 0)
            self._max_events += 1

    def select(self, _timeout: float | None) -> List[Tuple[int, int]]:
        _max_events = max(self._max_events, 1)  # to prevent ignoring timeout
        evs = self._kqueue.control(None, _max_events, _timeout)
        fd_events = []
        for ev in evs:
            fd = ev.ident
            kq_filter = ev.filter # ev.filter can be -1 or -2
            filter = 0
            if kq_filter & select.KQ_FILTER_READ:
                filter = EVENT_READ
            elif kq_filter & select.KQ_FILTER_WRITE:
                filter = EVENT_WRITE

            fd_events.append((fd, filter))
        return fd_events
