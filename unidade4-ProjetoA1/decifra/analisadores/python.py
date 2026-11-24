"""Analisador de Python: lê o código com o módulo ast (que já vem com o Python)."""
import ast

from decifra.textos import NOMES_SENSIVEIS, SQL, AnalisadorBase, alerta, cod, frase

FUNCOES = {
    "len": ("conta quantos itens tem em", "tamanho"),
    "sum": ("soma todos os itens de", None),
    "max": ("pega o maior valor de", None),
    "min": ("pega o menor valor de", None),
    "round": ("arredonda", None),
    "sorted": ("cria uma cópia ordenada de", None),
    "abs": ("pega o valor sem sinal de", None),
}
CONVERSOES = {"int": "número inteiro", "float": "número com casas decimais", "str": "texto"}
MODULOS = {
    "os": "funções para mexer com arquivos, pastas e o sistema",
    "random": "funções para sortear números e escolhas",
    "math": "funções de matemática, como raiz quadrada",
    "time": "funções para lidar com tempo e pausas",
    "datetime": "funções para trabalhar com datas e horas",
    "shutil": "funções para copiar, mover e apagar arquivos e pastas",
    "subprocess": "funções para executar outros programas",
    "requests": "funções para acessar a internet",
    "json": "funções para ler e escrever dados no formato JSON",
    "sqlite3": "funções para usar um banco de dados SQLite",
    "sys": "funções para conversar com o próprio Python e o sistema",
}
PERIGOS = {
    "os.remove": "apaga_arquivo", "os.unlink": "apaga_arquivo", "os.rmdir": "apaga_pasta",
    "shutil.rmtree": "apaga_pasta", "os.system": "executa_comando", "subprocess.run": "executa_comando",
    "subprocess.call": "executa_comando", "subprocess.Popen": "executa_comando",
    "eval": "executa_texto", "exec": "executa_texto",
    "requests.post": "envia_internet", "requests.put": "envia_internet", "requests.get": "acessa_internet",
    "urllib.request.urlopen": "acessa_internet",
}
COMPARACOES = {ast.Eq: "é igual a", ast.NotEq: "é diferente de", ast.Lt: "é menor que", ast.LtE: "é menor ou igual a",
               ast.Gt: "é maior que", ast.GtE: "é maior ou igual a", ast.In: "está em", ast.NotIn: "não está em",
               ast.Is: "é", ast.IsNot: "não é"}
OPERADORES = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.FloorDiv: "//", ast.Mod: "%", ast.Pow: "**"}
NAO_SEI = {ast.Lambda: "uma função `lambda`", ast.ClassDef: "uma classe (`class`)", ast.DictComp: "uma dict comprehension",
           ast.SetComp: "uma set comprehension", ast.GeneratorExp: "uma expressão geradora", ast.Yield: "`yield`",
           ast.AsyncFunctionDef: "uma função assíncrona (`async`)", ast.Await: "`await`", ast.Global: "`global`",
           ast.Match: "um `match`", ast.Assert: "um `assert`", ast.Raise: "um `raise`"}


def nome_chamada(no):
    if isinstance(no.func, ast.Name):
        return no.func.id
    if isinstance(no.func, ast.Attribute):
        partes = []
        alvo = no.func
        while isinstance(alvo, ast.Attribute):
            partes.append(alvo.attr)
            alvo = alvo.value
        if isinstance(alvo, ast.Name):
            partes.append(alvo.id)
            return ".".join(reversed(partes))
    return None


