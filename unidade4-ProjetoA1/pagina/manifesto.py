"""Gera pagina/arquivos.json: a lista de arquivos Python que o site carrega no navegador.

Uso: python pagina/manifesto.py   (rodar de novo sempre que criar um arquivo novo em decifra/)
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def listar():
    arquivos = sorted(str(p.relative_to(RAIZ)) for p in (RAIZ / "decifra").rglob("*.py"))
    arquivos += sorted(str(p.relative_to(RAIZ)) for p in (RAIZ / "dados").glob("*.json"))
    arquivos += sorted(str(p.relative_to(RAIZ)) for p in (RAIZ / "pagina" / "bibliotecas" / "esprima").glob("*.py"))
    return [a.replace("\\", "/") for a in arquivos]


if __name__ == "__main__":
    (RAIZ / "pagina" / "arquivos.json").write_text(json.dumps(listar(), indent=2) + "\n", encoding="utf-8")
    print(f"{len(listar())} arquivos listados em pagina/arquivos.json")
