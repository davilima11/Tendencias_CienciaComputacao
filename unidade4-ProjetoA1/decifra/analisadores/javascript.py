"""Analisador de JavaScript: lê o código com a biblioteca esprima.

Usa as mesmas frases do analisador de Python (decifra/textos.py).
"""
import esprima
from esprima.nodes import Node

from decifra.textos import NOMES_SENSIVEIS, SQL, AnalisadorBase, alerta, cod, frase

COMPARACOES = {"===": "é exatamente igual a (mesmo valor e mesmo tipo)", "!==": "é diferente de", "==": "é igual a",
               "!=": "é diferente de", "<": "é menor que", "<=": "é menor ou igual a", ">": "é maior que",
               ">=": "é maior ou igual a"}
CONVERSOES = {"parseInt": "número inteiro", "parseFloat": "número com casas decimais", "Number": "número",
              "String": "texto"}
ARREDONDAR = {"Math.floor": "arredondado para baixo", "Math.ceil": "arredondado para cima", "Math.round": "arredondado"}
MODULOS = {
    "fs": "funções para ler, escrever e apagar arquivos",
    "child_process": "funções para executar outros programas e comandos",
    "readline": "funções para ler o que a pessoa digita no terminal",
    "path": "funções para montar caminhos de pastas e arquivos",
    "http": "funções para criar um servidor ou acessar a internet",
}
NAO_SEI = {"ClassDeclaration": "uma classe (`class`)", "ClassExpression": "uma classe (`class`)",
           "AwaitExpression": "`await`", "YieldExpression": "`yield`", "SwitchStatement": "um `switch`",
           "ThrowStatement": "um `throw`", "NewExpression": None}


def filhos(no):
    for valor in vars(no).values():
        if isinstance(valor, Node):
            yield valor
        elif isinstance(valor, list):
            yield from (v for v in valor if isinstance(v, Node))


def percorrer(no):
    pilha = [no]
    while pilha:
        atual = pilha.pop()
        yield atual
        pilha.extend(filhos(atual))


def nome_chamada(callee):
    partes = []
    while callee is not None and callee.type == "MemberExpression" and not callee.computed:
        partes.append(callee.property.name)
        callee = callee.object
    if callee is not None and callee.type == "Identifier":
        partes.append(callee.name)
        return ".".join(reversed(partes))
    return None


def eh_funcao(no):
    return no is not None and no.type in ("ArrowFunctionExpression", "FunctionExpression")


