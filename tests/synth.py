"""Gera frames sintéticos (tabuleiro visto de cima a 2 px/mm) para testar a visão sem câmara."""
import cv2
import numpy as np

from vision import config

SCALE = 2.0          # píxeis por mm
OFFSET = (200, 200)  # deslocamento da origem do tabuleiro na imagem
SIZE = (1400, 1400)
DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)


def _marker(mid, mm, rot90=0):
    side = int(mm * SCALE)
    m = cv2.aruco.generateImageMarker(DICT, mid, side)
    m = np.rot90(m, rot90)
    pad = int(0.18 * side)
    return cv2.copyMakeBorder(m, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=255)


def _paste(canvas, img, cx_mm, cy_mm):
    h, w = img.shape
    x = int(OFFSET[0] + cx_mm * SCALE - w / 2)
    y = int(OFFSET[1] + cy_mm * SCALE - h / 2)
    canvas[y:y + h, x:x + w] = img


def frame(pieces=()):
    """pieces: lista de (id, x_mm, y_mm, rot90). Devolve imagem BGR."""
    canvas = np.full(SIZE, 255, np.uint8)
    for mid, (x, y) in config.ANCHOR_MM.items():
        _paste(canvas, _marker(mid, 50), x, y)
    for mid, x, y, rot in pieces:
        _paste(canvas, _marker(mid, 22, rot), x, y)
    return cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)
