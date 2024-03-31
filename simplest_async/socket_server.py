from .loop import EventLoop, get_running_loop
import socket


class Server:
    _addr: str
    _port: int
    _backlog: int
    _loop: EventLoop
    _srv_sock: socket.socket

    def __init__(self, _addr: str, _port: int) -> None:
        self._loop = get_running_loop()
        self._addr = _addr
        self._port = _port
        self._backlog = 256

    def run(self) -> None:
        self._srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._srv_sock.bind((self._addr, self._port))
        self._srv_sock.listen(self._backlog)

        self._srv_sock.setblocking(False)
        self._srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self._loop.add_file_read_event(self._srv_sock.fileno(), self._accept_handler)

    def _accept_handler(self) -> None:
        for _ in range(self._backlog):
            try:
                client_sock, _ = self._srv_sock.accept()
                # read_buffer = ReadBuffer(loop, cleint_sock)
                # writer_buffer = WriteBuffer(loop, client_sock)
                # self._loop.add_file_read_event(client_sock.fileno(), )
            except BlockingIOError:
                break
