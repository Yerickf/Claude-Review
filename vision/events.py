import json
import time

try:
    from websockets.sync.client import connect
except ImportError:  # sem a biblioteca, só imprime
    connect = None


class EventSender:
    """Envia eventos para o servidor sem nunca deitar abaixo o ciclo da câmara."""

    def __init__(self, url="ws://127.0.0.1:8000/ws/in", source="camera", echo=False):
        self.url = url
        self.source = source
        self.echo = echo
        self._ws = None
        self._next_try = 0.0

    def _ensure(self):
        if self._ws is not None:
            return True
        if connect is None or time.monotonic() < self._next_try:
            return False
        try:
            self._ws = connect(self.url, open_timeout=0.5)
            return True
        except Exception:
            self._ws = None
            self._next_try = time.monotonic() + 2.0
            return False

    def send(self, type_, payload=None):
        ev = {"type": type_, "payload": payload or {}, "source": self.source}
        if self.echo:
            print(json.dumps(ev, ensure_ascii=False))
        if not self._ensure():
            return False
        try:
            self._ws.send(json.dumps(ev))
            return True
        except Exception:
            self._ws = None
            return False
