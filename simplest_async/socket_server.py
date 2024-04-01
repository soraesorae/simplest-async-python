from .loop import EventLoop, get_running_loop
from .task import Task
from .socket_buffer import ReadBuffer
import socket
from typing import Coroutine, Callable, Any


class Server:
    _addr: str
    _port: int
    _backlog: int
    _loop: EventLoop
    _srv_sock: socket.socket

    def __init__(
        self, _addr: str, _port: int, _client_handler: Callable[[ReadBuffer], Coroutine]
    ) -> None:
        self._loop = get_running_loop()
        self._addr = _addr
        self._port = _port
        self._backlog = 256
        self._client_handler = _client_handler

    def run(self) -> None:
        self._srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._srv_sock.bind((self._addr, self._port))
        self._srv_sock.listen(self._backlog)

        self._srv_sock.setblocking(False)
        self._srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self._loop.add_file_read_event(self._srv_sock.fileno(), self._accept_handler)
        self._loop.run_until_stop()

    def _accept_handler(self) -> None:
        for _ in range(self._backlog):
            try:
                client_sock, _ = self._srv_sock.accept()
                client_sock.setblocking(False)
                read_buffer = ReadBuffer(self._loop, client_sock)
                Task(self._client_handler(read_buffer), self._loop)
                # read_buffer = ReadBuffer(loop, cleint_sock)
                # writer_buffer = WriteBuffer(loop, client_sock)
                # self._loop.add_file_read_event(client_sock.fileno(), )
            except BlockingIOError:
                break

    def __del__(self):
        self._srv_sock.close()
        # client sock close
