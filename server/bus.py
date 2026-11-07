import json
import time
from pathlib import Path

VALID_TYPES = {"PIECE_ENTER", "PIECE_EXIT", "DIAL_STEP", "RESET"}


class EventBus:
    """Numera os eventos (seq), guarda-os em memória e em JSONL. Sem rede, por isso é testável."""

    def __init__(self, log_file, resume=False):
        self.log_file = Path(log_file)
        self.log = []
        self.seq = 0
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        if self.log_file.exists():
            if resume:
                self._load()
            else:
                stamp = time.strftime("%Y%m%d-%H%M%S")
                self.log_file.rename(self.log_file.with_name("events-%s.jsonl" % stamp))
        self.log_file.touch()

    def _load(self):
        for line in self.log_file.read_text(encoding="utf-8").splitlines():
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            self.log.append(ev)
            self.seq = max(self.seq, int(ev.get("seq", 0)))

    def add(self, raw):
        """Valida e regista. Devolve o evento completo, ou None se for inválido."""
        if not isinstance(raw, dict) or raw.get("type") not in VALID_TYPES:
            return None
        payload = raw.get("payload")
        self.seq += 1
        ev = {
            "seq": self.seq,
            "ts": int(time.time() * 1000),
            "source": str(raw.get("source", "unknown")),
            "type": raw["type"],
            "payload": payload if isinstance(payload, dict) else {},
        }
        self.log.append(ev)
        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        return ev
