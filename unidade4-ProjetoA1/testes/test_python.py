from decifra.analisadores.python import analisar


def textos(fonte):
    resultado = analisar(fonte)
    linhas = {}
    for linha in resultado.linhas:  # uma linha pode ter mais de uma explicação
        linhas[linha.numero] = (linhas.get(linha.numero, "") + " " + linha.texto).strip()
    return linhas, resultado


def test_codigo_de_iniciante():
    linhas, r = textos('notas = [7.5, 8, 6]\ntotal = 0\nfor nota in notas:\n    total = total + nota\n'
                       'media = total / len(notas)\nprint("Média:", media)')
    assert "cria a variável `notas`" in linhas[1] and "lista com 3 itens" in linhas[1]
    assert "laço `for`" in linhas[3] and "`nota`" in linhas[3]
    assert linhas[4].startswith("soma `nota` ao valor que já estava em `total`")
    assert "mostra na tela" in linhas[6]
    assert r.desconhecidas == 0
    assert {"variavel", "lista", "for", "tamanho", "mostrar"} <= set(r.conceitos)


def test_funcao_if_elif_else_e_input():
    linhas, r = textos('def situacao(media):\n    if media >= 7:\n        return "Aprovado"\n    elif media >= 5:\n'
                       '        return "Recuperação"\n    else:\n        return "Reprovado"\n\n'
                       'nota = float(input("Média: "))\nprint(situacao(nota))')
    assert "cria uma função chamada `situacao` que recebe `media`" in linhas[1]
    assert "maior ou igual a `7`" in linhas[2]
    assert linhas[4].startswith("se não, verifica se")
    assert linhas[6].startswith("se nenhuma das condições anteriores")
    assert "o que a pessoa digitar" in linhas[9] and "casas decimais" in linhas[9]
    assert "criada na linha 1" in linhas[10]


def test_range_while_try_e_with():
    linhas, _ = textos('for i in range(5):\n    pass\nwhile True:\n    break\ntry:\n    x = int("a")\n'
                       'except ValueError:\n    print("erro")\nwith open("a.txt") as f:\n    print(f.read())')
    assert "de 0 até 4" in linhas[1]
    assert "`while True`" in linhas[3]
    assert linhas[5].startswith("tenta executar")
    assert "`ValueError`" in linhas[7]
    assert "abre o arquivo `\"a.txt\"` para ler" in linhas[9]


def test_cita_o_codigo_como_foi_escrito():
    linhas, _ = textos('import os\nos.remove(pasta + "/" + nome)')
    assert '`pasta + "/" + nome`' in linhas[2]


def test_list_comprehension_simples():
    linhas, r = textos("pares = [n for n in range(10) if n % 2 == 0]")
    assert "list comprehension" in linhas[1] and "só quando" in linhas[1]
    assert r.desconhecidas == 0


def test_alertas_de_seguranca():
    _, r = textos('import os, shutil\napi_key = "abc"\nos.remove("a.txt")\nshutil.rmtree("pasta")\neval(x)\n'
                  'open("dados.txt", "w")\nsql = f"SELECT * FROM t WHERE nome = \'{nome}\'"')
    alertas = " ".join(texto for _, texto in r.alertas)
    for esperado in ("senha ou chave", "apaga o arquivo", "apaga a pasta", "executa um texto como se fosse código",
                     "o conteúdo antigo é apagado", "SQL Injection"):
        assert esperado in alertas


def test_sql_com_parametro_nao_gera_alerta():
    _, r = textos('cur.execute("SELECT * FROM t WHERE nome = ?", (nome,))')
    assert not r.alertas


def test_admite_o_que_nao_sabe():
    linhas, r = textos("dobro = lambda x: x * 2\nclass Pessoa:\n    pass")
    assert "não sei explicar" in linhas[1]
    assert "não sei explicar" in linhas[2]
    assert r.desconhecidas == 2


def test_erro_de_sintaxe():
    _, r = textos("def f(:\n    pass")
    assert r.erro and "linha 1" in r.erro
