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

    def close(self):
        pass

    def _read_data(self) -> None:
        try:
            buf = self._sock.recv(self._recv_size)
        except BlockingIOError:
            raise
        if len(buf) == 0:
            raise  # check socket disconnected
        self._buffer.extend(buf)
        if self._wait_data is not None:
            self._wait_data.set_result(None)
            self._wait_data = None

    async def read(self, n: int) -> bytes:
        if len(self._buffer) == 0:
            if self._wait_data is None:
                self._wait_data = Future(self._loop)
            await self._wait_data
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
                if self._wait_data is None:
                    self._wait_data = Future(self._loop)
                await self._wait_data
            else:
                right_index = ret + len(sep)
                buf.extend(self._buffer[:right_index])
                del self._buffer[:right_index]
                break
        return bytes(buf)


class WriteBuffer:
    _loop: EventLoop
    _sock: socket.socket
    _buffer: bytearray
    _wait: Future | None

    def __init__(self, _loop: EventLoop, _sock: socket.socket) -> None:
        self._loop = _loop
        self._sock = _sock
        self._buffer = bytearray()
        self._wait = None

        self._loop.add_file_write_event(self._sock.fileno(), self._can_write)

    def _can_write(self) -> None:
        if self._wait is not None:
            self._wait.set_result(None)
            self._wait = None

    async def write(self, _data: bytes) -> None:
        data = bytearray(_data)
        while True:
            n = self._sock.send(data)
            if n < len(data):
                del data[:n]
                self._wait = Future(self._loop)
                await self._wait
            else:
                break
