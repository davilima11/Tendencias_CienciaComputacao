"""Descobre em que linguagem o código foi escrito (parte da camada perceptiva)."""
import ast
import re

import esprima

SINAIS = {
    "Python": [r"^\s*def\s+\w+\s*\(", r"^\s*(elif|import|from)\s", r"\bprint\s*\(", r"\binput\s*\(",
               r":\s*(#.*)?$", r"\b(True|False|None)\b", r"^\s*#", r"\b(and|or|not)\b", r"f\"|f'"],
    "JavaScript": [r"\b(let|const|var)\s+\w", r"\bfunction\b", r"\bconsole\.\w+\s*\(", r"=>", r";\s*$",
                   r"\{\s*$", r"===|!==", r"\bdocument\.", r"^\s*//", r"\b(true|false|null|undefined)\b", r"\$\{"],
}
OUTRAS = {
    "Java": r"public\s+(static\s+)?(class|void)|System\.out\.print|String\[\]\s+args|import\s+java\.",
    "C ou C++": r"#include\s*<|\bprintf\s*\(|\bint\s+main\s*\(|std::|cout\s*<<",
    "HTML": r"<\s*(html|div|body|head|p|h1|h2|ul|li|script|form|input)\b[^>]*>",
    "SQL": r"(?i)^\s*(select\s.+\sfrom|insert\s+into|update\s.+\sset|delete\s+from|create\s+table)\b",
    "PHP": r"<\?php|\$\w+\s*=.*;",
}


def le_python(texto):
    try:
        ast.parse(texto)
        return True
    except SyntaxError:
        return False


def le_javascript(texto):
    try:
        esprima.parseScript(texto)
        return True
    except esprima.Error:
        return False


def pontos(texto, linguagem):
    return sum(1 for padrao in SINAIS[linguagem] if re.search(padrao, texto, re.MULTILINE))


def detectar(texto):
    """Retorna (linguagem, motivo, ambigua).

    Quem decide a linguagem é a pessoa, no seletor. Isto aqui serve para reconhecer outras
    linguagens (Java, C...) e para avisar quando o código parece a linguagem que não foi escolhida.
    """
    py, js = le_python(texto), le_javascript(texto)
    p_py, p_js = pontos(texto, "Python"), pontos(texto, "JavaScript")

    for nome, padrao in OUTRAS.items():
        if re.search(padrao, texto, re.MULTILINE) and not (py and p_py > 0) and not (js and p_js > 0):
            return nome, f"ele tem marcas típicas de {nome}", False
    if py and not js:
        return "Python", "só o leitor de Python conseguiu ler o código", False
    if js and not py:
        return "JavaScript", "só o leitor de JavaScript conseguiu ler o código", False
    if py and js:
        if p_py > p_js:
            return "Python", "o código funciona nas duas linguagens, mas tem mais marcas de Python", False
        if p_js > p_py:
            return "JavaScript", "o código funciona nas duas linguagens, mas tem mais marcas de JavaScript", False
        return "Python", "o código funciona igual em Python e em JavaScript, então escolhi Python", True
    if p_js > p_py:
        return "JavaScript", "ele tem mais marcas de JavaScript (mas tem algum erro de digitação)", False
    if p_py > 0:
        return "Python", "ele tem mais marcas de Python (mas tem algum erro de digitação)", False
    return None, "não reconheci a linguagem", False
