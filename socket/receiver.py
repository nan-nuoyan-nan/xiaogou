import socket
import json
import threading


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
                with self._lock:
                    self._data[info.get("nano_id", "?")] = info
            except Exception:
                pass

    def get(self, nano_id=None):
        with self._lock:
            if nano_id is not None:
                return self._data.get(nano_id, {})
            return dict(self._data)
