# DecifraBot

Hoje muita gente pede para uma IA gerar um código e usa o resultado sem saber o que ele faz. O DecifraBot vai no caminho contrário: a pessoa cola um código e ele explica, em português simples, o que cada linha faz. Também serve para quem achou um código interessante por aí e quer entender como ele funciona.

Projeto final da Unidade IV (Agentes e Ética) da disciplina Tendências em Ciência da Computação.

| | |
|---|---|
| **Aluno** | Davi Vieira Lima |
| **RGM** | 39538061 |
| **Professora** | Kadidja Valéria |
| **Instituição** | UDF Centro Universitário |
| **Ferramenta de IA usada como apoio** | Claude |

**Versão online:** https://davilima11.github.io/Tendencias_CienciaComputacao/unidade4-ProjetoA1/ (dá para usar e ler a documentação direto no navegador, sem instalar nada)

![Tela do DecifraBot](documentacao/imagens/tela.png)

## O que ele faz

Explica código **Python** e **JavaScript** linha por linha. A pessoa escolhe a linguagem num seletor acima do campo de texto (começa em Python). O bot avisa quando o código faz algo que merece cuidado (apagar arquivos, mandar dados pela internet, montar SQL juntando texto, guardar senha no código) e responde perguntas sobre os conceitos que aparecem, como "o que é um for?". Depois de explicar, dá para pedir "explica a linha 4" ou "resume".

E o que ele **não** faz: não escreve nem corrige código, não executa o código e não guarda nada depois que a conversa acaba. Senhas e chaves que estiverem no código são escondidas antes de qualquer análise. Quando encontra algo que não sabe explicar, ele diz isso em vez de inventar.

## Como rodar

Precisa de Python 3.10 ou mais novo. Todos os comandos são rodados de dentro desta pasta:

```bash
cd unidade4-ProjetoA1
```

```bash
pip install -r requirements.txt
streamlit run app.py
```

Para abrir a versão web no computador (a mesma do site):

```bash
python -m http.server
# depois abra http://localhost:8000
```

Para rodar os testes:

```bash
python -m pytest
python -m testes.calibrar_limiar   # mostra como escolhi o limiar de confiança
```

## Onde está cada entrega

| Entrega da Unidade IV | Onde está |
|---|---|
| Criação de agente de IA | [documentacao/2-arquitetura-do-agente.md](documentacao/2-arquitetura-do-agente.md) e a pasta `decifra/` |
| Chatbot com a especificação | [documentacao/1-especificacao.md](documentacao/1-especificacao.md) e `app.py` |
| Viés algorítmico e responsabilidade social | [documentacao/3-etica-e-vies.md](documentacao/3-etica-e-vies.md) |
| Projeto final (solução aplicada) | este repositório, com os testes em [documentacao/4-testes.md](documentacao/4-testes.md) |

A documentação segue o fluxo de trabalho de chatbots do SERPRO, adaptado para o tamanho de um projeto de disciplina.

## Estrutura

```
app.py                        interface em Streamlit
index.html                    versão web (o mesmo código Python rodando no navegador)
decifra/
  agente.py                   as 4 camadas do agente (perceber, entender, decidir, executar)
  memoria.py                  memória curta e média
  linguagem.py                percebe quando o código é de outra linguagem, para avisar
  privacidade.py              esconde senhas e chaves antes da análise
  tfidf.py                    TF-IDF feito à mão, para entender as perguntas
  textos.py                   frases de explicação compartilhadas entre as linguagens
  ponte.py                    liga o código Python à versão web
  analisadores/python.py      lê Python com o módulo ast
  analisadores/javascript.py  lê JavaScript com a biblioteca esprima
dados/
  conhecimento.json           conceitos, perguntas e respostas
  exemplos.json               códigos de exemplo da tela
pagina/                       estilo e script da versão web
  bibliotecas/                Pyodide, esprima e marked (cópias, para o site não depender de outro servidor)
testes/                       testes com pytest e script de calibração
documentacao/                 especificação, arquitetura, ética e testes
  imagens/                    print da tela
```

## Tecnologias

Python, Streamlit, o módulo `ast` do próprio Python, a biblioteca `esprima` (para ler JavaScript) e pytest. A versão online usa o Pyodide, que roda Python dentro do navegador. Não usa API de IA nenhuma: o código da pessoa não sai do computador dela. O motivo dessa escolha está na arquitetura.

## Mais linguagens

Cada linguagem tem um analisador próprio, mas as frases de explicação ficam num arquivo só (`decifra/textos.py`) e são usadas pelas duas. Para ensinar Java ao DecifraBot, por exemplo, seria preciso um analisador novo que leia Java (a biblioteca `javalang` faz isso); o texto das explicações já está quase todo pronto.

## Referências

**Material da disciplina**

- VALÉRIA, Kadidja. *Guia de Estudos A1: Criação de Agentes de IA e Ética Aplicada*. Tendências em Ciência da Computação. UDF Centro Universitário, 2026.

**Desenvolvimento de chatbots e legislação**

- SERPRO. *Desenvolvendo Chatbots: fluxo de trabalho*. Disponível em: https://serprobots.estaleiro.serpro.gov.br/docs/dev/
- BRASIL. Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais (LGPD). Disponível em: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm

**Tutoriais e guias**

- PYTHON SOFTWARE FOUNDATION. *ast — Árvores de Sintaxe Abstrata*. Documentação oficial do Python em português. Disponível em: https://docs.python.org/pt-br/3.9/library/ast.html
- FREECODECAMP. *Como processar dados textuais usando o TF-IDF em Python*. Disponível em: https://www.freecodecamp.org/portuguese/news/como-processar-dados-textuais-usando-o-tf-idf-em-python/
- STREAMLIT. *Build a basic LLM chat app* (tutorial oficial para montar um chat). Disponível em: https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps
- PYODIDE. *Getting started* (guia de início). Disponível em: https://pyodide.readthedocs.io/en/stable/usage/quickstart.html
- TESTDRIVEN.IO. *Running Python in the Browser with WebAssembly*. Disponível em: https://testdriven.io/blog/python-webassembly/

**Ferramentas e bibliotecas usadas**

- esprima-python (leitura de código JavaScript). Disponível em: https://github.com/Kronuz/esprima-python
- Pyodide (Python no navegador, usado na versão web). Disponível em: https://pyodide.org
- Streamlit (interface da versão em Python). Disponível em: https://streamlit.io
- marked (exibição da documentação no site). Disponível em: https://marked.js.org
- scikit-learn (usado só no teste que confere o TF-IDF feito à mão). Disponível em: https://scikit-learn.org
- pytest (testes automatizados). Disponível em: https://pytest.org

**Ferramenta de IA usada como apoio:** Claude (Anthropic).
