"""Gera tools/marcadores.pdf com os marcadores ArUco no tamanho exato (300 dpi).

Página 1: IDs 10-16 (peças-tema), 2 cópias de cada, quadrado de 30 mm (marcador de 22 mm + margem branca).
Página 2: IDs 40-43 (âncoras), quadrado de 60 mm (marcador de 50 mm + margem branca).
Imprime a 100% ("tamanho real"), nunca "ajustar à página".
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

DPI = 300
MM = DPI / 25.4
D = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
OUT = Path(__file__).resolve().parent / "marcadores.pdf"


def with_margin(mid, marker_mm, margin_mm):
    m = cv2.aruco.generateImageMarker(D, mid, round(marker_mm * MM))
    p = round(margin_mm * MM)
    m = cv2.copyMakeBorder(m, p, p, p, p, cv2.BORDER_CONSTANT, value=255)
    cv2.rectangle(m, (0, 0), (m.shape[1] - 1, m.shape[0] - 1), 170, 1)  # linha de corte
    return m


def page(tiles):
    H, W = 3508, 2480  # A4 a 300 dpi
    margin, gap, label = round(10 * MM), round(8 * MM), 60
    canvas = np.full((H, W), 255, np.uint8)
    x = y = margin
    row_h = 0
    for mid, t in tiles:
        h, w = t.shape
        if x + w > W - margin:
            x, y, row_h = margin, y + row_h + label + gap, 0
        canvas[y:y + h, x:x + w] = t
        cv2.putText(canvas, "ID %d" % mid, (x, y + h + 35), cv2.FONT_HERSHEY_SIMPLEX, 1.0, 0, 2)
        x += w + gap
        row_h = max(row_h, h)
    return Image.fromarray(canvas)


if __name__ == "__main__":
    small = [(i, with_margin(i, 22, 4)) for i in range(10, 17) for _ in range(2)]
    big = [(i, with_margin(i, 50, 5)) for i in (40, 41, 42, 43)]
    p1, p2 = page(small), page(big)
    p1.save(OUT, save_all=True, append_images=[p2], resolution=DPI)
    print("criado", OUT)
