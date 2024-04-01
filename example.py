from simplest_async import socket_buffer
from simplest_async import socket_server
import sys


async def handler(read_buffer: socket_buffer.ReadBuffer):
    while True:
        data = await read_buffer.read_until(b"#\n")
        print(data)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        exit(f"Usage: python {sys.argv[0]} <addr> <port>")
    addr = sys.argv[1]
    port = int(sys.argv[2])
    server = socket_server.Server(addr, port, handler)
    server.run()
