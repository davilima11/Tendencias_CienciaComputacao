
# Aula 02 - Engenharia de Prompt

## 1. Identificação

- **Turma:** Tendências em Ciência da Computação
- **Grupo:** Individual
- **Data:** 20/08/2026
- **Nome:** Davi Vieira Lima

## 2. Problema escolhido

Escolhi um problema para organizar os estudos de Python. Sem um roteiro, é fácil estudar os assuntos fora de ordem ou ficar apenas na teoria.

O plano será feito para estudantes de TI que conhecem o básico de lógica, mas ainda estão começando em Python. 

**Problema:** como montar um plano simples e organizado, que misture teoria e prática e caiba no tempo disponível?

## 3. Objetivo

Usar uma IA para criar um plano de estudo de Python.

## 4. Prompt inicial

```text
Crie um plano de estudos para aprender Python.
```

## 5. Resultado inicial

> 1. **Semana 1 - Fundamentos:** sintaxe, variáveis, tipos de dados e operadores.
> 2. **Semana 2 - Estruturas de controle:** condições e laços de repetição.
> 3. **Semana 3 - Estruturas de dados e funções:** listas, dicionários, tuplas e funções.
> 4. **Semana 4 - Conteúdos complementares:** módulos, arquivos e tratamento de erros. No final, faça um projeto simples.
>
> Pratique durante os estudos e consulte a documentação oficial quando tiver dúvidas.

## 6. Análise crítica

| Questão | Resposta |
|---|---|
| A resposta atendeu ao objetivo? | Em parte. Ela criou uma sequência de estudos, mas ficou muito geral. |
| A resposta foi clara? | Sim. A divisão por semanas facilitou a leitura. |
| O que ficou faltando? | Faltaram o tempo de cada atividade, exercícios mais específicos e uma explicação do projeto final. |
| O que poderia melhorar? | Separar teoria, prática e revisão, além de explicar o que deve ser aprendido em cada semana. |
| O que precisa ser verificado? | A ordem dos conteúdos e se a quantidade de assuntos é adequada para iniciantes. |
| A IA fez alguma suposição? | Sim. Ela escolheu quatro semanas e recomendou prática sem saber quanto tempo o estudante tinha disponível. |

O ponto positivo foi a organização básica por semanas. Porém, como o prompt era muito aberto, a resposta não considerou o público, o tempo disponível e o formato que eu precisava.

## 7. Prompt refinado

```text
PAPEL:
Você é um professor de programação que ensina Python para iniciantes.

CONTEXTO:
Os estudantes estão começando o curso de Computação, possuem conhecimentos básicos de lógica e ainda não estudaram Python de forma organizada. Eles têm seis horas por semana durante quatro semanas.

OBJETIVO:
Criar um plano introdutório de Python com dificuldade progressiva.

TAREFA:
Monte um plano de estudos para quatro semanas. Em cada semana, informe o conteúdo, uma atividade prática, o tempo necessário e o resultado esperado. Na última semana, inclua um projeto final simples.

RESTRIÇÕES:
- usar Python 3;
- considerar seis horas por semana;
- manter o conteúdo no nível iniciante;
- misturar teoria, prática e revisão;
- não usar bibliotecas externas;
- evitar assuntos avançados.

FORMATO:
Apresente uma tabela com as colunas:
Semana | Conteúdo | Atividade prática | Tempo | Resultado esperado

Depois da tabela, escreva três recomendações curtas.

CRITÉRIOS DE QUALIDADE:
O plano deve ser claro, realista, progressivo e adequado para iniciantes.
```

## 8. Resultado refinado

