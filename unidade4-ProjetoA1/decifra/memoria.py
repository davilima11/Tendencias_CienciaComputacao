"""Memória do DecifraBot.

- Curta: as últimas mensagens da conversa. Código não entra aqui, só um aviso de que foi colado.
- Média: a linguagem escolhida no seletor, o último código (já com senhas escondidas) e a
  explicação dele, para responder "explica a linha 4" ou "resume". Também guarda um código
  que ficou esperando a pessoa trocar a linguagem.
- Longa: não existe de propósito. O código da pessoa não fica guardado depois da conversa.
"""
from collections import deque


class Memoria:
    TAMANHO_CURTA = 6

    LINGUAGEM_PADRAO = "Python"

    def __init__(self):
        self.curta = deque(maxlen=self.TAMANHO_CURTA)
        self.linguagem_escolhida = self.LINGUAGEM_PADRAO
        self.limpar_media()

    def registrar(self, autor, texto):
        self.curta.append((autor, texto))

    def guardar_codigo(self, codigo, linguagem, resultado):
        self.codigo = codigo
        self.linguagem = linguagem
        self.resultado = resultado

    def limpar_media(self):
        """Apaga o código da conversa. A linguagem escolhida continua, porque é o que está no seletor."""
        self.codigo = None
        self.linguagem = None
        self.resultado = None
        self.codigo_pendente = None

    def limpar(self):
        self.curta.clear()
        self.limpar_media()
