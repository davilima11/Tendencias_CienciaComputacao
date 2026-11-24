"""Textos de explicação compartilhados entre as linguagens.

Os analisadores de Python e de JavaScript leem o código de jeitos diferentes,
mas explicam com as mesmas frases. Para ensinar uma linguagem nova ao
DecifraBot, a maior parte do texto já está aqui.
"""
import re
from dataclasses import dataclass, field

FRASES = {
    "criar_variavel": "cria a variável {nome}, guardando {valor}.",
    "criar_constante": "cria a constante {nome} (um valor que não pode ser trocado depois), guardando {valor}.",
    "mudar_variavel": "muda o valor de {nome}, que passa a guardar {valor}.",
    "somar_em": "soma {valor} ao valor que já estava em {nome}.",
    "subtrair_de": "subtrai {valor} do valor que já estava em {nome}.",
    "operar_em": "atualiza {nome} usando o operador {operador}.",
    "incrementar": "aumenta o valor de {nome} em 1.",
    "decrementar": "diminui o valor de {nome} em 1.",
    "for_cada": "um laço `for` que passa por cada item de {origem}. A cada volta, o item da vez fica guardado em {var}.",
    "for_arquivos": "um laço `for` que passa por cada arquivo da pasta {pasta}. A cada volta, o nome do arquivo da vez fica guardado em {var}.",
    "for_numeros": "um laço `for` que repete o bloco abaixo uma vez para cada número de {inicio} até {fim}. A cada volta, o número da vez fica em {var}.",
    "for_contador": "um laço `for` com contador: começa com {inicio}, repete enquanto {condicao} e, no fim de cada volta, {passo}.",
    "for_chaves": "um laço `for` que passa por cada chave (nome de propriedade) de {origem}. A cada volta, a chave da vez fica em {var}.",
    "while": "um laço `while`: repete o bloco abaixo enquanto {condicao}. Se essa condição nunca ficar falsa, o laço não para.",
    "while_infinito": "um laço `while True`: repete o bloco abaixo para sempre, até encontrar um `break` lá dentro.",
    "escrever_arquivo": "escreve {valor} no arquivo {arquivo}.",
    "do_while": "um laço `do...while`: executa o bloco abaixo uma vez e depois continua repetindo enquanto {condicao}.",
    "if": "verifica se {condicao}. Se for verdade, executa o bloco abaixo.",
    "elif": "se não, verifica se {condicao}.",
    "else": "se nenhuma das condições anteriores for verdade, executa o bloco abaixo.",
    "funcao": "cria uma função chamada {nome}{recebe}. O código dentro dela só roda quando a função for chamada.",
    "retorno": "devolve {valor} para quem chamou a função.",
    "retorno_vazio": "termina a função sem devolver nada.",
    "mostrar": "mostra na tela {partes}.",
    "janela": "mostra uma janelinha de aviso com {partes}.",
    "chamar_funcao_do_codigo": "chama a função {nome} (criada na linha {linha}), e o código dela roda agora.",
    "chamar": "chama {codigo}.",
    "adicionar_lista": "adiciona {valor} no fim da lista {lista}.",
    "break": "sai do laço na hora, sem terminar as voltas que faltavam.",
    "continue": "pula o resto desta volta e vai direto para a próxima.",
    "pass": "não faz nada. Serve só para deixar o bloco preenchido.",
    "try": "tenta executar o bloco abaixo. Se acontecer um erro, em vez de o programa parar, ele pula para o bloco de tratamento.",
    "except": "diz o que fazer se der erro no bloco do `try`{tipo}.",
    "finally": "executa o bloco abaixo no final, tendo dado erro ou não.",
    "importar": "importa {modulo}, que traz {descricao}.",
    "segredo": "guarda em {nome} um texto que parece ser uma senha ou chave (escondi o valor).",
    "principal": "verifica se este arquivo está sendo executado diretamente (e não importado por outro arquivo). É um padrão comum para dizer onde o programa começa.",
    "abrir_arquivo": "abre o arquivo {arquivo} para {modo} e chama ele de {nome} dentro do bloco abaixo. No fim do bloco, o arquivo é fechado sozinho.",
    "nao_sei": "usa {estrutura}, que eu ainda não sei explicar. Prefiro avisar a chutar.",
}

