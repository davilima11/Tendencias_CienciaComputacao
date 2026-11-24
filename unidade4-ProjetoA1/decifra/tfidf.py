"""TF-IDF com pedaços de 2 a 4 letras, escrito à mão (mesma fórmula do scikit-learn).

Serve para entender perguntas como "o que é um for?" mesmo com erro de digitação.
Foi escrito sem bibliotecas para o projeto rodar em qualquer lugar.
"""
import math
import re
from collections import Counter


def pedacos(texto):
    resultado = []
    for palavra in re.sub(r"\s\s+", " ", texto).split():
        w = f" {palavra} "
        for n in range(2, 5):
            inicio = 0
            resultado.append(w[inicio:inicio + n])
            while inicio + n < len(w):
                inicio += 1
                resultado.append(w[inicio:inicio + n])
            if inicio == 0:  # palavra curta conta uma vez só
                break
    return resultado


class TfIdf:
    def __init__(self, frases):
        contagens = [Counter(pedacos(f)) for f in frases]
        df = Counter(termo for c in contagens for termo in c)
        n = len(frases)
        self.idf = {termo: math.log((1 + n) / (1 + freq)) + 1 for termo, freq in df.items()}
        self.vetores = [self._pesar(c) for c in contagens]

    def _pesar(self, contagem):
        vetor = {t: tf * self.idf[t] for t, tf in contagem.items() if t in self.idf}
        norma = math.sqrt(sum(p * p for p in vetor.values()))
        return {t: p / norma for t, p in vetor.items()} if norma else {}

    def mais_parecida(self, frase):
        """Devolve (índice da frase mais parecida, similaridade de 0 a 1)."""
        consulta = self._pesar(Counter(pedacos(frase)))
        melhor, maior = 0, 0.0
        for i, vetor in enumerate(self.vetores):
            similaridade = sum(p * vetor.get(t, 0.0) for t, p in consulta.items())
            if similaridade > maior:
                melhor, maior = i, similaridade
        return melhor, maior
