# O que fazer, por ordem

**Datas:** sessão conjunta **qua 11 nov** · apresentação **qua 18 nov**.
**Já está feito neste kit:** servidor, palco com teclado (funciona hoje!), lógica de câmara (deteção, homografia, entrar/sair, dial) e testes.
**O que falta é o trabalho de mundo real:** calibrar a câmara, afinar limiares e escrever o conteúdo.

## Sáb 7 (hoje: sem programar)
- [ ] `.\setup.ps1` (instala tudo, cria o repo no GitHub, faz o primeiro commit)
- [ ] Convidar o colega: GitHub → repo → Settings → Collaborators
- [ ] Imprimir `tools\marcadores.pdf` a **100%**, em papel mate. Mede 1 quadrado: tem de dar 30 mm
- [ ] Colar os marcadores em discos de cartolina (~30 mm) e os discos no topo de 7 peças bem diferentes entre si (a página 2 são as âncoras: colar nos 4 cantos, fora do tabuleiro)
- [ ] Medir o teu tabuleiro e preencher `SQUARE_MM` em `vision/config.py`
- [ ] Instalar uma app de webcam no telemóvel (DroidCam, Camo ou iVCam)
- [ ] Perguntas ao professor: porta do projetor (VGA/HDMI), montar 15 min antes, tomada
- [ ] Colega: fechar os 7 temas e preencher `content/`

## Dom 8: porta G1 (a câmara aguenta a luz?)
- [ ] `uv run python -m vision.detect_test --list` e depois `--cam N`: faz a matriz de testes (luz da janela, candeeiro, sombra da mão, 50/70/90 cm) e anota a tabela final
- [ ] Medir as posições das âncoras com uma régua e preencher `ANCHOR_MM` em `vision/config.py`
- [ ] `.\start-vision.ps1 --show --print`: o polígono **verde** tem de cobrir as 4 casas centrais
- [ ] **G1:** peça parada no hub 60 s com ≥ 98% de frames certos e 0 IDs falsos; e 10 min com a mão a mexer sem falsos "entrou"
- [ ] Decidir qual portátil apresenta

## Seg 9: câmara + palco ligados
- [ ] Terminal 1: `.\start.ps1` · Terminal 2: `.\start-vision.ps1 --show --print` · Browser: http://localhost:8000/stage/ (F = ecrã inteiro, D = debug)
- [ ] Afinar em `vision/config.py`: `ENTER_FRAMES`, `EXIT_MS`, `DETENT_DEG`. Gravar clipes com a tecla S
- [ ] Anel de papel com marcas de 45° no centro do tabuleiro (para sentires os detentes)
- [ ] Conteúdo do colega já a aparecer no palco (`uv run python tools/build_content.py`)

## Ter 10: G2 e preparação da sessão
- [ ] Ensaio solo com 2 temas completos, câmara e teclado
- [ ] Kit na mochila: 7 peças com tampa, âncoras, anel, suporte, cabo, extensão, portátil, carregador
- [ ] Colega: imprimir a 2.ª cópia dos marcadores, fazer as suas tampas, praticar o gesto (pôr, esperar 1 s, rodar, retirar)

## Qua 11: sessão conjunta (120 min)
- 0–15 montar o kit nas condições reais
- 15–35 teste de mãos (o colega põe, roda e retira)
- 35–80 ensaio completo cronometrado
- 80–100 simular falhas (tapar a câmara e passar ao teclado, reiniciar o processo da câmara)
- 100–120 lista de correções com dono e data

## 12–18 nov
- Qui 12: corrigir a lista da sessão, polir a legibilidade, fechar o conteúdo
- Sex 13: fallbacks (reinício automático, versão só-browser numa pen) e vídeo de ensaio perfeito
- Sáb 14 / dom 15: ensaios por videochamada, cronometrados
- Seg 16: **congelar funcionalidades**, só correção de erros, backups (pen, PDF)
- Ter 17: ensaio geral e checklist
- **Qua 18: apresentação**

## Se o tempo apertar, corta por esta ordem
Animações → ecrã de fecho decorado → câmara (fica o teclado) → dial (as setas fazem o mesmo scroll). Nunca cortes o conteúdo nem os fallbacks.
