"""Privacidade by design: esconde senhas e chaves antes de qualquer análise.

O código mascarado é o único que entra na memória. O valor original nunca é guardado.
"""
import re

# texto solto (fora de código) com dado sensível: a mensagem é descartada
PADROES_TEXTO = [
    ("uma senha", re.compile(r"\bsenha\s*(?:é|eh|:|=|era|seria)\s*\S+", re.IGNORECASE)),
    ("um número de cartão", re.compile(r"\b(?:\d[ -]?){15,16}\b")),
    ("um CPF", re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")),
]

# dentro do código: o valor é trocado por *** e o resto continua sendo explicado
PADROES_CODIGO = [
    ("senha ou chave em variável",
     re.compile(r"""(\b\w*(?:senha|password|passwd|pwd|api_?key|apikey|token|secret|segredo)\w*["']?\s*[:=]\s*)(["'])(?!\*\*\*)(.+?)\2""",
                re.IGNORECASE)),
    ("chave de API", re.compile(r"\b(sk-[A-Za-z0-9_\-]{10,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_\-]{20,}|xox[abprs]-[A-Za-z0-9\-]{10,})")),
    ("senha em endereço de conexão", re.compile(r"(\b\w+://[^:\s/'\"]+:)([^@\s'\"]+)(@)")),
    ("número de cartão", re.compile(r"\b(?:\d[ -]?){15,16}\b")),
    ("CPF", re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")),
]


def dado_sensivel_no_texto(texto):
    for tipo, padrao in PADROES_TEXTO:
        if padrao.search(texto or ""):
            return tipo
    return None


def mascarar_codigo(codigo):
    """Troca valores sensíveis por *** e diz o que foi escondido."""
    achados = []
    for tipo, padrao in PADROES_CODIGO:
        if not padrao.search(codigo):
            continue
        achados.append(tipo)
        if tipo == "senha ou chave em variável":
            codigo = padrao.sub(lambda m: f"{m.group(1)}{m.group(2)}***{m.group(2)}", codigo)
        elif tipo == "senha em endereço de conexão":
            codigo = padrao.sub(lambda m: f"{m.group(1)}***{m.group(3)}", codigo)
        else:
            codigo = padrao.sub("***", codigo)
    return codigo, achados
