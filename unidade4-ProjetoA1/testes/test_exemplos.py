"""Confere que os códigos da pasta codigos-de-exemplo continuam sendo bem explicados."""
from pathlib import Path

from decifra.agente import Agente

PASTA = Path(__file__).resolve().parent.parent / "codigos-de-exemplo"
ALERTAS_ESPERADOS = {
    "04_codigo_que_veio_da_ia.py": ["senha ou chave", "apaga o arquivo", "apaga a pasta", "envia dados"],
    "05_busca_no_banco.py": ["SQL Injection"],
    "08_botao_da_pagina.js": ["XSS"],
}


def explicar(arquivo):
    bot = Agente()
    bot.escolher_linguagem("JavaScript" if arquivo.suffix == ".js" else "Python")
    return bot.responder(arquivo.read_text(encoding="utf-8"))


def test_codigos_de_exemplo_sao_explicados():
    arquivos = [a for a in sorted(PASTA.glob("*.*")) if a.suffix in (".py", ".js") and a.name != "09_codigo_avancado.py"]
    assert len(arquivos) == 8
    for arquivo in arquivos:
        resposta = explicar(arquivo)
        assert resposta["acao"] == "explicar_codigo", arquivo.name
        assert resposta["resultado"].desconhecidas == 0, arquivo.name
        alertas = " ".join(texto for _, texto in resposta["resultado"].alertas)
        for esperado in ALERTAS_ESPERADOS.get(arquivo.name, []):
            assert esperado in alertas, (arquivo.name, esperado)
        if arquivo.name not in ALERTAS_ESPERADOS:
            assert not resposta["resultado"].alertas, arquivo.name


def test_codigo_avancado_avisa_o_que_nao_sabe():
    resposta = explicar(PASTA / "09_codigo_avancado.py")
    textos = " ".join(linha.texto for linha in resposta["linhas"])
    assert resposta["resultado"].desconhecidas == 2 and "ainda não sei explicar" in textos