class AnalisadorJavaScript(AnalisadorBase):
    linguagem = "JavaScript"

    def analisar(self):
        try:
            programa = esprima.parseScript(self.fonte, {"loc": True, "range": True})
        except esprima.Error as erro:
            linha = getattr(erro, "lineNumber", "?")
            self.resultado.erro = (f"Não consegui ler esse código JavaScript. Pode ter um erro de digitação perto da "
                                   f"linha {linha}, ou ele usa um recurso mais novo da linguagem que eu não conheço.")
            return self.resultado
        self.bloco(programa.body, 0)
        return self.finalizar()

    def c(self, no):
        return cod(self.fonte[no.range[0]:no.range[1]])

    # ---------- valores ----------
    def valor(self, no):
        t = no.type
        if t == "Literal":
            if isinstance(no.value, bool):
                return "verdadeiro (`true`)" if no.value else "falso (`false`)"
            if no.value is None and no.raw == "null":
                return "vazio (`null`)"
            if isinstance(no.value, str):
                return f'o texto "{no.value}"' if len(no.value) <= 50 else "um texto comprido"
            if isinstance(no.value, (int, float)):
                numero = int(no.value) if float(no.value).is_integer() else no.value
                return f"o número {numero}"
            return self.c(no)
        if t == "Identifier" and no.name == "undefined":
            return "indefinido (`undefined`)"
        if t == "TemplateLiteral":
            if not no.expressions:
                return f'o texto "{no.quasis[0].value.cooked}"'
            self.conceito("texto_formatado")
            return f"um texto montado com valores dentro dele ({self.c(no)}, uma template string)"
        if t == "ArrayExpression":
            self.conceito("lista")
            n = len(no.elements)
            return "um array vazio (uma lista)" if n == 0 else f"um array (uma lista) com {n} {'item' if n == 1 else 'itens'}"
        if t == "ObjectExpression":
            self.conceito("dicionario")
            n = len(no.properties)
            return "um objeto vazio" if n == 0 else f"um objeto com {n} {'propriedade' if n == 1 else 'propriedades'} (pares de nome e valor)"
        if t == "MemberExpression":
            if not no.computed and no.property.name == "length":
                self.conceito("tamanho")
                return f"a quantidade de itens de {self.c(no.object)}"
            if no.computed and no.property.type == "Literal" and isinstance(no.property.value, (int, float)):
                return f"o item da posição {int(no.property.value)} de {self.c(no.object)} (a contagem começa em 0)"
            return self.c(no)
        if t == "CallExpression":
            return self.chamada(no)
        if t in ("BinaryExpression", "LogicalExpression") and no.operator in COMPARACOES or t == "LogicalExpression":
            return f"verdadeiro ou falso, conforme {self.condicao(no)}"
        if t == "BinaryExpression":
            return f"o resultado de {self.c(no)}"
        if t == "ConditionalExpression":
            return f"{self.valor(no.consequent)} se {self.condicao(no.test)}, ou {self.valor(no.alternate)} se não"
        return self.c(no)

    def chamada(self, no):
        nome = nome_chamada(no.callee)
        args = no.arguments
        if nome == "prompt":
            self.conceito("entrada")
            self.atividade("entrada")
            return "o que a pessoa digitar na janelinha" + (f" (aparece {self.valor(args[0])})" if args else "")
        if nome in CONVERSOES and args:
            self.conceito("conversao")
            return f"{self.valor(args[0])}, convertido para {CONVERSOES[nome]}"
        if nome == "Math.random":
            self.atividade("aleatorio")
            return "um número sorteado entre 0 e 1 (`Math.random()`)"
        if nome in ARREDONDAR and args:
            return f"{self.valor(args[0])}, {ARREDONDAR[nome]}"
        if nome in ("document.getElementById", "document.querySelector") and args:
            self.atividade("pagina")
            return f"o elemento da página encontrado por {self.c(args[0])}"
        if no.callee.type == "MemberExpression" and not no.callee.computed and args and eh_funcao(args[0]):
            metodo = no.callee.property.name
            funcao = args[0]
            param = self.c(funcao.params[0]) if funcao.params else "o item"
            corpo = funcao.body
            if metodo in ("map", "filter") and corpo.type != "BlockStatement":
                self.conceito("lista")
                if metodo == "map":
                    return f"uma lista nova com {self.c(corpo)} para cada {param} de {self.c(no.callee.object)} (isso é o `map`)"
                return f"uma lista nova só com os itens {param} de {self.c(no.callee.object)} em que {self.condicao(corpo)} (isso é o `filter`)"
        if nome in self.funcoes:
            return f"o resultado da função `{nome}` (criada na linha {self.funcoes[nome]})"
        if nome == "fetch":
            self.atividade("internet")
            return f"a resposta do endereço {self.c(args[0]) if args else ''} na internet"
        return f"o resultado de {self.c(no)}"

    def condicao(self, no):
        if no.type == "BinaryExpression" and no.operator in COMPARACOES:
            self.conceito("comparacao")
            return f"{self.c(no.left)} {COMPARACOES[no.operator]} {self.c(no.right)}"
        if no.type == "LogicalExpression":
            ligacao = " e " if no.operator == "&&" else " ou " if no.operator == "||" else f" {no.operator} "
            return f"{self.condicao(no.left)}{ligacao}{self.condicao(no.right)}"
        if no.type == "UnaryExpression" and no.operator == "!":
            return f"não for verdade que {self.condicao(no.argument)}"
        if no.type == "Literal" and no.value is True:
            return "for verdade (e `true` é sempre verdade, então só para com um `break`)"
        return f"{self.c(no)} for verdadeiro"

    # ---------- verificações da linha ----------
    def partes_da_linha(self, no):
        t = no.type
        if t in ("IfStatement", "WhileStatement", "DoWhileStatement"):
            return [no.test]
        if t == "ForStatement":
            return [p for p in (no.init, no.test, no.update) if p is not None]
        if t in ("ForOfStatement", "ForInStatement"):
            return [no.right]
        if t in ("FunctionDeclaration", "TryStatement", "BlockStatement"):
            return []
        if t == "VariableDeclaration":
            return [d.init for d in no.declarations if d.init is not None and not eh_funcao(d.init)]
        if t == "ExpressionStatement" and no.expression.type == "CallExpression" \
                and any(eh_funcao(a) for a in no.expression.arguments):
            return [a for a in no.expression.arguments if not eh_funcao(a)] + [no.expression.callee]
        return [no]

    def verificar(self, no):
        for parte in self.partes_da_linha(no):
            for filho in percorrer(parte):
                linha = filho.loc.start.line
                if filho.type == "CallExpression":
                    self.verificar_chamada(filho)
                elif filho.type == "AssignmentExpression" and filho.left.type == "MemberExpression" \
                        and not filho.left.computed and filho.left.property.name in ("innerHTML", "outerHTML"):
                    self.atividade("pagina")
                    self.alerta(linha, alerta("html_pagina"))
                elif filho.type in ("TemplateLiteral", "BinaryExpression") and SQL.search(self.fonte[filho.range[0]:filho.range[1]]) \
                        and (filho.type == "TemplateLiteral" and filho.expressions or filho.type == "BinaryExpression" and filho.operator == "+"):
                    self.alerta(linha, alerta("sql_montado"))
                elif filho.type == "Property" and filho.key.type in ("Identifier", "Literal") \
                        and NOMES_SENSIVEIS.search(str(getattr(filho.key, "name", None) or filho.key.value)) \
                        and filho.value.type == "Literal" and isinstance(filho.value.value, str):
                    nome = getattr(filho.key, "name", None) or filho.key.value
                    self.alerta(linha, alerta("segredo", nome=f"A propriedade `{nome}`"))

    def verificar_chamada(self, no):
        nome = nome_chamada(no.callee) or ""
        linha = no.loc.start.line
        alvo = self.c(no.arguments[0]) if no.arguments else "o endereço indicado"
        metodo = nome.split(".")[-1]
        if nome in ("console.log", "alert"):
            self.conceito("mostrar")
        if nome in ("eval", "Function"):
            self.alerta(linha, alerta("executa_texto"))
        elif nome == "fetch":
            self.atividade("internet")
            opcoes = self.fonte[no.range[0]:no.range[1]]
            envia = any(m in opcoes.upper() for m in ("'POST'", '"POST"', "'PUT'", '"PUT"'))
            self.alerta(linha, alerta("envia_internet" if envia else "acessa_internet", alvo=alvo))
        elif nome == "document.write":
            self.atividade("pagina")
            self.alerta(linha, alerta("html_pagina"))
        elif metodo in ("unlink", "unlinkSync", "rm", "rmSync") and nome.startswith("fs."):
            self.atividade("arquivo")
            self.alerta(linha, alerta("apaga_arquivo", alvo=alvo))
        elif metodo in ("rmdir", "rmdirSync") and nome.startswith("fs."):
            self.atividade("arquivo")
            self.alerta(linha, alerta("apaga_pasta", alvo=alvo))
        elif metodo in ("writeFile", "writeFileSync") and nome.startswith("fs."):
            self.atividade("arquivo")
            self.alerta(linha, alerta("sobrescreve_arquivo", alvo=alvo))
        elif metodo in ("execSync", "spawn", "spawnSync") or nome in ("child_process.exec", "cp.exec"):
            self.alerta(linha, alerta("executa_comando"))

    # ---------- explicação de cada instrução ----------
    def corpo(self, no):
        if no is None:
            return []
        return no.body if no.type == "BlockStatement" else [no]

    def bloco(self, corpo, nivel):
        for no in corpo:
            self.instrucao(no, nivel)

    def instrucao(self, no, nivel):
        if no.type == "EmptyStatement":
            return
        self.verificar(no)
        linha = no.loc.start.line
        for parte in self.partes_da_linha(no):
            for filho in percorrer(parte):
                if NAO_SEI.get(filho.type):
                    self.nao_sei(linha, NAO_SEI[filho.type], nivel)
                    return
        metodo = getattr(self, "explicar_" + no.type, None)
        if metodo:
            metodo(no, nivel)
        elif NAO_SEI.get(no.type):
            self.nao_sei(linha, NAO_SEI[no.type], nivel)
        else:
            self.nao_sei(linha, f"uma estrutura do tipo `{no.type}`", nivel)

    def explicar_VariableDeclaration(self, no, nivel):
        for declaracao in no.declarations:
            linha = declaracao.loc.start.line
            if declaracao.id.type != "Identifier":
                self.add(linha, f"separa as partes de {self.c(declaracao.init)} em variáveis ({self.c(declaracao.id)}).", nivel)
                continue
            nome = declaracao.id.name
            init = declaracao.init
            if eh_funcao(init):
                self.explicar_funcao(nome, init, linha, nivel)
                continue
            if init is not None and init.type == "CallExpression" and nome_chamada(init.callee) == "require" \
                    and init.arguments and init.arguments[0].type == "Literal":
                self.conceito("modulo")
                modulo = str(init.arguments[0].value)
                if modulo in ("fs", "path"):
                    self.atividade("arquivo")
                descricao = MODULOS.get(modulo, "funções prontas que não vêm carregadas por padrão")
                self.variaveis.add(nome)
                apelido = "" if nome == modulo else f" (aqui com o nome `{nome}`)"
                self.add(linha, frase("importar", modulo=f"o módulo `{modulo}`{apelido}", descricao=descricao), nivel)
                continue
            if init is None:
                self.variaveis.add(nome)
                self.conceito("variavel")
                self.add(linha, f"cria a variável `{nome}`, ainda sem valor.", nivel)
                continue
            if NOMES_SENSIVEIS.search(nome) and init.type == "Literal" and isinstance(init.value, str):
                self.variaveis.add(nome)
                self.alerta(linha, alerta("segredo", nome=f"A variável `{nome}`"))
                self.add(linha, frase("segredo", nome=f"`{nome}`"), nivel)
                continue
            self.variaveis.add(nome)
            if no.kind == "const":
                self.conceito("constante")
                self.add(linha, frase("criar_constante", nome=f"`{nome}`", valor=self.valor(init)), nivel)
            else:
                self.conceito("variavel")
                self.add(linha, frase("criar_variavel", nome=f"`{nome}`", valor=self.valor(init)), nivel)

    def explicar_funcao(self, nome, funcao, linha, nivel):
        self.conceito("funcao")
        self.atividade("funcao")
        self.funcoes[nome] = linha
        params = [self.c(p) for p in funcao.params]
        recebe = " que recebe " + ", ".join(params) if params else ", sem receber nenhum valor"
        texto = frase("funcao", nome=f"`{nome}`", recebe=recebe)
        if funcao.type == "ArrowFunctionExpression":
            texto += " Ela foi escrita no formato de arrow function (`=>`), um jeito mais curto de criar funções."
        self.add(linha, texto, nivel)
        if funcao.body.type == "BlockStatement":
            self.bloco(funcao.body.body, nivel + 1)
        else:
            self.add(funcao.body.loc.start.line, frase("retorno", valor=self.valor(funcao.body)), nivel + 1)

    def explicar_FunctionDeclaration(self, no, nivel):
        self.explicar_funcao(no.id.name, no, no.loc.start.line, nivel)

    def explicar_ReturnStatement(self, no, nivel):
        self.conceito("return")
        if no.argument is None:
            self.add(no.loc.start.line, frase("retorno_vazio"), nivel)
        else:
            self.add(no.loc.start.line, frase("retorno", valor=self.valor(no.argument)), nivel)

    def explicar_ExpressionStatement(self, no, nivel):
        e = no.expression
        linha = no.loc.start.line
        if e.type == "AssignmentExpression":
            self.explicar_atribuicao(e, linha, nivel)
        elif e.type == "UpdateExpression":
            chave = "incrementar" if e.operator == "++" else "decrementar"
            self.add(linha, frase(chave, nome=self.c(e.argument)), nivel)
        elif e.type == "CallExpression":
            self.explicar_chamada(e, linha, nivel)
        elif e.type == "Literal" and e.value == "use strict":
            self.add(linha, "liga o modo estrito do JavaScript, que reclama de alguns erros em vez de deixar passar.", nivel)
        else:
            self.add(linha, f"calcula {self.c(e)}, mas não guarda o resultado em lugar nenhum.", nivel)

    def explicar_atribuicao(self, e, linha, nivel):
        alvo = e.left
        if alvo.type == "MemberExpression" and not alvo.computed and alvo.property.name in ("innerHTML", "textContent", "innerText", "value"):
            self.atividade("pagina")
            onde = self.c(alvo.object)
            if alvo.property.name == "innerHTML":
                self.add(linha, f"coloca {self.valor(e.right)} como HTML dentro do elemento {onde} da página.", nivel)
            elif alvo.property.name == "value":
                self.add(linha, f"troca o valor do campo {onde} da página por {self.valor(e.right)}.", nivel)
            else:
                self.add(linha, f"troca o texto do elemento {onde} da página por {self.valor(e.right)}.", nivel)
            return
        nome = self.c(alvo)
        if alvo.type == "Identifier" and NOMES_SENSIVEIS.search(alvo.name) and e.right.type == "Literal" \
                and isinstance(e.right.value, str):
            self.alerta(linha, alerta("segredo", nome=f"A variável `{alvo.name}`"))
            self.add(linha, frase("segredo", nome=nome), nivel)
            return
        if e.operator == "+=":
            self.add(linha, frase("somar_em", valor=self.c(e.right), nome=nome), nivel)
        elif e.operator == "-=":
            self.add(linha, frase("subtrair_de", valor=self.c(e.right), nome=nome), nivel)
        elif e.operator != "=":
            self.add(linha, frase("operar_em", nome=nome, operador=f"`{e.operator}`"), nivel)
        elif e.right.type == "BinaryExpression" and e.right.left.type == "Identifier" and alvo.type == "Identifier" \
                and e.right.left.name == alvo.name and e.right.operator in ("+", "-"):
            chave = "somar_em" if e.right.operator == "+" else "subtrair_de"
            self.add(linha, frase(chave, valor=self.c(e.right.right), nome=nome), nivel)
        else:
            self.add(linha, frase("mudar_variavel", nome=nome, valor=self.valor(e.right)), nivel)

    def explicar_chamada(self, e, linha, nivel):
        nome = nome_chamada(e.callee) or ""
        args = e.arguments
        metodo = e.callee.property.name if e.callee.type == "MemberExpression" and not e.callee.computed else None
        if nome == "console.log":
            self.atividade("saida")
            partes = " seguido de ".join(self.valor(a) for a in args) or "uma linha em branco"
            self.add(linha, frase("mostrar", partes=partes), nivel)
        elif nome == "alert":
            self.atividade("saida")
            self.add(linha, frase("janela", partes=" seguido de ".join(self.valor(a) for a in args) or "uma mensagem vazia"), nivel)
        elif metodo == "push" and args:
            self.conceito("lista")
            self.add(linha, frase("adicionar_lista", valor=self.valor(args[0]), lista=self.c(e.callee.object)), nivel)
        elif metodo == "forEach" and args and eh_funcao(args[0]):
            self.conceito("for")
            self.atividade("laco")
            funcao = args[0]
            var = self.c(funcao.params[0]) if funcao.params else "o item"
            self.add(linha, frase("for_cada", origem=self.c(e.callee.object), var=var).replace("um laço `for`", "um `forEach` (parecido com um laço `for`)"), nivel)
            self.corpo_funcao(funcao, nivel + 1)
        elif metodo == "addEventListener" and len(args) > 1 and eh_funcao(args[1]):
            self.atividade("pagina")
            evento = self.valor(args[0]).replace("o texto ", "")
            self.add(linha, f"fica esperando o evento {evento} acontecer em {self.c(e.callee.object)}. Quando acontecer, executa o bloco abaixo.", nivel)
            self.corpo_funcao(args[1], nivel + 1)
        elif nome == "setTimeout" and args and eh_funcao(args[0]):
            espera = self.c(args[1]) if len(args) > 1 else "`0`"
            self.add(linha, f"espera {espera} milissegundos (1000 = 1 segundo) e depois executa o bloco abaixo.", nivel)
            self.corpo_funcao(args[0], nivel + 1)
        elif any(eh_funcao(a) for a in args):
            self.nao_sei(linha, f"uma função passada como valor para {self.c(e.callee)} (um callback)", nivel)
        elif nome in self.funcoes:
            self.add(linha, frase("chamar_funcao_do_codigo", nome=f"`{nome}`", linha=self.funcoes[nome]), nivel)
        elif nome == "fetch":
            opcoes = self.fonte[e.range[0]:e.range[1]].upper()
            chave = "envia_internet" if '"POST"' in opcoes or "'POST'" in opcoes else "acessa_internet"
            self.add(linha, alerta(chave, alvo=self.c(args[0]) if args else "um endereço") + ".", nivel)
        elif nome.startswith("fs.") and metodo in ("unlink", "unlinkSync", "rm", "rmSync"):
            self.add(linha, alerta("apaga_arquivo", alvo=self.c(args[0]) if args else "") + ".", nivel)
        else:
            self.add(linha, frase("chamar", codigo=self.c(e)), nivel)

    def corpo_funcao(self, funcao, nivel):
        if funcao.body.type == "BlockStatement":
            self.bloco(funcao.body.body, nivel)
        else:
            self.add(funcao.body.loc.start.line, f"calcula {self.c(funcao.body)}.", nivel)

    def explicar_IfStatement(self, no, nivel):
        self.conceito("if")
        self.atividade("decisao")
        self.add(no.loc.start.line, frase("if", condicao=self.condicao(no.test)), nivel)
        self.bloco(self.corpo(no.consequent), nivel + 1)
        atual = no
        while atual.alternate is not None:
            if atual.alternate.type == "IfStatement":
                atual = atual.alternate
                self.add(atual.loc.start.line, frase("elif", condicao=self.condicao(atual.test)), nivel)
                self.bloco(self.corpo(atual.consequent), nivel + 1)
            else:
                self.add(atual.alternate.loc.start.line, frase("else"), nivel)
                self.bloco(self.corpo(atual.alternate), nivel + 1)
                break

    def explicar_ForStatement(self, no, nivel):
        self.conceito("for")
        self.atividade("laco")
        inicio = "sem valor inicial"
        if no.init is not None and no.init.type == "VariableDeclaration" and no.init.declarations[0].init is not None:
            d = no.init.declarations[0]
            self.variaveis.add(self.c(d.id).strip("`"))
            inicio = f"{self.c(d.id)} valendo {self.c(d.init)}"
        elif no.init is not None:
            inicio = self.c(no.init)
        condicao = self.condicao(no.test) if no.test is not None else "sempre (não tem condição)"
        if no.update is not None and no.update.type == "UpdateExpression":
            passo = f"{'aumenta' if no.update.operator == '++' else 'diminui'} {self.c(no.update.argument)} em 1"
        elif no.update is not None:
            passo = f"executa {self.c(no.update)}"
        else:
            passo = "não muda nada sozinho"
        self.add(no.loc.start.line, frase("for_contador", inicio=inicio, condicao=condicao, passo=passo), nivel)
        self.bloco(self.corpo(no.body), nivel + 1)

    def var_do_laco(self, esquerda):
        if esquerda.type == "VariableDeclaration":
            return self.c(esquerda.declarations[0].id)
        return self.c(esquerda)

    def explicar_ForOfStatement(self, no, nivel):
        self.conceito("for")
        self.atividade("laco")
        origem = self.c(no.right) if no.right.type == "Identifier" else self.valor(no.right)
        self.add(no.loc.start.line, frase("for_cada", origem=origem, var=self.var_do_laco(no.left)), nivel)
        self.bloco(self.corpo(no.body), nivel + 1)

    def explicar_ForInStatement(self, no, nivel):
        self.conceito("for")
        self.atividade("laco")
        self.add(no.loc.start.line, frase("for_chaves", origem=self.c(no.right), var=self.var_do_laco(no.left)), nivel)
        self.bloco(self.corpo(no.body), nivel + 1)

    def explicar_WhileStatement(self, no, nivel):
        self.conceito("while")
        self.atividade("laco")
        if no.test.type == "Literal" and no.test.value is True:
            self.add(no.loc.start.line, frase("while_infinito").replace("`while True`", "`while (true)`"), nivel)
        else:
            self.add(no.loc.start.line, frase("while", condicao=self.condicao(no.test)), nivel)
        self.bloco(self.corpo(no.body), nivel + 1)

    def explicar_DoWhileStatement(self, no, nivel):
        self.conceito("while")
        self.atividade("laco")
        self.add(no.loc.start.line, frase("do_while", condicao=self.condicao(no.test)), nivel)
        self.bloco(self.corpo(no.body), nivel + 1)

    def explicar_BreakStatement(self, no, nivel):
        self.add(no.loc.start.line, frase("break"), nivel)

    def explicar_ContinueStatement(self, no, nivel):
        self.add(no.loc.start.line, frase("continue"), nivel)

    def explicar_BlockStatement(self, no, nivel):
        self.bloco(no.body, nivel)

    def explicar_TryStatement(self, no, nivel):
        self.conceito("try")
        self.add(no.loc.start.line, frase("try"), nivel)
        self.bloco(no.block.body, nivel + 1)
        if no.handler is not None:
            nome = f" (o erro fica guardado em {self.c(no.handler.param)})" if no.handler.param is not None else ""
            self.add(no.handler.loc.start.line, frase("except", tipo=nome).replace("`try`", "`try`, no `catch`"), nivel)
            self.bloco(no.handler.body.body, nivel + 1)
        if no.finalizer is not None:
            self.add(no.finalizer.loc.start.line, frase("finally"), nivel)
            self.bloco(no.finalizer.body, nivel + 1)


def analisar(fonte):
    return AnalisadorJavaScript(fonte).analisar()
