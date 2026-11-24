"""Testa as perguntas com frases que NÃO estão na base, para escolher o limiar de confiança.

Uso: python -m testes.calibrar_limiar
"""
from decifra.agente import Agente

# perguntas do jeito que um aluno escreveria (nenhuma está igual na base)
DENTRO_DO_ESCOPO = [
    ("pra que serve uma variavel", "conceito:variavel"), ("oq é um array", "conceito:lista"),
    ("como funciona o laço de repetição", "conceito:for"), ("nao entendi o for", "conceito:for"),
    ("qual a diferença do for pro while", "conceito:while"), ("o que faz o if", "conceito:if"),
    ("como funciona uma função", "conceito:funcao"), ("o que significa def", "conceito:funcao"),
    ("o que o return devolve", "conceito:return"), ("pra que serve o console.log", "conceito:mostrar"),
    ("como pego o que o usuario digitou", "conceito:entrada"), ("pq usar int no input", "conceito:conversao"),
    ("o que é len em python", "conceito:tamanho"), ("o que é const em javascript", "conceito:constante"),
    ("o que quer dizer import", "conceito:modulo"), ("o que é esse f antes das aspas", "conceito:texto_formatado"),
    ("qual a diferença de == e ===", "conceito:comparacao"), ("como funciona try catch", "conceito:try"),
    ("o que é um dicionario", "conceito:dicionario"), ("pra que serve o range", "conceito:range"),
    ("faz esse codigo pra mim", "pedido_codigo"), ("arruma meu codigo", "pedido_codigo"),
    ("me explica resumido", "resumo"), ("olá tudo bem", "saudacao"), ("valeu mano", "agradecimento"),
    ("como eu uso isso", "ajuda"),
]
# segundo conjunto, escrito DEPOIS de corrigir os erros do primeiro, para conferir com frases que
# não influenciaram nenhuma correção
VALIDACAO = [
    ("ainda nao saquei o while", "conceito:while"), ("pra que usar const", "conceito:constante"),
    ("como funciona o return", "conceito:return"), ("o que é parametro de funcao", "conceito:funcao"),
    ("como funciona uma lista em js", "conceito:lista"), ("o que é o else", "conceito:if"),
    ("o que é prompt", "conceito:entrada"), ("como funciona o import", "conceito:modulo"),
    ("explica o que e objeto", "conceito:dicionario"), ("cria um programa de calculadora", "pedido_codigo"),
    ("corrige esse erro pra mim", "pedido_codigo"), ("resume pra mim", "resumo"), ("bom dia", "saudacao"),
    ("o que você consegue fazer", "ajuda"), ("como transformar texto em numero", "conceito:conversao"),
    ("como sei quantos itens tem no vetor", "conceito:lista"),
]
FORA_DO_ESCOPO = [
    "qual a capital da frança", "quem ganhou o jogo ontem", "me indica um filme", "que horas são",
    "vai chover amanhã", "quanto custa um notebook", "me conta uma piada", "qual o melhor time",
    "como faz bolo de cenoura", "asdkjh qwe", "quero marcar férias", "qual seu nome",
]


def rotulo_final(agente, frase):
    """O rótulo depois das regras da camada decisória (pedido de código tem regra própria)."""
    percepcao = agente.perceber(frase)
    rotulo, confianca, _ = agente.entender(percepcao)
    if percepcao["pede_codigo"]:
        return "pedido_codigo", 1.0
    return rotulo, confianca


def avaliar(agente, limiar, frases=DENTRO_DO_ESCOPO):
    acertos = rejeitadas = 0
    for frase, esperado in frases:
        rotulo, confianca = rotulo_final(agente, frase)
        if confianca < limiar:
            rejeitadas += 1
        elif rotulo == esperado:
            acertos += 1
    fora = sum(1 for f in FORA_DO_ESCOPO if agente.entender(agente.perceber(f))[1] < limiar)
    return acertos, rejeitadas, fora


if __name__ == "__main__":
    bot = Agente()
    print("limiar | calibração: certas (rejeitadas) | validação: certas (rejeitadas) | fora do escopo rejeitadas")
    for limiar in (0.25, 0.30, 0.35, 0.40, 0.45, 0.50):
        a, r, f = avaliar(bot, limiar)
        av, rv, _ = avaliar(bot, limiar, VALIDACAO)
        print(f"{limiar:.2f}   | {a}/{len(DENTRO_DO_ESCOPO)} ({r})                     | "
              f"{av}/{len(VALIDACAO)} ({rv})                    | {f}/{len(FORA_DO_ESCOPO)}")
    print("\nDetalhe:")
    for frase, esperado in DENTRO_DO_ESCOPO + VALIDACAO:
        rotulo, conf = rotulo_final(bot, frase)
        print(f"  {conf:.2f} {'OK  ' if rotulo == esperado else 'ERRO'} {rotulo:28s} <- {frase}")
    for frase in FORA_DO_ESCOPO:
        rotulo, conf, _ = bot.entender(bot.perceber(frase))
        print(f"  {conf:.2f} fora {rotulo:28s} <- {frase}")
