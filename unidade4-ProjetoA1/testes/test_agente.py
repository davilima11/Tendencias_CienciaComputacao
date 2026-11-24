import pytest

from decifra.agente import Agente
from decifra.linguagem import detectar
from decifra.privacidade import mascarar_codigo

CODIGO_PY = 'notas = [7.5, 8, 6]\ntotal = 0\nfor nota in notas:\n    total = total + nota\n\n# média final\nprint(total)'


@pytest.fixture
def bot():
    return Agente()


# ---------- camada perceptiva: linguagem ----------
@pytest.mark.parametrize("codigo, esperada", [
    ("def f():\n    return 1", "Python"),
    ("let x = 5;", "JavaScript"),
    ('print("oi")', "Python"),
    ("total = total + nota;", "JavaScript"),
    ('public class A { public static void main(String[] a) { System.out.println(1); } }', "Java"),
    ('#include <stdio.h>\nint main() { printf("oi"); }', "C ou C++"),
    ("<div><p>oi</p></div>", "HTML"),
    ("SELECT * FROM alunos WHERE id = 1", "SQL"),
])
def test_detecta_a_linguagem(codigo, esperada):
    assert detectar(codigo)[0] == esperada


def test_codigo_que_vale_nas_duas_linguagens_e_ambiguo():
    linguagem, _, ambigua = detectar("x = 5")
    assert linguagem == "Python" and ambigua


# ---------- privacidade ----------
def test_mascara_senhas_e_chaves():
    codigo, achados = mascarar_codigo('api_key = "sk-abcdefghijklmnop"\nurl = "mysql://root:minhaSenha@localhost/db"\n'
                                      'const cfg = { apiKey: "AIzaSyA1234567890abcdefghij" };')
    assert "sk-abc" not in codigo and "minhaSenha" not in codigo and "AIzaSy" not in codigo
    assert "senha ou chave em variável" in achados and "senha em endereço de conexão" in achados


def test_chave_nao_chega_na_memoria_nem_na_resposta(bot):
    resposta = bot.responder('chave = "sk-proj-a8F3kL0pQ2xZ9vB7nM4c"\nprint(chave)')
    guardado = str(bot.memoria.codigo) + str(list(bot.memoria.curta)) + str(resposta)
    assert "a8F3kL0pQ2" not in guardado
    assert any("escondi" in aviso for aviso in resposta["avisos"])


def test_senha_digitada_fora_de_codigo_e_descartada(bot):
    resposta = bot.responder("minha senha é abc123")
    assert resposta["acao"] == "bloquear_dado"
    assert "abc123" not in str(list(bot.memoria.curta))


# ---------- conversa (camadas decisória e executiva) ----------
def test_explica_codigo_e_depois_uma_linha(bot):
    assert bot.responder(CODIGO_PY)["acao"] == "explicar_codigo"
    resposta = bot.responder("explica a linha 4")
    assert resposta["acao"] == "explicar_linha"
    assert "total = total + nota" in resposta["texto"] and "Soma `nota`" in resposta["texto"]


def test_linha_em_branco_comentario_e_inexistente(bot):
    bot.responder(CODIGO_PY)
    assert "em branco" in bot.responder("explica a linha 5")["texto"]
    assert "comentário" in bot.responder("linha 6")["texto"]
    assert "não existe a linha 50" in bot.responder("explica a linha 50")["texto"]


def test_pedir_linha_ou_resumo_sem_codigo(bot):
    assert bot.responder("explica a linha 2")["acao"] == "sem_codigo"
    assert bot.responder("resume")["acao"] == "sem_codigo"


def test_resumo(bot):
    bot.responder(CODIGO_PY)
    resposta = bot.responder("resume")
    assert resposta["acao"] == "resumir" and "Por cima" in resposta["texto"]


def test_conceito_usa_exemplo_da_linguagem_escolhida(bot):
    bot.escolher_linguagem("JavaScript")
    resposta = bot.responder("o que é um for?")
    assert resposta["acao"] == "explicar_conceito" and "```javascript" in resposta["texto"]


def test_termo_tecnico_vale_mais_que_frase_parecida(bot):
    # "entendi" lembra agradecimento, mas a pergunta é sobre o for
    assert bot.responder("nao entendi o for")["rotulo"] == "conceito:for"


@pytest.mark.parametrize("pedido", ["corrige meu código pra mim", "faz esse codigo pra mim", "resolve o exercício"])
def test_recusa_escrever_codigo(bot, pedido):
    resposta = bot.responder(pedido)
    assert resposta["acao"] == "recusar_codigo" and "não escrevo nem corrijo" in resposta["texto"]


