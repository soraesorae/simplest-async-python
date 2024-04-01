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
        if len(buf) == 0:
            raise  # check socket disconnected
        self._buffer.extend(buf)
        if self._wait_data:
            self._wait_data.set_result(None)
        self._wait_data = None

    async def read(self, n: int) -> bytes:
        if len(self._buffer) < n:
            n = len(self._buffer)
        buf = self._buffer[:n]
        del self._buffer[:n]
        return bytes(buf)

    async def read_until(self, sep: bytes) -> bytes:
        buf = bytearray()
        while True:
            ret = self._buffer.find(sep)
            if ret == -1:  # not found
                buf.extend(self._buffer)
                self._buffer.clear()
                self._wait_data = Future(self._loop)
                await self._wait_data
            else:
                right_index = ret - len(sep)
                buf.extend(self._buffer[:right_index])
                del self._buffer[:right_index]
                break
        return bytes(buf)