class AnalisadorPython(AnalisadorBase):
    linguagem = "Python"

    def c(self, no):
        """Cita o trecho exatamente como está escrito no código."""
        trecho = ast.get_source_segment(self.fonte, no)
        return cod(trecho if trecho is not None else ast.unparse(no))

    def analisar(self):
        try:
            arvore = ast.parse(self.fonte)
        except SyntaxError as erro:
            self.resultado.erro = f"Não consegui ler esse código Python. Pode ter um erro de digitação perto da linha {erro.lineno}."
            return self.resultado
        self.bloco(arvore.body, 0)
        return self.finalizar()

    # ---------- valores ----------
    def valor(self, no):
        if isinstance(no, ast.Constant):
            if isinstance(no.value, bool):
                return "verdadeiro (`True`)" if no.value else "falso (`False`)"
            if isinstance(no.value, str):
                return f'o texto "{no.value}"' if len(no.value) <= 50 else "um texto comprido"
            if no.value is None:
                return "vazio (`None`)"
            return f"o número {no.value}"
        if isinstance(no, ast.List):
            self.conceito("lista")
            if not no.elts:
                return "uma lista vazia"
            return f"uma lista com {len(no.elts)} {'item' if len(no.elts) == 1 else 'itens'}"
        if isinstance(no, ast.Dict):
            self.conceito("dicionario")
            return f"um dicionário com {len(no.keys)} pares de chave e valor" if no.keys else "um dicionário vazio"
        if isinstance(no, ast.JoinedStr):
            self.conceito("texto_formatado")
            return f"um texto montado com valores dentro dele ({self.c(no)}, uma f-string)"
        if isinstance(no, ast.ListComp):
            return self.list_comprehension(no)
        if isinstance(no, ast.Subscript):
            if isinstance(no.slice, ast.Constant) and isinstance(no.slice.value, int):
                return f"o item da posição {no.slice.value} de {self.c(no.value)} (a contagem começa em 0)"
            if isinstance(no.slice, ast.Constant) and isinstance(no.slice.value, str):
                return f'o valor da chave "{no.slice.value}" em {self.c(no.value)}'
            return f"o item {self.c(no.slice)} de {self.c(no.value)}"
        if isinstance(no, ast.Call):
            return self.chamada(no)
        if isinstance(no, ast.BinOp):
            return f"o resultado de {self.c(no)}"
        if isinstance(no, ast.Compare):
            return f"verdadeiro ou falso, conforme {self.condicao(no)}"
        return self.c(no)

    def list_comprehension(self, no):
        gerador = no.generators[0]
        if len(no.generators) > 1 or not isinstance(gerador.target, ast.Name):
            return f"uma lista criada com uma list comprehension mais complexa ({self.c(no)})"
        self.conceito("lista")
        texto = f"uma lista nova com {self.c(no.elt)} para cada {self.c(gerador.target)} de {self.c(gerador.iter)}"
        if gerador.ifs:
            texto += f", só quando {self.condicao(gerador.ifs[0])}"
        return texto + " (isso é uma list comprehension)"

    def chamada(self, no):
        nome = nome_chamada(no)
        args = [self.valor(a) for a in no.args]
        if nome == "input":
            self.conceito("entrada")
            self.atividade("entrada")
            return "o que a pessoa digitar" + (f" (aparece {args[0]})" if args else "")
        if nome in CONVERSOES and args:
            self.conceito("conversao")
            return f"{args[0]}, convertido para {CONVERSOES[nome]}"
        if nome == "range":
            self.conceito("range")
            return f"os números de {self.inicio_range(no)} até {self.fim_range(no)}"
        if nome in FUNCOES and args:
            descricao, conceito = FUNCOES[nome]
            if conceito:
                self.conceito(conceito)
            return f"o resultado de {self.c(no)} ({descricao} {args[0]})"
        if nome and nome.startswith("random."):
            self.atividade("aleatorio")
            return f"um valor sorteado ({self.c(no)})"
        if nome == "os.listdir":
            self.atividade("arquivo")
            return f"os nomes dos arquivos da pasta {self.c(no.args[0]) if no.args else ''}".strip()
        if nome in self.funcoes:
            return f"o resultado da função `{nome}` (criada na linha {self.funcoes[nome]})"
        if isinstance(no.func, ast.Attribute) and no.func.attr in ("upper", "lower", "strip", "split"):
            nomes = {"upper": "em letras maiúsculas", "lower": "em letras minúsculas",
                     "strip": "sem os espaços do começo e do fim", "split": "separado em pedaços"}
            return f"o texto de {self.c(no.func.value)} {nomes[no.func.attr]}"
        return f"o resultado de {self.c(no)}"

    def inicio_range(self, no):
        return ast.unparse(no.args[0]) if len(no.args) > 1 else "0"

    def fim_range(self, no):
        fim = no.args[1] if len(no.args) > 1 else no.args[0]
        if isinstance(fim, ast.Constant) and isinstance(fim.value, int):
            return str(fim.value - 1)
        return f"{ast.unparse(fim)} - 1"

    def condicao(self, no):
        if isinstance(no, ast.Compare) and len(no.ops) == 1 and type(no.ops[0]) in COMPARACOES:
            self.conceito("comparacao")
            return f"{self.c(no.left)} {COMPARACOES[type(no.ops[0])]} {self.c(no.comparators[0])}"
        if isinstance(no, ast.BoolOp):
            ligacao = " e " if isinstance(no.op, ast.And) else " ou "
            return ligacao.join(self.condicao(v) for v in no.values)
        if isinstance(no, ast.UnaryOp) and isinstance(no.op, ast.Not):
            return f"não for verdade que {self.condicao(no.operand)}"
        if isinstance(no, ast.Constant) and no.value is True:
            return "for verdade (e `True` é sempre verdade, então só para com um `break`)"
        return f"{self.c(no)} for verdadeiro"

    # ---------- verificações da linha ----------
    def partes_da_linha(self, no):
        """Só o que pertence à própria linha (os blocos de dentro são verificados quando chegar neles)."""
        if isinstance(no, (ast.If, ast.While)):
            return [no.test]
        if isinstance(no, ast.For):
            return [no.iter]
        if isinstance(no, ast.With):
            return [item.context_expr for item in no.items]
        if isinstance(no, (ast.FunctionDef, ast.Try)):
            return []
        return [no]

    def verificar(self, no):
        for parte in self.partes_da_linha(no):
            for filho in ast.walk(parte):
                if isinstance(filho, ast.Call):
                    self.verificar_chamada(filho)
                if isinstance(filho, (ast.JoinedStr, ast.BinOp)) and SQL.search(ast.unparse(filho)) \
                        and not isinstance(filho, ast.Constant):
                    self.alerta(filho.lineno, alerta("sql_montado"))
                if isinstance(filho, ast.Call) and isinstance(filho.func, ast.Attribute) and filho.func.attr == "format" \
                        and isinstance(filho.func.value, ast.Constant) and SQL.search(str(filho.func.value.value)):
                    self.alerta(filho.lineno, alerta("sql_montado"))

    def verificar_chamada(self, no):
        nome = nome_chamada(no)
        alvo = self.c(no.args[0]) if no.args else "o endereço indicado"
        if nome == "print":
            self.conceito("mostrar")
        elif nome in FUNCOES and FUNCOES[nome][1]:
            self.conceito(FUNCOES[nome][1])
        if nome in PERIGOS:
            self.alerta(no.lineno, alerta(PERIGOS[nome], alvo=alvo))
            self.atividade("internet" if "internet" in PERIGOS[nome] else "arquivo")
        if nome == "open":
            self.atividade("arquivo")
            modo = no.args[1] if len(no.args) > 1 else next((k.value for k in no.keywords if k.arg == "mode"), None)
            if isinstance(modo, ast.Constant) and "w" in str(modo.value):
                self.alerta(no.lineno, alerta("sobrescreve_arquivo", alvo=alvo))

    # ---------- explicação de cada instrução ----------
    def bloco(self, corpo, nivel):
        for no in corpo:
            self.instrucao(no, nivel)

    def instrucao(self, no, nivel):
        self.verificar(no)
        for parte in self.partes_da_linha(no):
            for filho in ast.walk(parte):
                if type(filho) in NAO_SEI:
                    self.nao_sei(no.lineno, NAO_SEI[type(filho)], nivel)
                    return
        metodo = getattr(self, "explicar_" + type(no).__name__, None)
        if metodo:
            metodo(no, nivel)
        elif type(no) in NAO_SEI:
            self.nao_sei(no.lineno, NAO_SEI[type(no)], nivel)
        else:
            self.nao_sei(no.lineno, f"uma estrutura do tipo `{type(no).__name__}`", nivel)

    def explicar_Assign(self, no, nivel):
        if len(no.targets) != 1:
            self.add(no.lineno, f"guarda o mesmo valor em várias variáveis ao mesmo tempo: {self.c(no)}.", nivel)
            return
        alvo = no.targets[0]
        if isinstance(alvo, ast.Tuple):
            nomes = ", ".join(self.c(e) for e in alvo.elts)
            self.add(no.lineno, f"guarda valores em {nomes} de uma vez só (cada variável recebe uma parte de {self.c(no.value)}).", nivel)
            return
        if isinstance(alvo, ast.Subscript):
            self.add(no.lineno, f"guarda {self.valor(no.value)} em {self.c(alvo)}.", nivel)
            return
        if not isinstance(alvo, ast.Name):
            self.add(no.lineno, f"guarda {self.valor(no.value)} em {self.c(alvo)}.", nivel)
            return
        nome = alvo.id
        if NOMES_SENSIVEIS.search(nome) and isinstance(no.value, ast.Constant) and isinstance(no.value.value, str):
            self.variaveis.add(nome)
            self.alerta(no.lineno, alerta("segredo", nome=f"A variável `{nome}`"))
            self.add(no.lineno, frase("segredo", nome=f"`{nome}`"), nivel)
            return
        v = no.value
        if isinstance(v, ast.BinOp) and isinstance(v.left, ast.Name) and v.left.id == nome and type(v.op) in (ast.Add, ast.Sub):
            chave = "somar_em" if isinstance(v.op, ast.Add) else "subtrair_de"
            self.add(no.lineno, frase(chave, valor=self.c(v.right), nome=f"`{nome}`"), nivel)
            return
        self.conceito("variavel")
        chave = "mudar_variavel" if nome in self.variaveis else "criar_variavel"
        self.variaveis.add(nome)
        self.add(no.lineno, frase(chave, nome=f"`{nome}`", valor=self.valor(v)), nivel)

    def explicar_AugAssign(self, no, nivel):
        nome = self.c(no.target)
        if isinstance(no.op, ast.Add):
            self.add(no.lineno, frase("somar_em", valor=self.c(no.value), nome=nome), nivel)
        elif isinstance(no.op, ast.Sub):
            self.add(no.lineno, frase("subtrair_de", valor=self.c(no.value), nome=nome), nivel)
        else:
            self.add(no.lineno, frase("operar_em", nome=nome, operador=f"`{OPERADORES.get(type(no.op), '?')}=`"), nivel)

    def explicar_For(self, no, nivel):
        self.conceito("for")
        self.atividade("laco")
        var = self.c(no.target)
        if isinstance(no.target, ast.Name):
            self.variaveis.add(no.target.id)
        it = no.iter
        if isinstance(it, ast.Call) and nome_chamada(it) == "range" and it.args:
            self.conceito("range")
            texto = frase("for_numeros", inicio=self.inicio_range(it), fim=self.fim_range(it), var=var)
        elif isinstance(it, ast.Call) and nome_chamada(it) == "os.listdir" and it.args:
            self.atividade("arquivo")
            texto = frase("for_arquivos", pasta=self.c(it.args[0]), var=var)
        else:
            origem = self.c(it) if isinstance(it, ast.Name) else self.valor(it)
            texto = frase("for_cada", origem=origem, var=var)
        self.add(no.lineno, texto, nivel)
        self.bloco(no.body, nivel + 1)

    def explicar_While(self, no, nivel):
        self.conceito("while")
        self.atividade("laco")
        if isinstance(no.test, ast.Constant) and no.test.value is True:
            self.add(no.lineno, frase("while_infinito"), nivel)
        else:
            self.add(no.lineno, frase("while", condicao=self.condicao(no.test)), nivel)
        self.bloco(no.body, nivel + 1)

    def explicar_If(self, no, nivel):
        teste = ast.unparse(no.test)
        if teste in ("__name__ == '__main__'", '__name__ == "__main__"'):
            self.add(no.lineno, frase("principal"), nivel)
            self.bloco(no.body, nivel + 1)
            return
        self.conceito("if")
        self.atividade("decisao")
        self.add(no.lineno, frase("if", condicao=self.condicao(no.test)), nivel)
        self.bloco(no.body, nivel + 1)
        atual = no
        while atual.orelse:
            if len(atual.orelse) == 1 and isinstance(atual.orelse[0], ast.If) \
                    and self.linha_fonte(atual.orelse[0].lineno).lstrip().startswith("elif"):
                atual = atual.orelse[0]
                self.add(atual.lineno, frase("elif", condicao=self.condicao(atual.test)), nivel)
                self.bloco(atual.body, nivel + 1)
            else:
                self.add(self.linha_do_else(atual.orelse[0].lineno), frase("else"), nivel)
                self.bloco(atual.orelse, nivel + 1)
                break

    def linha_fonte(self, numero):
        linhas = self.fonte.splitlines()
        return linhas[numero - 1] if 0 < numero <= len(linhas) else ""

    def linha_do_else(self, primeira_do_bloco):
        for numero in range(primeira_do_bloco, 0, -1):
            if self.linha_fonte(numero).strip().startswith("else"):
                return numero
        return primeira_do_bloco - 1

    def explicar_FunctionDef(self, no, nivel):
        self.conceito("funcao")
        self.atividade("funcao")
        self.funcoes[no.name] = no.lineno
        params = [a.arg for a in no.args.args]
        self.variaveis.update(params)
        recebe = " que recebe " + ", ".join(f"`{p}`" for p in params) if params else ", sem receber nenhum valor"
        self.add(no.lineno, frase("funcao", nome=f"`{no.name}`", recebe=recebe), nivel)
        self.bloco(no.body, nivel + 1)

    def explicar_Return(self, no, nivel):
        self.conceito("return")
        if no.value is None:
            self.add(no.lineno, frase("retorno_vazio"), nivel)
        else:
            self.add(no.lineno, frase("retorno", valor=self.valor(no.value)), nivel)

    def explicar_Import(self, no, nivel):
        self.conceito("modulo")
        nomes = [a.name for a in no.names]
        descricao = MODULOS.get(nomes[0].split(".")[0], "funções prontas que não vêm carregadas por padrão")
        if "requests" in nomes:
            self.atividade("internet")
        self.add(no.lineno, frase("importar", modulo=", ".join(f"o módulo `{n}`" for n in nomes), descricao=descricao), nivel)

    def explicar_ImportFrom(self, no, nivel):
        self.conceito("modulo")
        coisas = ", ".join(f"`{a.name}`" for a in no.names)
        descricao = MODULOS.get((no.module or "").split(".")[0], "funções prontas que não vêm carregadas por padrão")
        self.add(no.lineno, frase("importar", modulo=f"{coisas} do módulo `{no.module}`", descricao=descricao), nivel)

    def explicar_Expr(self, no, nivel):
        v = no.value
        if isinstance(v, ast.Constant) and isinstance(v.value, str):
            self.add(no.lineno, "é um texto solto que serve de comentário ou documentação (docstring). Não faz nada quando o programa roda.", nivel)
            return
        if not isinstance(v, ast.Call):
            self.add(no.lineno, f"calcula {self.c(v)}, mas não guarda o resultado em lugar nenhum.", nivel)
            return
        nome = nome_chamada(v)
        if nome == "print":
            self.atividade("saida")
            partes = " seguido de ".join(self.valor(a) for a in v.args) or "uma linha em branco"
            self.add(no.lineno, frase("mostrar", partes=partes), nivel)
        elif nome in PERIGOS:
            alvo = self.c(v.args[0]) if v.args else "o endereço indicado"
            self.add(no.lineno, alerta(PERIGOS[nome], alvo=alvo) + ".", nivel)
        elif isinstance(v.func, ast.Attribute) and v.func.attr == "write" and v.args:
            self.add(no.lineno, frase("escrever_arquivo", valor=self.valor(v.args[0]), arquivo=self.c(v.func.value)), nivel)
        elif isinstance(v.func, ast.Attribute) and v.func.attr == "append" and v.args:
            self.conceito("lista")
            self.add(no.lineno, frase("adicionar_lista", valor=self.valor(v.args[0]), lista=self.c(v.func.value)), nivel)
        elif nome in self.funcoes:
            self.add(no.lineno, frase("chamar_funcao_do_codigo", nome=f"`{nome}`", linha=self.funcoes[nome]), nivel)
        else:
            self.add(no.lineno, frase("chamar", codigo=self.c(v)), nivel)

    def explicar_Break(self, no, nivel):
        self.add(no.lineno, frase("break"), nivel)

    def explicar_Continue(self, no, nivel):
        self.add(no.lineno, frase("continue"), nivel)

    def explicar_Pass(self, no, nivel):
        self.add(no.lineno, frase("pass"), nivel)

    def explicar_Try(self, no, nivel):
        self.conceito("try")
        self.add(no.lineno, frase("try"), nivel)
        self.bloco(no.body, nivel + 1)
        for tratador in no.handlers:
            tipo = f" (se o erro for do tipo `{ast.unparse(tratador.type)}`)" if tratador.type else ""
            self.add(tratador.lineno, frase("except", tipo=tipo), nivel)
            self.bloco(tratador.body, nivel + 1)
        if no.finalbody:
            self.add(self.linha_do_else(no.finalbody[0].lineno), frase("finally"), nivel)
            self.bloco(no.finalbody, nivel + 1)

    def explicar_With(self, no, nivel):
        item = no.items[0]
        chamada = item.context_expr
        if isinstance(chamada, ast.Call) and nome_chamada(chamada) == "open" and item.optional_vars is not None:
            self.conceito("arquivo")
            modo_no = chamada.args[1] if len(chamada.args) > 1 else None
            modo = str(modo_no.value) if isinstance(modo_no, ast.Constant) else "r"
            texto_modo = "escrever (apagando o que tinha antes)" if "w" in modo else \
                "acrescentar coisas no final" if "a" in modo else "ler"
            arquivo = self.c(chamada.args[0]) if chamada.args else "um arquivo"
            self.add(no.lineno, frase("abrir_arquivo", arquivo=arquivo, modo=texto_modo, nome=self.c(item.optional_vars)), nivel)
            self.bloco(no.body, nivel + 1)
        else:
            self.nao_sei(no.lineno, "um bloco `with`", nivel)
            self.bloco(no.body, nivel + 1)


def analisar(fonte):
    return AnalisadorPython(fonte).analisar()
