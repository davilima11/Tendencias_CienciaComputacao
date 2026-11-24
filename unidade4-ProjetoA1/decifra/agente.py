"""O DecifraBot, organizado nas 4 camadas vistas na Unidade 4:

1. perceber -> camada perceptiva: separa código de pergunta, esconde senhas, confere a linguagem
2. entender -> camada cognitiva: lê o código com o analisador da linguagem, ou entende a pergunta com TF-IDF
3. decidir  -> camada decisória: aplica as regras (dado sensível, linguagem, limiar, pedido de código)
4. executar -> camada executiva: monta a resposta
"""
import ast
import json
import re
import unicodedata
from pathlib import Path

from decifra.analisadores import javascript, python
from decifra.linguagem import OUTRAS, detectar, le_javascript, le_python
from decifra.memoria import Memoria
from decifra.privacidade import dado_sensivel_no_texto, mascarar_codigo
from decifra.tfidf import TfIdf

BASE_PADRAO = Path(__file__).resolve().parent.parent / "dados" / "conhecimento.json"
ANALISADORES = {"Python": python.analisar, "JavaScript": javascript.analisar}
CONSEGUE_LER = {"Python": le_python, "JavaScript": le_javascript}
OUTRA = {"Python": "JavaScript", "JavaScript": "Python"}

# limiares de confiança para perguntas (escolhidos testando, ver documentacao/4-testes.md)
LIMIAR_ALTO = 0.55
LIMIAR_BAIXO = 0.40
# a partir daqui a explicação fica comprida demais para ler numa conversa
LIMITE_LINHAS = 80

PEDE_LINHA = re.compile(r"\blinha\s*(\d+)\b", re.IGNORECASE)
TROCA_LINGUAGEM = re.compile(r"^\s*(?:(?:é|e|eh|isso é|isso e|ta em|está em|esta em|o código é|o codigo e)\s+)?(javascript|js|python|py)\s*[.!]?\s*$", re.IGNORECASE)
NOMES_LINGUAGEM = {"javascript": "JavaScript", "js": "JavaScript", "python": "Python", "py": "Python"}
# verbo de pedido + algo para fazer: "faz esse código pra mim", "arruma meu código", "resolve o exercício"
PEDIDO_CODIGO = re.compile(r"\b(faz|faca|fazer|cria|crie|criar|escreve|escreva|escrever|corrige|corrija|corrigir|conserta|"
                           r"conserte|arruma|arrume|melhora|melhore|resolve|resolva|gera|gere)\b.*"
                           r"\b(codigo|programa|script|exercicio|questao|atividade|para mim)\b")


def sem_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def parece_codigo(texto):
    """Código tem cara de código: o Python ou o JavaScript conseguem ler e tem algum símbolo de código."""
    limpo = texto.strip()
    if not limpo:
        return False
    tem_simbolo = "\n" in limpo or re.search(r"[=(){}\[\];:<>]", limpo)
    if not tem_simbolo:
        return False
    if PEDE_LINHA.search(limpo) and len(limpo) < 40:
        return False
    if le_python(limpo):
        arvore = ast.parse(limpo)
        sozinho = len(arvore.body) == 1 and isinstance(arvore.body[0], ast.Expr) \
            and isinstance(arvore.body[0].value, (ast.Name, ast.Constant))
        return not sozinho
    if le_javascript(limpo):
        return True
    # não leu em nenhuma, mas pode ser código de outra linguagem (SQL, Java...) ou código com erro
    if any(re.search(padrao, limpo, re.MULTILINE) for padrao in OUTRAS.values()):
        return True
    return "\n" in limpo or bool(re.search(r"[;{}]|\w+\(.*\)|<\w+>", limpo))


