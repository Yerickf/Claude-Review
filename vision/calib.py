import cv2
import numpy as np

from . import config


def marker_center(corners):
    return np.asarray(corners, dtype=np.float32).reshape(4, 2).mean(axis=0)


def homography_from_anchors(found):
    """found: {id: cantos 4x2 em píxeis}. Devolve H (píxeis -> mm) ou None
    se as 4 âncoras não estiverem todas visíveis."""
    ids = [i for i in config.ANCHOR_MM if i in found]
    if len(ids) < 4:
        return None
    src = np.array([marker_center(found[i]) for i in ids], np.float32)
    dst = np.array([config.ANCHOR_MM[i] for i in ids], np.float32)
    H, _ = cv2.findHomography(src, dst, 0)
    return H


def to_board(H, pts):
    """Aplica uma matriz 3x3 a uma lista de pontos (x, y)."""
    arr = np.asarray(pts, np.float32).reshape(-1, 1, 2)
    return cv2.perspectiveTransform(arr, H).reshape(-1, 2)


def hub_polygon_px(H):
    """Os 4 cantos do hub desenhados na imagem (para confirmar a calibração)."""
    x0, y0, x1, y1 = config.HUB_RECT_MM
    quad = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
    return to_board(np.linalg.inv(H), quad)
