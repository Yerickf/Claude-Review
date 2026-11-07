# Tudo em milímetros, no referencial do TABULEIRO.
# Origem (0, 0) = canto do tabuleiro que fica no canto superior esquerdo da imagem
# da câmara; x cresce para a direita, y cresce para baixo.

SQUARE_MM = 55.0                 # MEDE o lado de uma casa do teu tabuleiro
BOARD_MM = 8 * SQUARE_MM

# Centro de cada âncora (ID 40-43), medido a partir da origem. MEDE COM UMA RÉGUA
# depois de as colares fora dos cantos. Estes valores são só um exemplo.
ANCHOR_MM = {
    40: (-45.0, -45.0),                       # canto superior esquerdo
    41: (BOARD_MM + 45.0, -45.0),             # canto superior direito
    42: (BOARD_MM + 45.0, BOARD_MM + 45.0),   # canto inferior direito
    43: (-45.0, BOARD_MM + 45.0),             # canto inferior esquerdo
}

# IDs das peças-tema (um por tema).
PIECE_IDS = range(10, 17)

# Hub = as 4 casas centrais (d4, e4, d5, e5): (x0, y0, x1, y1).
HUB_RECT_MM = (3 * SQUARE_MM, 3 * SQUARE_MM, 5 * SQUARE_MM, 5 * SQUARE_MM)

# Estabilidade (afina nos testes; a 30 fps, 8 frames = ~270 ms).
ENTER_FRAMES = 8          # frames seguidos com a peça no hub para "entrar"
EXIT_MS = 800             # tempo sem a peça no hub para "sair"
DETENT_DEG = 45.0         # 1 passo do dial = 45 graus
DIAL_STABLE_FRAMES = 5    # frames com o ângulo parado antes de ler o dial
DIAL_STABLE_TOL_DEG = 3.0 # o que conta como "parado"
