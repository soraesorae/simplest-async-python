import select

EVENT_READ = 1 << 0
EVENT_WRITE = 1 << 1


class KqueueSelect:
    _kqueue: select.kqueue

    def __init__(self):
        self._kqueue = select.kqueue()
        self._max_events = 0

    def add_file_event(self, fd: int, filter: int, data=None):
        kqueue_fliter = 0
        if filter & EVENT_READ:
            kqueue_fliter |= select.KQ_FILTER_READ
            self._max_events += 1
        if filter & EVENT_WRITE:
            kqueue_fliter |= select.KQ_FILTER_WRITE
            self._max_events += 1

        kev = select.kevent(ident=fd, filter=kqueue_fliter, flags=select.KQ_EV_ADD)
        self._kqueue.control([kev], 0, 0)

    def del_file_event(self, fd, filter: int, data=None):
        kqueue_filter = 0
        if filter & EVENT_READ:
            kqueue_filter |= select.KQ_FILTER_READ
            self._max_events -= 1
        if filter & EVENT_WRITE:
            kqueue_filter |= select.KQ_FILTER_WRITE
            self._max_events -= 1

        kev = select.kevent(ident=fd, filter=kqueue_filter, flags=select.KQ_EV_DELETE)
        self._kqueue.control([kev], 0, 0)

    def select(self, _timeout: float | None):
        _max_events = max(self._max_events, 1)  # to prevent ignoring timeout
        evs = self._kqueue.control(None, _max_events, _timeout)
        fd_events = []
        for ev in evs:
            fd = ev.ident
            filter = ev.filter
            fd_events.append((fd, filter))
