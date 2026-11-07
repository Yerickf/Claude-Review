"""Corre com: uv run python -m tests.test_bus"""
import json
import tempfile
from pathlib import Path

from server.bus import EventBus

with tempfile.TemporaryDirectory() as d:
    f = Path(d) / "events.jsonl"
    b = EventBus(f)
    e1 = b.add({"type": "PIECE_ENTER", "payload": {"marker": 11}, "source": "camera"})
    e2 = b.add({"type": "DIAL_STEP", "payload": {"steps": -1}})
    assert (e1["seq"], e2["seq"]) == (1, 2)
    assert e2["source"] == "unknown"
    assert b.add({"type": "NAO_EXISTE"}) is None
    assert b.add("lixo") is None
    assert len(f.read_text(encoding="utf-8").splitlines()) == 2

    b2 = EventBus(f, resume=True)            # retoma depois de um crash
    assert b2.seq == 2 and len(b2.log) == 2
    assert b2.add({"type": "RESET"})["seq"] == 3

    b3 = EventBus(f)                         # arranque normal: roda o log antigo
    assert b3.log == [] and b3.seq == 0
    assert len(list(Path(d).glob("events-*.jsonl"))) == 1
    print("bus: ok")
