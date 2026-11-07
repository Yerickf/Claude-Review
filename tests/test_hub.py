"""Corre com: uv run python -m tests.test_hub"""
from vision import config
from vision.hub import HubTracker
from vision.run import Pipeline
from tests import synth

CX = (config.HUB_RECT_MM[0] + config.HUB_RECT_MM[2]) / 2
CY = (config.HUB_RECT_MM[1] + config.HUB_RECT_MM[3]) / 2
FPS = 30.0


def run_logic():
    """Lógica pura: entra, roda, é tapada pela mão, sai."""
    t = HubTracker()
    now = 0.0
    out = []

    def frames(n, obs):
        nonlocal now
        for _ in range(n):
            out.extend(t.update(now, obs))
            now += 1 / FPS

    frames(7, {12: (CX, CY, 10.0)})
    assert out == [], "não pode entrar antes de %d frames" % config.ENTER_FRAMES
    frames(1, {12: (CX, CY, 10.0)})
    assert out == [("PIECE_ENTER", {"marker": 12})], out
    out.clear()

    frames(10, {12: (CX, CY, 10.0 + 52.0)})        # rodou ~52 graus: 1 passo
    assert out == [("DIAL_STEP", {"steps": 1})], out
    out.clear()

    frames(10, {12: (CX, CY, 10.0 - 40.0)})        # de 55 para -30: ~ -85 graus = -2 passos
    assert out == [("DIAL_STEP", {"steps": -2})], out
    out.clear()

    frames(15, {})                                 # mão tapa 0.5 s: não sai
    assert out == [], out
    frames(10, {12: (CX, CY, 10.0 - 40.0)})
    assert out == [], out

    frames(30, {})                                 # ausente 1 s: sai
    assert out == [("PIECE_EXIT", {"marker": 12})], out
    out.clear()

    frames(30, {13: (10.0, 10.0, 0.0)})            # peça fora do hub: ignorada
    assert out == [], out
    print("hub (lógica): ok")


def run_pipeline():
    """Imagens sintéticas -> deteção ArUco -> homografia -> eventos."""
    p = Pipeline()
    now = 0.0
    out = []
    for _ in range(10):
        ev, found, obs = p.step(synth.frame([(12, CX, CY, 0)]), now)
        out.extend(ev)
        now += 1 / FPS
    assert p.H is not None, "homografia não calculada"
    assert 12 in obs and abs(obs[12][0] - CX) < 3 and abs(obs[12][1] - CY) < 3, obs
    assert out == [("PIECE_ENTER", {"marker": 12})], out
    out.clear()

    # Rodar 90 graus no sentido anti-horário (np.rot90, k=1) = -90 graus = -2 passos.
    for _ in range(10):
        ev, _, obs = p.step(synth.frame([(12, CX, CY, 1)]), now)
        out.extend(ev)
        now += 1 / FPS
    assert out == [("DIAL_STEP", {"steps": -2})], (out, obs)
    print("pipeline (imagens sintéticas): ok")


if __name__ == "__main__":
    run_logic()
    run_pipeline()
