import math


def angle_deg(p0, p1):
    """Ângulo (graus) do vetor p0 -> p1. Com y para baixo, positivo = sentido horário."""
    return math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))


def circ_diff(a, b):
    """Diferença mais curta a - b, entre -180 e 180 (trata o salto 359 -> 0)."""
    return (a - b + 180.0) % 360.0 - 180.0


def dial_steps(ref_deg, new_deg, detent=45.0):
    """Quantos detentes rodou desde o ângulo de referência.

    Devolve (passos, nova_referência). A referência avança sempre em múltiplos
    exatos do detente, por isso o erro da câmara nunca se acumula.
    """
    delta = circ_diff(new_deg, ref_deg)
    steps = round(delta / detent)
    return steps, ref_deg + steps * detent


if __name__ == "__main__":
    assert dial_steps(0, 50)[0] == 1
    assert dial_steps(0, -100)[0] == -2
    assert dial_steps(350, 10)[0] == 0          # 20 graus: abaixo de meio detente
    assert dial_steps(350, 40)[0] == 1          # atravessa o 0/360
    assert dial_steps(10, 340)[0] == -1         # atravessa o 0/360 para trás
    assert dial_steps(0, 20)[0] == 0            # ruído pequeno não conta
    print("dial.py: ok")
