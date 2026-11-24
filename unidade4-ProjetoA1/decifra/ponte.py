"""Ponte entre o DecifraBot e a versão web (index.html).

No navegador, o mesmo código Python roda dentro do Pyodide. Esta ponte só
transforma as respostas em JSON para a página conseguir mostrar.
"""
import json
from pathlib import Path

from decifra.agente import Agente

_agente = Agente()


def _para_json(resposta):
    saida = {chave: resposta.get(chave) for chave in
             ("tipo", "texto", "avisos", "acao", "explicacao", "linguagem", "linguagem_escolhida", "codigo_exibido")}
    if resposta["tipo"] == "explicacao":
        resultado = resposta["resultado"]
        saida["linhas"] = [{"numero": l.numero, "texto": l.texto, "nivel": l.nivel} for l in resposta["linhas"]]
        saida["alertas"] = [{"numero": n, "texto": t} for n, t in resultado.alertas]
        saida["conceitos"] = [_agente.conceitos[c]["titulo"] for c in resultado.conceitos if c in _agente.conceitos]
    return saida


def responder(texto):
    return json.dumps(_para_json(_agente.responder(texto)), ensure_ascii=False)


def escolher_linguagem(linguagem, explicar_pendente=True):
    """Seletor de linguagem: devolve a explicação do código que estava esperando, ou "null"."""
    resposta = _agente.escolher_linguagem(linguagem, explicar_pendente)
    return json.dumps(_para_json(resposta) if resposta else None, ensure_ascii=False)


def linguagem_escolhida():
    return _agente.memoria.linguagem_escolhida


def limpar():
    _agente.memoria.limpar()


def mensagem_inicial():
    return _agente.msgs["inicial"]


def exemplos():
    caminho = Path(__file__).resolve().parent.parent / "dados" / "exemplos.json"
    return caminho.read_text(encoding="utf-8")
