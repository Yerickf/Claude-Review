import math

from . import config
from .dial import circ_diff, dial_steps


class HubTracker:
    """Transforma observações por frame em eventos estáveis.

    Entrada de update(): {id: (x_mm, y_mm, ângulo)} só com as peças-tema.
    Saída: lista de (tipo, payload) com PIECE_ENTER, PIECE_EXIT e DIAL_STEP.
    """

    def __init__(self, hub_rect=None):
        self.rect = hub_rect or config.HUB_RECT_MM
        self.cx = (self.rect[0] + self.rect[2]) / 2
        self.cy = (self.rect[1] + self.rect[3]) / 2
        self.current = None
        self._cand = None
        self._cand_n = 0
        self._missing_since = None
        self._ref = 0.0
        self._last_angle = None
        self._stable_n = 0

    def _inside(self, x, y):
        x0, y0, x1, y1 = self.rect
        return x0 <= x <= x1 and y0 <= y <= y1

    def update(self, now, observed):
        events = []
        in_hub = {m: v for m, v in observed.items() if self._inside(v[0], v[1])}
        if self.current is None:
            self._try_enter(in_hub, events)
        else:
            self._track_current(now, in_hub, events)
        return events

    def _try_enter(self, in_hub, events):
        if not in_hub:
            self._cand, self._cand_n = None, 0
            return
        m = min(in_hub, key=lambda k: math.hypot(in_hub[k][0] - self.cx, in_hub[k][1] - self.cy))
        if m == self._cand:
            self._cand_n += 1
        else:
            self._cand, self._cand_n = m, 1
        if self._cand_n >= config.ENTER_FRAMES:
            self.current = m
            self._ref = in_hub[m][2]
            self._last_angle = in_hub[m][2]
            self._stable_n = 0
            self._missing_since = None
            self._cand, self._cand_n = None, 0
            events.append(("PIECE_ENTER", {"marker": m}))

    def _track_current(self, now, in_hub, events):
        v = in_hub.get(self.current)
        if v is None:
            # A mão tapa o marcador a meio do gesto: só sai se estiver ausente tempo suficiente.
            if self._missing_since is None:
                self._missing_since = now
            elif (now - self._missing_since) * 1000.0 >= config.EXIT_MS:
                events.append(("PIECE_EXIT", {"marker": self.current}))
                self.current = None
                self._missing_since = None
                self._stable_n = 0
            return
        self._missing_since = None
        angle = v[2]
        if self._last_angle is not None and abs(circ_diff(angle, self._last_angle)) <= config.DIAL_STABLE_TOL_DEG:
            self._stable_n += 1
        else:
            self._stable_n = 0
        self._last_angle = angle
        if self._stable_n >= config.DIAL_STABLE_FRAMES:
            steps, self._ref = dial_steps(self._ref, angle, config.DETENT_DEG)
            if steps:
                events.append(("DIAL_STEP", {"steps": steps}))
            self._stable_n = 0
