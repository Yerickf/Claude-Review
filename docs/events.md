# Contrato de eventos

Tudo o que acontece (câmara, teclado) vira um evento com este formato:

```json
{ "seq": 17, "ts": 1731000000000, "source": "camera", "type": "PIECE_ENTER", "payload": { "marker": 12 } }
```

- `seq`: atribuído **só pelo servidor**, sempre crescente. Define a ordem.
- `ts`: milissegundos desde 1970, relógio do servidor.
- `source`: `camera` | `stage` (teclado no palco).
- `type` e `payload`: ver a tabela.

## Princípios

1. O estado do palco é `reduce(log de eventos)`: o mesmo log dá sempre o mesmo estado (por isso um *refresh* recupera tudo).
2. A câmara e o teclado emitem **os mesmos eventos**. Se a câmara falhar, o teclado faz exatamente o mesmo.
3. Eventos fora de contexto são ignorados, nunca geram erro (ex.: `DIAL_STEP` com o hub vazio).
4. Só entra uma peça de cada vez: `PIECE_ENTER` com um tema aberto é ignorado até haver `PIECE_EXIT`.
5. Voltar a um tema retoma no ecrã onde ficou. Quando os 7 temas foram vistos, o `PIECE_EXIT` seguinte mostra o ecrã de fecho.

## Eventos

| Tipo | Payload | Origem típica | Quando é emitido |
|---|---|---|---|
| `PIECE_ENTER` | `{ "marker": 12 }` | camera, teclado | Peça estável no hub (~8 frames), ou teclas 1–7 |
| `PIECE_EXIT` | `{ "marker": 12 }` | camera, teclado | Hub vazio e estável ≥ 800 ms, ou tecla 0 (ou Esc / Backspace) |
| `DIAL_STEP` | `{ "steps": 1 }` (negativo = para trás) | camera, teclado | Rotação de ≥ 1 detente (45°), ou setas ←/→ (PgDn/PgUp/Espaço também) |
| `RESET` | `{}` | teclado | Volta ao ecrã de espera e apaga o progresso (tecla R) |

## Valores fixos

- `marker` 10–16 = os 7 temas (o ficheiro de cada tema diz qual). 40–43 = âncoras (não geram eventos).
- Teclas: **1–7** põem a peça (marcador 10–16), **0** tira, **← →** andam nos ecrãs, **R** reinicia, **F** ecrã inteiro, **D** mostra o estado de debug.
- Sentido do dial: **horário = +1** (ecrã seguinte), anti-horário = −1.
