import select


class KqueueSelect:
    _kqueue = select.kqueue

    def __init__(self):
        self._kqueue = select.kqueue()