| Semana | Conteúdo | Atividade prática | Tempo | Resultado esperado |
|---|---|---|---|---|
| **1 - Primeiros passos** | Instalação, `print()`, `input()`, variáveis, tipos e operadores. | Fazer um programa que receba duas notas e calcule a média. | 2 h de teoria, 3 h de prática e 1 h de revisão. | Criar programas simples, receber dados e fazer cálculos. |
| **2 - Decisões e repetições** | `if`, `elif`, `else`, operadores lógicos, `for` e `while`. | Criar um verificador de aprovação e uma tabuada. | 2 h de teoria, 3 h de prática e 1 h de revisão. | Usar condições e repetições em um programa. |
| **3 - Listas e funções** | Listas, dicionários e funções com parâmetros e retorno. | Guardar notas em uma lista e criar uma função para calcular a média. | 2 h de teoria, 3 h de prática e 1 h de revisão. | Organizar dados e dividir o código em funções. |
| **4 - Projeto final** | Módulos, arquivos de texto, `try`, `except` e revisão. | Criar um gerenciador de tarefas que permita adicionar, listar e concluir tarefas. | 1 h e 30 min de teoria, 3 h e 30 min de projeto e 1 h de testes. | Juntar os principais conteúdos em um programa funcional. |

### Recomendações

1. Refazer pelo menos um exercício por semana sem olhar a solução.
2. Anotar os erros encontrados e como foram resolvidos.
3. Testar os programas com entradas diferentes.

## 9. Técnicas utilizadas

- [x] **Role Prompting:** defini o papel de professor de programação.
- [x] **Contexto:** informei o nível dos estudantes e o tempo disponível.
- [x] **Restrições:** limitei a duração, a dificuldade e os assuntos.
- [x] **Formato de saída:** pedi uma tabela com colunas definidas.
- [x] **Prompt em etapas:** dividi o prompt em partes.
- [x] **Refinamento iterativo:** melhorei o prompt depois de analisar a primeira resposta.


## 10. Comparação

| Critério | Prompt inicial | Prompt refinado |
|---|---|---|
| Clareza | Era simples, mas muito aberto. | Explicou exatamente o que deveria ser feito. |
| Contexto | Não informou público nem tempo. | Informou o nível dos estudantes e as seis horas semanais. |
| Relevância | Deu apenas uma orientação geral. | Criou um plano voltado para a situação apresentada. |
| Organização | Separou os assuntos por semanas. | Organizou conteúdo, prática, tempo e resultado. |
| Precisão | Não definiu limites. | Respeitou as quatro semanas e o nível iniciante. |
| Utilidade | Serviu como ponto de partida. | Pode ser usado diretamente como roteiro de estudos. |

O prompt refinado teve o melhor resultado porque deixou claro o público, o objetivo, os limites e o formato da resposta. Dessa forma, a IA precisou fazer menos suposições.

### Teste de robustez

Alterei uma informação do para ver o impacto na resposta.

**Versão A:**

```text
Os estudantes possuem conhecimentos básicos de lógica de programação.
```

**Versão B:**

```text
Os estudantes nunca estudaram programação e não conhecem lógica de programação.
```

Na versão B, o plano teria que começar com conceitos como algoritmo, entrada, processamento e saída. Alguns assuntos das últimas semanas também precisariam ser reduzidos ou adiados.

A resposta mudou porque o conhecimento anterior define o ponto de partida. A versão A é melhor para quem já conhece lógica, enquanto a versão B seria melhor para quem está começando do zero.

## 11. Validação

Primeiro, conferi se cada semana tinha seis horas. Depois, verifiquei se os conteúdos começavam pelo básico e aumentavam de dificuldade aos poucos.

O plano ficou coerente, mas pode precisar de ajustes dependendo do ritmo e das dificuldades de cada estudante.

## 12. Ética e responsabilidade

A IA pode sugerir conteúdos em uma ordem ruim, colocar assuntos demais ou apresentar informações incorretas. Além disso, uma resposta bem organizada pode parecer correta mesmo quando possui problemas.

Por isso, eu não devo aceitar o resultado sem conferir.

## 13. Take Away

### O que aprendi sobre Engenharia de Prompt?

Aprendi que um prompt mais bem estruturado ajuda a IA a entender o que eu realmente preciso. O primeiro prompt gerou uma resposta genérica. Depois que eu utilizei algo mais etruturado o resultado ficou mais útil e organizado.


## 14. Link

[Atividade Prática - Aula 2 - Engenharia de Prompt](https://github.com/davilima11/Tendencias_CienciaComputacao/blob/main/unidade1/aula2/AtividadePratica_aula2_engenharia_de_prompt.md)
