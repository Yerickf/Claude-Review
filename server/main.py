import asyncio
import json
import os
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .bus import EventBus

ROOT = Path(__file__).resolve().parent.parent

app = FastAPI(title="Tabuleiro Vivo")
bus = EventBus(ROOT / "recordings" / "events.jsonl", resume=os.environ.get("RESUME") == "1")
viewers = set()  # palcos/consolas: recebem tudo. Quem só envia (a câmara) usa /ws/in.


async def publish(raw):
    ev = bus.add(raw)
    if ev is None:
        return
    msg = json.dumps({"kind": "event", "event": ev}, ensure_ascii=False)
    for ws in list(viewers):
        try:
            await asyncio.wait_for(ws.send_text(msg), timeout=1.0)
        except Exception:
            viewers.discard(ws)  # um cliente lento nunca trava os outros


async def receive(ws, default_source):
    text = await ws.receive_text()
    try:
        raw = json.loads(text)
    except ValueError:
        return
    if isinstance(raw, dict):
        raw.setdefault("source", default_source)
        await publish(raw)


@app.websocket("/ws")
async def ws_viewer(ws: WebSocket):
    await ws.accept()
    snapshot = json.dumps({"kind": "snapshot", "events": bus.log}, ensure_ascii=False)
    viewers.add(ws)  # antes de enviar o snapshot, para não perder eventos pelo caminho
    try:
        await ws.send_text(snapshot)
        while True:
            await receive(ws, "stage")
    except WebSocketDisconnect:
        pass
    finally:
        viewers.discard(ws)


@app.websocket("/ws/in")
async def ws_publisher(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            await receive(ws, "camera")
    except WebSocketDisconnect:
        pass


@app.get("/")
def root():
    return RedirectResponse("/stage/")


@app.get("/api/log")
def get_log():
    return bus.log


app.mount("/stage", StaticFiles(directory=ROOT / "stage", html=True), name="stage")
