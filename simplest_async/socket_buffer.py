from .loop import EventLoop
from .future import Future
import socket


class ReadBuffer:
    _loop: EventLoop
    _sock: socket.socket
    _buffer: bytearray
    _recv_size = 4096
    _wait_data: Future | None

    def __init__(self, _loop: EventLoop, _sock: socket.socket) -> None:
        self._loop = _loop
        self._sock = _sock
        self._buffer = bytearray()
        self._wait_data = None

        self._loop.add_file_read_event(self._sock.fileno(), self._read_data)

    def _read_data(self) -> None:
        buf = self._sock.recv(self._recv_size)
        self._buffer.extend(buf)

    async def read(self, n: int) -> bytes:
        if len(self._buffer) < n:
            n = len(self._buffer)
        buf = self._buffer[:n]
        del self._buffer[:n]
        return bytes(buf)
