from decifra.analisadores.javascript import analisar


def textos(fonte):
    resultado = analisar(fonte)
    linhas = {}
    for linha in resultado.linhas:  # uma linha pode ter mais de uma explicação
        linhas[linha.numero] = (linhas.get(linha.numero, "") + " " + linha.texto).strip()
    return linhas, resultado


def test_codigo_de_iniciante():
    linhas, r = textos("let notas = [7.5, 8, 6];\nlet total = 0;\nfor (const nota of notas) {\n  total = total + nota;\n}\n"
                       "const media = total / notas.length;\nconsole.log(`Média: ${media}`);")
    assert "array (uma lista) com 3 itens" in linhas[1]
    assert "laço `for`" in linhas[3]
    assert linhas[4].startswith("soma `nota`")
    assert "constante `media`" in linhas[6]
    assert "template string" in linhas[7]
    assert r.desconhecidas == 0


def test_mesmas_frases_do_python():
    """O texto compartilhado faz Python e JavaScript explicarem o laço do mesmo jeito."""
    from decifra.analisadores.python import analisar as analisar_python
    js = analisar("for (const n of numeros) {\n  console.log(n);\n}").linhas[0].texto
    py = analisar_python("for n in numeros:\n    print(n)").linhas[0].texto
    assert js == py


def test_for_com_contador_e_else_if():
    linhas, _ = textos('for (let i = 0; i < 3; i++) {\n  console.log(i);\n}\nif (x > 1) {\n  a();\n} else if (x === 1) {\n'
                       '  b();\n} else {\n  c();\n}')
    assert "começa com `i` valendo `0`" in linhas[1] and "aumenta `i` em 1" in linhas[1]
    assert "exatamente igual" in linhas[6]
    assert linhas[8].startswith("se nenhuma das condições anteriores")


def test_funcoes_map_filter_e_eventos():
    linhas, r = textos('const dobro = (x) => x * 2;\nconst pares = nums.filter(n => n % 2 === 0);\n'
                       'const quadrados = nums.map(n => n * n);\nbotao.addEventListener("click", () => {\n  alert("oi");\n});')
    assert "arrow function" in linhas[1]
    assert "`filter`" in linhas[2]
    assert "`map`" in linhas[3]
    assert 'evento "click"' in linhas[4]
    assert "janelinha" in linhas[5]
    assert r.desconhecidas == 0


def test_prompt_e_conversao():
    linhas, _ = textos('const idade = parseInt(prompt("Idade:"));')
    assert "o que a pessoa digitar na janelinha" in linhas[1] and "número inteiro" in linhas[1]


def test_alertas_de_seguranca():
    _, r = textos('const apiKey = "abc";\nel.innerHTML = nome;\nfetch("https://x.com", { method: "POST" });\n'
                  'const fs = require("fs");\nfs.unlinkSync("a.txt");\neval(codigo);\n'
                  'const sql = `SELECT * FROM t WHERE nome = \'${nome}\'`;')
    alertas = " ".join(texto for _, texto in r.alertas)
    for esperado in ("senha ou chave", "XSS", "envia dados pela internet", "apaga o arquivo",
                     "executa um texto como se fosse código", "SQL Injection"):
        assert esperado in alertas


def test_admite_o_que_nao_sabe():
    linhas, r = textos("class Pessoa {}\nlista.sort((a, b) => a - b);")
    assert "não sei explicar" in linhas[1]
    assert "callback" in linhas[2]
    assert r.desconhecidas == 2


def test_erro_de_sintaxe():
    _, r = textos("for (let i = 0; i < 3; i++ {")
    assert r.erro and "linha 1" in r.erro
