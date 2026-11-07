# Como escrever o conteúdo (para o colega)

Cada tema é um ficheiro `temaN.yaml` nesta pasta. Cada tema é uma **lista de ecrãs**: o ecrã aparece, e o dial passa ao seguinte.

## O que mexer

- `tema`: o título do tema.
- `dono`: quem fala (`tu`, `colega` ou `os dois`).
- `ecras`: a lista. Cada ecrã tem:
  - `tipo`: `facto`, `pergunta` ou `resposta`. Uma **pergunta é sempre seguida de uma resposta** (a resposta aparece quando se roda o dial).
  - `titulo`: o subtema.
  - `texto`: **no máximo 12 palavras** (tem de se ler lá do fundo da sala).
  - `imagem`: opcional. Põe a imagem em `stage/img/` e escreve `img/nome.jpg`.
  - `fonte`: o link da fonte. **Obrigatório nos factos.**

## Regras que cabem na apresentação

- 7 temas em ~15 minutos = ~2 minutos por tema, por isso **no máximo 6 ecrãs por tema**.
- Uma ideia por ecrã. Se precisas de mais, divide em dois ecrãs.
- Imagens: usa o Wikimedia Commons e anota o autor na fonte.

## Cuidados com o YAML

- Escreve sempre os textos **entre aspas duplas** `"assim"`. Se o texto tiver aspas, usa aspas simples por fora: `'ele disse "olá"'`.
- Indenta com **espaços** (nunca com Tab) e mantém o alinhamento igual aos exemplos.
- Não apagues os `-` do início de cada ecrã.

## Como guardar

No VS Code: Source Control → escreve uma mensagem → Commit → Sync. **Antes de começares a trabalhar, faz sempre Pull.**
Só mexes em `content/` e `docs/`. O resto do código é do teu colega.

## Ver como fica (opcional)

1. `winget install astral-sh.uv`, fecha e reabre o terminal.
2. Na pasta do projeto: `uv sync` e depois `uv run python tools/build_content.py` (mostra avisos dos erros mais comuns).
3. Abre `stage\index.html` com duplo clique. Teclas **1–7** abrem os temas, **← →** passam os ecrãs, **0** fecha o tema.
