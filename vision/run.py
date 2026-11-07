import argparse
import math
import os
import time

import cv2
import numpy as np

from . import config
from .calib import homography_from_anchors, hub_polygon_px, to_board
from .events import EventSender
from .hub import HubTracker


class Pipeline:
    """Um frame entra, saem eventos. Separado do ciclo da câmara para poder ser testado."""

    def __init__(self):
        dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        params = cv2.aruco.DetectorParameters()
        params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
        self.detector = cv2.aruco.ArucoDetector(dictionary, params)
        self.tracker = HubTracker()
        self.H = None
        self._n = 0

    def step(self, frame, now):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame
        corners, ids, _ = self.detector.detectMarkers(gray)
        found = {}
        if ids is not None:
            for c, i in zip(corners, ids.flatten()):
                found[int(i)] = c.reshape(4, 2)

        # Recalcula a homografia a cada 15 frames se as 4 âncoras estiverem visíveis
        # (tolera pancadas na mesa); se não estiverem, mantém a última.
        if self.H is None or self._n % 15 == 0:
            H = homography_from_anchors(found)
            if H is not None:
                self.H = H
        self._n += 1

        observed = {}
        if self.H is not None:
            for m, c in found.items():
                if m in config.PIECE_IDS:
                    pts = to_board(self.H, c)           # 4 cantos em mm
                    cx, cy = pts.mean(axis=0)
                    # Ângulo medido já no plano do tabuleiro: corrige a perspetiva da câmara.
                    ang = math.degrees(math.atan2(pts[1][1] - pts[0][1], pts[1][0] - pts[0][0]))
                    observed[m] = (float(cx), float(cy), ang)

        events = self.tracker.update(now, observed)
        return events, found, observed


def draw_debug(frame, pipe, found, observed, last_events):
    if found:
        cv2.aruco.drawDetectedMarkers(frame, [c.reshape(1, 4, 2) for c in found.values()],
                                      np.array(list(found.keys()), dtype=np.int32).reshape(-1, 1))
    if pipe.H is not None:
        poly = hub_polygon_px(pipe.H).astype("int32")
        cv2.polylines(frame, [poly], True, (0, 200, 0), 2)
    lines = [
        "H: %s" % ("ok" if pipe.H is not None else "faltam ancoras 40-43"),
        "no hub: %s" % pipe.tracker.current,
        "pecas vistas: %s" % sorted(observed.keys()),
    ] + last_events[-3:]
    for i, t in enumerate(lines):
        cv2.putText(frame, t, (10, 25 + 24 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)


def open_capture(args):
    if args.video:
        return cv2.VideoCapture(args.video)
    cap = cv2.VideoCapture(args.cam, cv2.CAP_DSHOW) if os.name == "nt" else cv2.VideoCapture(args.cam)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    return cap


def main():
    ap = argparse.ArgumentParser(description="Câmara -> eventos do hub")
    ap.add_argument("--cam", type=int, default=0, help="índice da câmara (usa detect_test --list)")
    ap.add_argument("--video", help="ficheiro de vídeo em vez da câmara")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--show", action="store_true", help="janela de debug (q sai, r recalibra, s grava frame)")
    ap.add_argument("--print", action="store_true", help="imprime os eventos no terminal")
    ap.add_argument("--url", default="ws://127.0.0.1:8000/ws/in")
    args = ap.parse_args()

    cap = open_capture(args)
    if not cap.isOpened():
        raise SystemExit("Não consegui abrir a câmara. Corre: uv run python -m vision.detect_test --list")

    sender = EventSender(args.url, echo=args.print)
    pipe = Pipeline()
    last_events = []
    fails = 0
    print("A correr. Ctrl+C para parar." + (" Janela: q sai." if args.show else ""))
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                fails += 1
                if args.video or fails > 100:
                    break
                time.sleep(0.05)
                continue
            fails = 0
            events, found, observed = pipe.step(frame, time.monotonic())
            for type_, payload in events:
                sender.send(type_, payload)
                last_events.append("%s %s" % (type_, payload))
            if args.show:
                draw_debug(frame, pipe, found, observed, last_events)
                cv2.imshow("vision", frame)
                k = cv2.waitKey(1) & 0xFF
                if k == ord("q"):
                    break
                if k == ord("r"):
                    pipe.H = None
                if k == ord("s"):
                    name = "recordings/frame-%d.png" % int(time.time())
                    cv2.imwrite(name, frame)
                    print("guardado", name)
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
