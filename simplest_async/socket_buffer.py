from .loop import EventLoop
import socket


class ReadBuffer:
    _loop: EventLoop
    _sock: socket.socket

    def __init__(self, _loop: EventLoop, _sock: socket.socket) -> None:
        self._loop = _loop
        self._sock = _sock