ALERTAS = {
    "apaga_arquivo": "apaga o arquivo {alvo} do seu computador, sem pedir confirmação",
    "apaga_pasta": "apaga a pasta {alvo} e tudo que estiver dentro dela, sem pedir confirmação",
    "executa_comando": "executa um comando direto no sistema do seu computador",
    "executa_texto": "executa um texto como se fosse código. Se esse texto vier de fora (do usuário ou da internet), qualquer coisa pode ser executada",
    "envia_internet": "envia dados pela internet para {alvo}",
    "acessa_internet": "se conecta à internet ({alvo}). Confira se você confia nesse endereço",
    "sobrescreve_arquivo": "abre o arquivo {alvo} para escrita: se ele já existir, o conteúdo antigo é apagado",
    "segredo": "{nome} parece guardar uma senha ou chave. Nunca compartilhe código com esse valor preenchido",
    "chave_no_texto": "o código tem um texto com cara de chave de acesso (escondi o valor). Nunca compartilhe código com chave preenchida",
    "html_pagina": "coloca HTML direto na página. Se esse texto vier do usuário, alguém pode injetar código na página (isso se chama XSS)",
    "sql_montado": "monta um comando SQL juntando textos. Se uma parte vier do usuário, alguém pode alterar o comando (isso se chama SQL Injection). O certo é usar consulta parametrizada",
}

# o que o código faz "por cima", na ordem em que aparece no resumo
ATIVIDADES = {
    "funcao": "cria função",
    "entrada": "pede dados para a pessoa",
    "decisao": "toma decisões com `if`",
    "laco": "repete coisas com laço",
    "arquivo": "mexe com arquivos",
    "internet": "acessa a internet",
    "aleatorio": "sorteia valores",
    "pagina": "mexe na página (HTML)",
    "saida": "mostra resultados na tela",
}

NOMES_SENSIVEIS = re.compile(r"senha|password|passwd|pwd|api_?key|apikey|token|secret|segredo", re.IGNORECASE)
SQL = re.compile(r"\b(select|insert|update|delete)\b.*\b(from|into|set|where)\b", re.IGNORECASE)


def frase(chave, **valores):
    return FRASES[chave].format(**valores)


def alerta(chave, **valores):
    return ALERTAS[chave].format(**valores)


def cod(trecho):
    """Coloca um trecho de código entre crases, encurtando se for muito grande."""
    trecho = " ".join(trecho.split())
    if len(trecho) > 60:
        trecho = trecho[:57] + "..."
    if "`" in trecho:  # código com crase (template string) precisa de crase dupla no Markdown
        return f"`` {trecho} ``"
    return f"`{trecho}`"


@dataclass
class Linha:
    numero: int
    texto: str
    nivel: int = 0


@dataclass
class Resultado:
    linguagem: str
    linhas: list = field(default_factory=list)
    alertas: list = field(default_factory=list)  # (numero, texto)
    conceitos: list = field(default_factory=list)
    atividades: list = field(default_factory=list)
    linhas_de_codigo: int = 0
    desconhecidas: int = 0
    erro: str = None

    def resumo(self):
        feitas = [ATIVIDADES[a] for a in ATIVIDADES if a in self.atividades]
        if not feitas:
            return "Por cima, esse código só guarda valores em variáveis."
        if len(feitas) == 1:
            return f"Por cima, esse código {feitas[0]}."
        return f"Por cima, esse código {', '.join(feitas[:-1])} e {feitas[-1]}."


class AnalisadorBase:
    """Parte comum dos analisadores: guarda as explicações, alertas e conceitos."""

    linguagem = ""

    def __init__(self, fonte):
        self.fonte = fonte
        self.resultado = Resultado(self.linguagem)
        self.variaveis = set()
        self.funcoes = {}

    def add(self, numero, texto, nivel):
        self.resultado.linhas.append(Linha(numero, texto, nivel))

    def nao_sei(self, numero, estrutura, nivel):
        self.resultado.desconhecidas += 1
        self.add(numero, frase("nao_sei", estrutura=estrutura), nivel)

    def alerta(self, numero, texto):
        if (numero, texto) not in self.resultado.alertas:
            self.resultado.alertas.append((numero, texto))

    def conceito(self, nome):
        if nome not in self.resultado.conceitos:
            self.resultado.conceitos.append(nome)

    def atividade(self, nome):
        if nome not in self.resultado.atividades:
            self.resultado.atividades.append(nome)

    def finalizar(self):
        self.resultado.linhas.sort(key=lambda linha: linha.numero)
        self.resultado.alertas.sort()
        self.resultado.linhas_de_codigo = len({l.numero for l in self.resultado.linhas})
        return self.resultado
