import socket
import json
import threading
import time


class Receiver:
    def __init__(self, port=10001):
        self._data = {}
        self._lock = threading.Lock()

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(("0.0.0.0", port))

        self._thread = threading.Thread(target=self._listen, daemon=True)
        self._thread.start()

    def _listen(self):
        while True:
            try:
                raw, _ = self._sock.recvfrom(4096)
                info = json.loads(raw.decode())
