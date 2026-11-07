# Tabuleiro Vivo

Apresentação interativa sobre Magnus Carlsen. Uma peça com marcador ArUco no centro do tabuleiro abre um tema; rodá-la anda pelos ecrãs desse tema. Corre 100% no portátil, sem internet.

```
vision/    câmara -> deteção ArUco -> eventos (Python + OpenCV)
server/    FastAPI: numera os eventos, grava o log, serve o palco
stage/     o palco: HTML/CSS/JS simples (funciona também só com o teclado)
content/   os 7 temas em YAML (o colega edita aqui)
tools/     gerador de marcadores, conversor de conteúdo
tests/     testes (sem câmara: usam imagens sintéticas)
docs/      TODO.md (o que fazer por ordem) e events.md (contrato de eventos)
```

## Começar

```powershell
.\setup.ps1          # uma vez: instala, testa, cria o repo no GitHub
.\start.ps1          # servidor + palco em http://localhost:8000/stage/
.\start-vision.ps1 --show --print    # câmara com janela de debug
```

Teclas no palco: **1–7** põem a peça, **0** tira, **← →** andam nos ecrãs, **R** reinicia, **F** ecrã inteiro, **D** debug.
O palco também abre com duplo clique em `stage\index.html` (só com o teclado, sem servidor).

## Testes

```powershell
uv run python -m vision.dial
uv run python -m tests.test_hub
uv run python -m tests.test_bus
```

## Notas

- Se o PC for partilhado, no fim da sessão: `gh auth logout`.
- `recordings/` não vai para o Git (vídeos e logs de eventos).
- O servidor arranca com um log novo; para retomar depois de um crash: `$env:RESUME=1; .\start.ps1`.