class Agente:
    def __init__(self, caminho_base=BASE_PADRAO):
        with open(caminho_base, encoding="utf-8") as arquivo:
            base = json.load(arquivo)
        self.conceitos = base["conceitos"]
        self.intencoes = base["intencoes"]
        self.msgs = base["mensagens"]
        self.sinonimos = base["sinonimos"]
        self.memoria = Memoria()
        frases, self.rotulos = [], []
        for chave, conceito in self.conceitos.items():
            for pergunta in conceito["perguntas"]:
                frases.append(self.normalizar(pergunta))
                self.rotulos.append("conceito:" + chave)
        for nome, intencao in self.intencoes.items():
            for exemplo in intencao["exemplos"]:
                frases.append(self.normalizar(exemplo))
                self.rotulos.append(nome)
        self.tfidf = TfIdf(frases)

    def normalizar(self, texto):
        texto = sem_acento(texto.lower())
        texto = re.sub(r"[^\w\s=]", " ", texto)
        return " ".join(self.sinonimos.get(p, p) for p in texto.split())

    # ---------- camada 1: perceptiva ----------
    def perceber(self, texto):
        texto = (texto or "").strip("\n")
        percepcao = {"original": texto, "eh_codigo": parece_codigo(texto), "dado_sensivel": None,
                     "codigo": None, "escondidos": [], "linguagem": self.memoria.linguagem_escolhida,
                     "detectada": None, "motivo": "", "linha": None, "troca_linguagem": None,
                     "normalizado": "", "pede_codigo": False, "termos": {}}
        if percepcao["eh_codigo"]:
            codigo, escondidos = mascarar_codigo(texto)
            percepcao["codigo"], percepcao["escondidos"] = codigo, escondidos
            # a pessoa escolhe a linguagem; a detecção só serve para avisar quando o código parece outra
            detectada, motivo, ambigua = detectar(codigo)
            # código que vale igual nas duas (como `x = 5`) não tem "cara" de nenhuma
            percepcao.update(detectada=None if ambigua else detectada, motivo=motivo)
            return percepcao
        percepcao["dado_sensivel"] = dado_sensivel_no_texto(texto)
        pede_linha = PEDE_LINHA.search(texto)
        percepcao["linha"] = int(pede_linha.group(1)) if pede_linha else None
        troca = TROCA_LINGUAGEM.match(texto)
        percepcao["troca_linguagem"] = NOMES_LINGUAGEM[troca.group(1).lower()] if troca else None
        percepcao["normalizado"] = self.normalizar(texto)
        percepcao["pede_codigo"] = bool(PEDIDO_CODIGO.search(percepcao["normalizado"]))
        percepcao["termos"] = self.termos_citados(percepcao["normalizado"])
        return percepcao

    def termos_citados(self, normalizado):
        """Quais conceitos têm um termo técnico escrito na pergunta (como `for` ou `def`)."""
        texto = f" {normalizado} "
        return {chave: termo for chave, conceito in self.conceitos.items() for termo in conceito.get("termos", [])
                if f" {termo} " in texto}

    # ---------- camada 2: cognitiva ----------
    def entender(self, percepcao):
        if percepcao["eh_codigo"]:
            detectada = percepcao["detectada"]
            if detectada is not None and detectada not in ANALISADORES:
                return ("codigo", 1.0, None)  # Java, C, HTML...: não adianta ler
            return ("codigo", 1.0, ANALISADORES[percepcao["linguagem"]](percepcao["codigo"]))
        if percepcao["dado_sensivel"] or not percepcao["normalizado"]:
            return (None, 0.0, None)
        indice, confianca = self.tfidf.mais_parecida(percepcao["normalizado"])
        rotulo = self.rotulos[indice]
        # um termo técnico de um conceito só vale mais que a frase parecida
        # ("não entendi o for" é sobre o for, não um agradecimento)
        if len(percepcao["termos"]) == 1:
            chave = next(iter(percepcao["termos"]))
            if rotulo != "conceito:" + chave:
                return ("conceito:" + chave, 1.0, None)
        return (rotulo, confianca, None)

    # ---------- camada 3: decisória ----------
    def decidir(self, percepcao, rotulo, confianca, resultado):
        if percepcao["dado_sensivel"]:
            return "bloquear_dado"
        if percepcao["eh_codigo"]:
            if resultado is None:
                return "linguagem_nao_suportada"
            if resultado.erro:
                # não deu para ler na linguagem escolhida: se a outra consegue, a escolha é que está errada
                outra = OUTRA[percepcao["linguagem"]]
                return "linguagem_diferente" if CONSEGUE_LER[outra](percepcao["codigo"]) else "erro_de_leitura"
            return "explicar_codigo"
        if percepcao["troca_linguagem"]:
            return "trocar_linguagem"
        if percepcao["linha"] is not None:
            return "explicar_linha" if self.memoria.resultado else "sem_codigo"
        if percepcao["pede_codigo"]:
            return "recusar_codigo"
        if confianca < LIMIAR_BAIXO:
            return "nao_entendi"
        if rotulo == "pedido_codigo":
            # recusar é uma decisão que precisa de certeza, para não recusar uma pergunta normal
            return "recusar_codigo" if confianca >= LIMIAR_ALTO else "nao_entendi"
        if rotulo in ("resumo", "detalhado"):
            if not self.memoria.resultado:
                return "sem_codigo"
            return "resumir" if rotulo == "resumo" else "explicar_de_novo"
        if rotulo.startswith("conceito:"):
            return "explicar_conceito" if confianca >= LIMIAR_ALTO else "explicar_conceito_com_duvida"
        return "responder"

    # ---------- camada 4: executiva ----------
    def executar(self, acao, percepcao, rotulo, resultado):
        resposta = {"tipo": "texto", "texto": "", "resultado": None, "avisos": []}
        if acao == "bloquear_dado":
            resposta["texto"] = self.msgs["dado_sensivel"].format(tipo=percepcao["dado_sensivel"])
        elif acao == "linguagem_nao_suportada":
            resposta["texto"] = self.msgs["linguagem_nao_suportada"].format(linguagem=percepcao["detectada"])
        elif acao == "erro_de_leitura":
            resposta["texto"] = resultado.erro
        elif acao == "linguagem_diferente":
            # o código fica esperando: quando a pessoa trocar a linguagem, ele é explicado
            self.memoria.codigo_pendente = percepcao["codigo"]
            escolhida, outra = percepcao["linguagem"], OUTRA[percepcao["linguagem"]]
            resposta["texto"] = self.msgs["linguagem_diferente"].format(
                escolhida=escolhida, outra=outra, outra_minuscula=outra.lower())
        elif acao == "explicar_codigo":
            self.memoria.codigo_pendente = None
            self.memoria.guardar_codigo(percepcao["codigo"], percepcao["linguagem"], resultado)
            resposta = self.resposta_de_codigo(resultado, percepcao)
        elif acao == "trocar_linguagem":
            resposta = self.trocar_linguagem(percepcao["troca_linguagem"])
        elif acao == "explicar_linha":
            resposta["texto"] = self.explicar_linha(percepcao["linha"])
        elif acao == "sem_codigo":
            resposta["texto"] = self.msgs["sem_codigo"]
        elif acao == "resumir":
            resposta["texto"] = self.resumo(self.memoria.resultado)
        elif acao == "explicar_de_novo":
            resposta = self.resposta_de_codigo(self.memoria.resultado, {"codigo": self.memoria.codigo})
        elif acao in ("explicar_conceito", "explicar_conceito_com_duvida"):
            resposta["texto"] = self.explicar_conceito(rotulo.split(":", 1)[1], acao.endswith("duvida"))
        elif acao == "recusar_codigo":
            resposta["texto"] = self.intencoes["pedido_codigo"]["resposta"]
        elif acao == "nao_entendi":
            resposta["texto"] = self.msgs["nao_entendi"]
        else:  # responder
            resposta["texto"] = self.intencoes[rotulo]["resposta"]
        return resposta

    def resposta_de_codigo(self, resultado, percepcao):
        avisos = []
        if percepcao.get("escondidos"):
            avisos.append(self.msgs["mascarado"].format(itens=" e ".join(percepcao["escondidos"])))
        detectada, escolhida = percepcao.get("detectada"), resultado.linguagem
        if detectada in ANALISADORES and detectada != escolhida:
            avisos.append(self.msgs["parece_outra"].format(outra=detectada, escolhida=escolhida))
        linhas = resultado.linhas
        total = len((percepcao.get("codigo") or "").splitlines())
        if total > LIMITE_LINHAS:
            linhas = [l for l in linhas if l.numero <= LIMITE_LINHAS]
            avisos.append(self.msgs["comprido"].format(total=total, limite=LIMITE_LINHAS))
        return {"tipo": "explicacao", "texto": resultado.resumo(), "resultado": resultado, "linhas": linhas,
                "avisos": avisos}

    def trocar_linguagem(self, linguagem, reexplicar=True):
        """Troca a linguagem escolhida e explica o código que estava esperando (ou, se a pessoa
        escreveu "é javascript", o último código de novo, agora na outra linguagem)."""
        self.memoria.linguagem_escolhida = linguagem
        codigo = self.memoria.codigo_pendente or (self.memoria.codigo if reexplicar else None)
        self.memoria.codigo_pendente = None
        aviso = self.msgs["trocar_linguagem"].format(linguagem=linguagem)
        if not codigo:
            return {"tipo": "texto", "texto": aviso, "resultado": None, "avisos": []}
        resultado = ANALISADORES[linguagem](codigo)
        if resultado.erro:
            return {"tipo": "texto", "texto": aviso + f" O último código que você colou não parece {linguagem}, "
                    "então não expliquei ele de novo. Pode colar um código novo.", "resultado": None, "avisos": []}
        self.memoria.guardar_codigo(codigo, linguagem, resultado)
        resposta = self.resposta_de_codigo(resultado, {"codigo": codigo})
        resposta["avisos"].insert(0, aviso)
        return resposta

    def escolher_linguagem(self, linguagem, explicar_pendente=True):
        """Chamado pelo seletor da tela. Só responde se tinha um código esperando a troca.

        Os botões de exemplo usam explicar_pendente=False: eles trocam a linguagem e já mandam
        o próprio código, então um código que estava esperando é descartado.
        """
        if linguagem not in ANALISADORES:
            raise ValueError(f"linguagem desconhecida: {linguagem}")
        if not explicar_pendente:
            self.memoria.codigo_pendente = None
        if not self.memoria.codigo_pendente:
            self.memoria.linguagem_escolhida = linguagem
            return None
        resposta = self.trocar_linguagem(linguagem, reexplicar=False)
        resultado = resposta.get("resultado")
        explicacao = (f"Li como {linguagem} porque você trocou a linguagem no seletor. "
                      f"{self.contagem(resultado)}" if resultado else "")
        resposta.update(acao="trocar_linguagem", rotulo=None, confianca=1.0, linguagem=linguagem,
                        linguagem_escolhida=linguagem, explicacao=explicacao, codigo_exibido=None)
        self.memoria.registrar("decifrabot", resposta["texto"][:200])
        return resposta

    def contagem(self, resultado):
        total = len(resultado.linhas)
        certas = total - resultado.desconhecidas
        texto = f"Reconheci {certas} de {total} instruções"
        return texto + (f"; nas outras {resultado.desconhecidas}, avisei que não sei." if resultado.desconhecidas else ".")

    def explicar_linha(self, numero):
        linhas_fonte = self.memoria.codigo.splitlines()
        if not 1 <= numero <= len(linhas_fonte):
            total = len(linhas_fonte)
            return f"O código tem {total} {'linha' if total == 1 else 'linhas'}, então não existe a linha {numero}."
        texto_linha = linhas_fonte[numero - 1].strip()
        explicacoes = [l.texto for l in self.memoria.resultado.linhas if l.numero == numero]
        # linha com crase (template string) precisa de crase dupla para não quebrar o Markdown
        citacao = f"`` {texto_linha} ``" if "`" in texto_linha else f"`{texto_linha}`"
        mostra = f"**Linha {numero}:** {citacao}\n\n" if texto_linha else ""
        if explicacoes:
            return mostra + "\n\n".join(e[0].upper() + e[1:] for e in explicacoes)
        if not texto_linha:
            return f"A linha {numero} está em branco. Ela só serve para separar as partes do código e facilitar a leitura."
        if texto_linha.startswith(("#", "//")):
            return mostra + "É um comentário: o programa ignora essa linha. Ela está ali só para quem lê o código."
        if re.fullmatch(r"[\s})\];,]+", texto_linha):
            return mostra + "Essa linha só fecha um bloco (ou uma lista) que foi aberto antes."
        anteriores = [l for l in self.memoria.resultado.linhas if l.numero < numero]
        if anteriores:
            inicio = anteriores[-1]
            return mostra + (f"Essa linha é a continuação da instrução que começa na linha {inicio.numero}, "
                             f"que {inicio.texto}")
        return mostra + "Não tenho uma explicação separada para essa linha."

    def resumo(self, resultado):
        partes = [resultado.resumo()]
        if resultado.alertas:
            partes.append(f"Tem {len(resultado.alertas)} {'ponto' if len(resultado.alertas) == 1 else 'pontos'} de atenção, que aparecem na explicação completa.")
        if resultado.conceitos:
            titulos = [self.conceitos[c]["titulo"] for c in resultado.conceitos if c in self.conceitos]
            partes.append("Conceitos usados: " + ", ".join(titulos) + ".")
        partes.append('Se quiser ver tudo de novo, linha por linha, peça "explica linha por linha".')
        return "\n\n".join(partes)

    def explicar_conceito(self, chave, com_duvida):
        conceito = self.conceitos[chave]
        linguagem = self.memoria.linguagem_escolhida
        texto = conceito["explicacao"] + f"\n\nExemplo em {linguagem}:\n```{linguagem.lower()}\n{conceito['exemplos'][linguagem]}\n```"
        if com_duvida:
            texto = self.msgs["com_duvida"].format(tema=conceito["titulo"]) + texto
        return texto

    def explicar_decisao(self, acao, percepcao, rotulo, confianca, resultado):
        """Explica em linguagem simples por que o DecifraBot respondeu daquele jeito (interpretabilidade)."""
        conf = f"{confianca:.2f}".replace(".", ",")
        if acao == "explicar_codigo":
            return f"Li como {resultado.linguagem} porque é a linguagem escolhida no seletor. {self.contagem(resultado)}"
        if acao == "trocar_linguagem":
            if resultado:
                return f"Li como {resultado.linguagem} porque você pediu para trocar a linguagem. {self.contagem(resultado)}"
            return "Você pediu para trocar a linguagem."
        if acao == "linguagem_diferente":
            escolhida = percepcao["linguagem"]
            return (f"Tentei ler como {escolhida}, que é a linguagem escolhida, e não consegui. "
                    f"O leitor de {OUTRA[escolhida]} conseguiu, então o código deve ser {OUTRA[escolhida]}.")
        if acao == "linguagem_nao_suportada":
            return f"Não expliquei porque {percepcao['motivo']}."
        if acao == "erro_de_leitura":
            return f"Tentei ler como {percepcao['linguagem']}, que é a linguagem escolhida, e o código tem algo que eu não consegui ler."
        if acao == "bloquear_dado":
            return "A mensagem parecia ter um dado sensível, então foi descartada antes de qualquer análise."
        if acao == "nao_entendi":
            return f"A pergunta mais parecida que conheço teve confiança {conf}, abaixo do mínimo. Preferi admitir que não entendi."
        if acao == "recusar_codigo":
            if percepcao.get("pede_codigo"):
                return "A mensagem tem um verbo de pedido (como \"faz\" ou \"corrige\") junto com \"código\" ou \"pra mim\". Escrever ou corrigir código fica fora do meu papel."
            return f"Entendi como um pedido para escrever ou corrigir código (confiança {conf}). Isso fica fora do meu papel."
        if acao.startswith("explicar_conceito"):
            chave = rotulo.split(':', 1)[1]
            titulo = self.conceitos[chave]["titulo"]
            if chave in percepcao.get("termos", {}) and len(percepcao["termos"]) == 1:
                return f"Achei o termo técnico \"{percepcao['termos'][chave]}\" na pergunta, que é de {titulo}."
            return f"Entendi como uma pergunta sobre {titulo} (confiança {conf})."
        if acao in ("explicar_linha", "resumir", "explicar_de_novo", "sem_codigo"):
            return "Usei o último código que você colou, que fica guardado só durante esta conversa."
        return f"Entendi como '{rotulo}' (confiança {conf})."

    # ---------- fluxo completo ----------
    def responder(self, texto):
        percepcao = self.perceber(texto)
        rotulo, confianca, resultado = self.entender(percepcao)
        acao = self.decidir(percepcao, rotulo, confianca, resultado)
        resposta = self.executar(acao, percepcao, rotulo, resultado)
        if acao == "trocar_linguagem":
            resultado = resposta.get("resultado")
        resposta.update(acao=acao, rotulo=rotulo, confianca=round(confianca, 2), linguagem=percepcao["linguagem"],
                        linguagem_escolhida=self.memoria.linguagem_escolhida,
                        explicacao=self.explicar_decisao(acao, percepcao, rotulo, confianca, resultado),
                        codigo_exibido=percepcao["codigo"])
        # memória curta: código entra só como aviso, e mensagem com dado sensível não entra
        if percepcao["eh_codigo"]:
            self.memoria.registrar("usuario", f"[código {percepcao['linguagem'] or ''} com {len(texto.splitlines())} linhas]")
        elif acao != "bloquear_dado":
            self.memoria.registrar("usuario", texto)
        self.memoria.registrar("decifrabot", resposta["texto"][:200])
        return resposta