def test_pergunta_normal_nao_e_recusada(bot):
    assert bot.responder("como criar uma função")["acao"] == "explicar_conceito"


@pytest.mark.parametrize("frase", ["qual a capital da frança", "quem ganhou o jogo ontem", "asdkjh qwe"])
def test_fora_do_escopo_admite_que_nao_entendeu(bot, frase):
    assert bot.responder(frase)["acao"] == "nao_entendi"


# ---------- seletor de linguagem (Python ou JavaScript, sem modo automático) ----------
def test_comeca_em_python(bot):
    assert bot.memoria.linguagem_escolhida == "Python"
    assert bot.responder("x = 5")["linguagem"] == "Python"


def test_codigo_da_outra_linguagem_pede_para_trocar(bot):
    resposta = bot.responder("let x = 5;\nconsole.log(x);")
    assert resposta["acao"] == "linguagem_diferente" and "Troque para JavaScript" in resposta["texto"]
    assert bot.memoria.codigo_pendente is not None


def test_trocar_no_seletor_explica_o_codigo_pendente(bot):
    bot.responder("let x = 5;\nconsole.log(x);")
    resposta = bot.escolher_linguagem("JavaScript")
    assert resposta["acao"] == "trocar_linguagem" and resposta["linguagem"] == "JavaScript"
    assert resposta["linhas"] and bot.memoria.codigo_pendente is None


def test_trocar_no_seletor_sem_codigo_pendente_nao_responde(bot):
    assert bot.escolher_linguagem("JavaScript") is None
    assert bot.memoria.linguagem_escolhida == "JavaScript"
    with pytest.raises(ValueError):
        bot.escolher_linguagem("Java")


def test_exemplo_troca_a_linguagem_sem_explicar_o_pendente(bot):
    bot.responder("let x = 5;\nconsole.log(x);")
    assert bot.escolher_linguagem("Python", explicar_pendente=False) is None
    assert bot.memoria.codigo_pendente is None


def test_escrever_a_linguagem_tambem_troca(bot):
    bot.responder("é javascript")
    assert bot.memoria.linguagem_escolhida == "JavaScript"
    assert bot.responder("y = 10")["linguagem"] == "JavaScript"
    assert bot.responder('def f():\n    print("oi")')["acao"] == "linguagem_diferente"


def test_codigo_que_vale_nas_duas_e_lido_na_escolhida_sem_aviso(bot):
    bot.escolher_linguagem("JavaScript")
    resposta = bot.responder("x = 5")
    assert resposta["linguagem"] == "JavaScript" and not any("cara de" in a for a in resposta["avisos"])


@pytest.mark.parametrize("codigo, linguagem", [
    ('public class A { public static void main(String[] a) { System.out.println(1); } }', "Java"),
    ("SELECT * FROM alunos WHERE id = 1", "SQL"),
    ("<div><p>oi</p></div>", "HTML"),
])
def test_linguagem_que_nao_sei(bot, codigo, linguagem):
    resposta = bot.responder(codigo)
    assert resposta["acao"] == "linguagem_nao_suportada" and linguagem in resposta["texto"]


def test_memoria_curta_nao_guarda_codigo(bot):
    bot.responder(CODIGO_PY)
    assert all("total = total" not in texto for _, texto in bot.memoria.curta)


def test_toda_resposta_explica_a_decisao(bot):
    for mensagem in ["oi", CODIGO_PY, "linha 3", "o que é lista", "corrige meu codigo", "bolo de cenoura", "x = 5"]:
        assert bot.responder(mensagem)["explicacao"]


def test_tfidf_feito_a_mao_igual_ao_scikit_learn():
    sklearn = pytest.importorskip("sklearn.feature_extraction.text")
    from sklearn.metrics.pairwise import cosine_similarity

    from decifra.tfidf import TfIdf
    frases = ["o que e variavel", "pra que serve uma lista", "como funciona o for", "oi", "x"]
    vetorizador = sklearn.TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
    matriz = vetorizador.fit_transform(frases)
    nosso = TfIdf(frases)
    for consulta in ["oq e um for", "variavel", "listas", "a"]:
        esperado = cosine_similarity(vetorizador.transform([consulta]), matriz)[0]
        indice, valor = nosso.mais_parecida(consulta)
        assert indice == esperado.argmax() and abs(valor - esperado.max()) < 1e-9
