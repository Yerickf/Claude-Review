"""Converte content/tema*.yaml em stage/content.js e avisa de erros de conteúdo.

Uso: uv run python tools/build_content.py [--strict]
(--strict termina com erro se houver avisos)
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TIPOS = {"facto", "pergunta", "resposta"}
MAX_PALAVRAS = 12
MAX_ECRAS = 6
MARKERS = set(range(10, 17))


def validar(t, nome, avisos):
    def av(msg):
        avisos.append("%s: %s" % (nome, msg))

    for k in ("tema", "marker", "dono", "ecras"):
        if k not in t:
            av("falta o campo '%s'" % k)
    if t.get("marker") not in MARKERS:
        av("marker %r tem de estar entre 10 e 16" % t.get("marker"))
    if str(t.get("tema", "")).upper().startswith("TEMA "):
        av("o título ainda é o de exemplo")
    ecras = t.get("ecras") or []
    if not ecras:
        av("sem ecrãs")
    if len(ecras) > MAX_ECRAS:
        av("%d ecrãs (máx. %d para caber em ~2 min)" % (len(ecras), MAX_ECRAS))
    for i, e in enumerate(ecras, 1):
        if e.get("tipo") not in TIPOS:
            av("ecrã %d: tipo %r inválido (facto | pergunta | resposta)" % (i, e.get("tipo")))
        palavras = len(str(e.get("texto", "")).split())
        if palavras > MAX_PALAVRAS:
            av("ecrã %d: %d palavras (máx. %d)" % (i, palavras, MAX_PALAVRAS))
        if e.get("tipo") == "facto" and not str(e.get("fonte", "")).strip():
            av("ecrã %d: facto sem fonte" % i)
        if e.get("tipo") == "pergunta":
            nxt = ecras[i] if i < len(ecras) else {}
            if nxt.get("tipo") != "resposta":
                av("ecrã %d: a pergunta devia ser seguida de uma resposta" % i)


def main():
    strict = "--strict" in sys.argv
    avisos = []
    temas = []
    vistos = {}
    for f in sorted((ROOT / "content").glob("tema*.yaml")):
        t = yaml.safe_load(f.read_text(encoding="utf-8"))
        if not isinstance(t, dict):
            avisos.append("%s: ficheiro vazio ou inválido" % f.name)
            continue
        validar(t, f.name, avisos)
        m = t.get("marker")
        if m in vistos:
            avisos.append("%s: marker %s repetido (já usado em %s)" % (f.name, m, vistos[m]))
        vistos[m] = f.name
        temas.append(t)

    out = ROOT / "stage" / "content.js"
    out.write_text(
        "// GERADO por tools/build_content.py. Não editar: edita os ficheiros em content/.\n"
        "window.CONTENT = " + json.dumps(temas, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    total = sum(len(t.get("ecras") or []) for t in temas)
    print("%d temas, %d ecrãs -> %s" % (len(temas), total, out.relative_to(ROOT)))
    for a in avisos:
        print("AVISO", a)
    if strict and avisos:
        sys.exit(1)


if __name__ == "__main__":
    main()
