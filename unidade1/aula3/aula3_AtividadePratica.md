# Atividade - Refinamento de Prompts

## Identificação
- Nome: Davi Vieira Lima
- Turma: Tendência em Ciência da Computação
- Data: 03
- Ferramenta de IA utilizada: Chatgpt
---

## Problema escolhido

### Contexto

Para pessoas que iniciaram algum curso ou começaram a faculdade de TI, ou seja, inciantes em progamação ou que querem aprender diferentes linguagens de progamação.

### Problema
Explicar um conceito de programação para um iniciante; Nesse caso o que são loops (for) e (while), como funcionam e qual a diferença entre eles. Nesse prompt pode escolher outros conceitos é somente substituir o conceito que queira para o lugar de for e while.

### Objetivo
Usar a IA pra me explicar esse conceito de um jeito simples, como se fosse pra alguém que tá aprendendo programação agora. No caso, esse prompt é para python mas pode escolher outras linguagens de progamação.

---

## Prompt 1 - Versão inicial

### Prompt
```
Explique loops em programação.
```

### Resultado

Loops são estruturas de controle de fluxo que permitem executar um bloco de código repetidamente enquanto uma condição é verdadeira ou para cada item em uma sequência. Os dois tipos mais comuns são o loop `for` e o loop `while`. O loop `for` é utilizado quando se sabe previamente o número de iterações, iterando sobre sequências como listas, tuplas, strings ou ranges. O loop `while` é utilizado quando a repetição depende de uma condição dinâmica que pode mudar durante a execução. Loops podem ser controlados com instruções como `break` (interrompe o loop), `continue` (pula para a próxima iteração) e `else` (executado quando o loop termina normalmente). Loops aninhados permitem iterar sobre estruturas multidimensionais. É importante evitar loops infinitos, que ocorrem quando a condição de parada nunca é satisfeita. Em termos de complexidade, loops simples têm complexidade O(n), enquanto loops aninhados podem ter O(n²) ou superior. Linguagens modernas oferecem alternativas como list comprehensions, funções map/filter e iteradores para substituir loops tradicionais em determinados cenários.

### Análise
- **O que funcionou?** A IA explicou o que são loops e citou os dois tipos principais.
- **O que faltou?** Não deu nenhum exemplo de código. Ficou tudo nem um bloco de texto difícil de ler.
- **O que ficou genérico?** Falou de complexidade O(n), loops aninhados, list comprehensions e coisas que um iniciante não precisa saber agora.
- **O que poderia ser melhor?** Podia ter exemplos práticos, uma linguagem mais simples e uma comparação entre `for` e `while`.

---

## Prompt 2 - Primeiro refinamento

### Alterações realizadas
- **Papel:** Pedi pra IA atuar como um monitor que ajuda iniciantes.
- **Contexto:** Disse que sou aluno de primeiro semestre.
- **Objetivo:** Entender for e while de forma simples.
- **Público:** Estudante iniciante que só sabe variáveis e if/else.
- **Formato:** Pedi subtítulos, exemplos de código em Python com comentários.
- **Restrições:** Linguagem simples e sem termos avançados.
- **Critérios:** Não adicionei ainda.

### Prompt
```
Atue como um monitor de programação que ajuda iniciantes.

Explique o que são loops (for e while) em programação para
um estudante de primeiro semestre que já sabe usar variáveis
e if/else, mas nunca viu loops.

Apresente:
1. O que é um loop e pra que serve;
2. Como funciona o for, com um exemplo em Python;
3. Como funciona o while, com um exemplo em Python;
4. A diferença entre os dois de forma simples.

Use linguagem simples. Se usar algum termo técnico, explique.
```

### Resultado

**O que é um loop?**

Loop é uma estrutura que faz o computador repetir um pedaço de código várias vezes. Em vez de você escrever a mesma coisa 10 vezes, o loop faz isso automaticamente. É tipo falar pro computador: "repete isso aqui até eu mandar parar".

**Como funciona o for**

O `for` é usado quando você já sabe quantas vezes quer repetir algo. Ele percorre uma sequência (uma lista de coisas, um intervalo de números, etc.) e faz algo com cada item.

```python
# Mostrando os números de 1 a 5
for numero in range(1, 6):
    print(numero)

# Saída:
# 1
# 2
# 3
# 4
# 5
```

O `range(1, 6)` cria uma sequência de 1 até 5 (o 6 não entra). O `for` pega cada número dessa sequência e coloca na variável `numero`, e aí o `print` mostra na tela.

**Como funciona o while**

O `while` é usado quando você não sabe exatamente quantas vezes vai repetir. Ele fica repetindo enquanto uma condição for verdadeira.

```python
# Contando de 1 até 5 com while
contador = 1

while contador <= 5:
    print(contador)
    contador = contador + 1

# Saída:
# 1
# 2
# 3
# 4
# 5
```

Aqui o `while` verifica se `contador` é menor ou igual a 5. Se for, executa o bloco. No final de cada repetição, o contador aumenta em 1. Quando chega em 6, a condição fica falsa e o loop para.

**Qual a diferença entre os dois?**

- **for:** Você usa quando sabe quantas vezes quer repetir. Exemplo: percorrer uma lista de nomes, contar de 1 a 100.
- **while:** Você usa quando não sabe quantas vezes vai repetir, porque depende de algo que pode mudar. Exemplo: pedir a senha pro usuário até ele acertar.

Se dá pra usar os dois na maioria dos casos, mas o `for` costuma ser mais prático quando você já tem uma sequência definida.

---

## Comparação entre Prompt 1 e Prompt 2

| Critério | Prompt 1 | Prompt 2 |
|---|:---:|:---:|
| Clareza | 2 | 4 |
| Precisão | 3 | 4 |
| Relevância | 2 | 5 |
| Organização | 1 | 5 |
| Adequação ao público | 1 | 4 |
| Atendimento ao objetivo | 2 | 4 |

### O que melhorou?
A resposta do Prompt 2 ficou muito mais fácil de entender. Ter exemplos de código com comentários faz diferença para a compreenção. A comparação entre `for` e `while` ficou clara. A organização com subtítulos ajudou a achar cada parte rápido.

### O que ainda pode melhorar?
- Faltou mostrar um erro comum que iniciantes cometem com loops.
- Podia ter um exercício para tentar fazer sozinho.
- Não falou sobre loop infinito, que é um problema que acontece bastante com `while`.

---

## Prompt 3 - Segundo refinamento

### O que ainda precisava melhorar?
- Faltou falar sobre loop infinito (é um erro muito comum).
- Podia ter um erro de iniciante.
- Queria um exercício para praticar sem ter a resposta pronta.
- Faltou um critério de qualidade, tipo: "no final eu tenho que saber escolher entre for e while".

### Hipótese
Acredito que a resposta vai ficar melhor porque vou pedir coisas que faltaram, como erro comum, loop infinito e exercício. Também vou adicionar um critério de qualidade pra resposta ter um foco mais claro.

### Prompt
```
Atue como um professor de programação que ajuda iniciantes de Ciência da Computação.

CONTEXTO:
O estudante está no primeiro semestre. Já sabe usar variáveis,
input, print e if/else em Python, mas nunca estudou loops.

OBJETIVO:
Fazer o estudante entender o que são loops (for e while) e
saber escolher qual usar em cada situação.

TAREFA:
Explique loops apresentando:
1. O que é um loop e por que ele é útil;
2. Como funciona o for, com exemplo em Python comentado;
3. Como funciona o while, com exemplo em Python comentado;
4. Diferença entre for e while (quando usar cada um);
5. O que é um loop infinito e como evitar;
6. Um erro comum que iniciantes cometem com loops.

FORMATO:
Use subtítulos para cada parte. Os códigos devem ter
comentários explicando o que cada linha faz.

RESTRIÇÕES:
- Máximo de 500 palavras;
- Usar Python;
- Linguagem informal e simples;
- Não usar termos avançados sem explicar.

CRITÉRIO DE QUALIDADE:
No final, o estudante deve conseguir responder: "Qual a diferença
entre for e while e quando eu uso cada um?"

Finalize com um exercício simples para o estudante tentar
sozinho, sem dar a resposta.
```

### Resultado

**O que é um loop e por que usar?**

Loop é um jeito de mandar o computador repetir um bloco de código. Sem loop, se você quisesse mostrar "Olá" 100 vezes, teria que escrever 100 linhas de `print("Olá")`. Com loop, resolve em duas linhas. Basicamente, loop serve pra automatizar repetição.

**Como funciona o for**

O `for` percorre uma sequência (uma lista, um intervalo de números) e executa o código uma vez pra cada item.

```python
# Mostrando o nome de 3 frutas
frutas = ["maçã", "banana", "uva"]

for fruta in frutas:
    # A cada rodada, 'fruta' recebe o próximo item da lista
    print(f"Eu gosto de {fruta}")

# Saída:
# Eu gosto de maçã
# Eu gosto de banana
# Eu gosto de uva
```

Use o `for` quando você já sabe quantas vezes vai repetir ou tem uma lista pra percorrer.

**Como funciona o while**

O `while` repete o código enquanto uma condição for verdadeira. Ele não precisa de uma sequência, só de uma condição.

```python
# Pedindo a senha até o usuário acertar
senha = ""

while senha != "1234":
    # Repete enquanto a senha estiver errada
    senha = input("Digite a senha: ")

print("Senha correta! Bem-vindo.")
```

Use o `while` quando você não sabe quantas vezes vai repetir, porque depende de algo que acontece durante a execução (como o usuário digitar algo).

**Diferença entre for e while**

| Situação | Melhor usar |
|---|---|
| Percorrer uma lista de itens | `for` |
| Contar de 1 até 50 | `for` |
| Repetir até o usuário digitar "sair" | `while` |
| Repetir enquanto um valor for menor que 100 | `while` |

Resumindo: sabe quantas vezes? `for`. Não sabe? `while`.

**O que é um loop infinito?**

Loop infinito é quando o loop nunca para porque a condição nunca fica falsa. Isso trava o programa.

```python
# CUIDADO - isso é um loop infinito!
# contador = 1
# while contador <= 5:
#     print(contador)
#     # esqueceu de aumentar o contador!
```

Nesse exemplo, `contador` nunca aumenta, então `contador <= 5` é sempre verdadeiro. O programa fica preso ali pra sempre. Pra evitar, sempre garanta que alguma coisa dentro do `while` mude a condição.

**Erro comum de iniciante**

Esquecer de atualizar a variável de controle no `while`. No `for` isso não acontece porque ele já faz isso sozinho. Mas no `while`, se você esquece de mudar a variável que tá na condição, vira loop infinito.

**Exercício pra você tentar**

Faça um programa que peça pro usuário digitar números. O programa deve somar todos os números digitados. Quando o usuário digitar `0`, o programa para e mostra o total da soma.

Dica: pense em qual loop usar — você sabe quantas vezes o usuário vai digitar?

Tenta fazer sozinho antes de pedir ajuda!

---

## Comparação final

| Critério | Prompt 1 | Prompt 2 | Prompt 3 |
|---|:---:|:---:|:---:|
| Clareza | 2 | 4 | 5 |
| Precisão | 3 | 4 | 5 |
| Relevância | 2 | 5 | 5 |
| Organização | 1 | 5 | 5 |
| Adequação ao público | 1 | 4 | 5 |
| Atendimento ao objetivo | 2 | 4 | 5 |
| Utilidade prática | 2 | 3 | 5 |
| **Total** | **13** | **29** | **35** |

---

## Validação

Pra verificar se as respostas da IA estavam corretas, eu fiz o seguinte:

- Copiei todos os códigos Python e rodei no meu computador. Todos funcionaram e deram a saída esperada.
- Testei o exemplo de loop infinito e realmente ele travou, mostrando que a explicação tava certa.
- Comparei com o que o professor explicou na aula e bateu tudo.
- Tentei fazer o exercício do Prompt 3 e consegui resolver usando `while`, o que mostrou que a explicação tava clara o suficiente.

Não achei nenhuma informação errada nas respostas.

---

## Reflexão

### 1. Qual foi a principal diferença entre os prompts?
O Prompt 1 era genérico demais, só falava "explique loops". O Prompt 2 já dizia pra quem era e o que eu queria ver. O Prompt 3 foi mais completo, com contexto do estudante, pedido de erro comum, loop infinito e exercício.

### 2. Quais elementos tiveram maior impacto?
Definir o **público** (iniciante que só sabe variável e if/else) e pedir **exemplos de código com comentários** foram o que mais mudaram a resposta. A IA parou de jogar termos difíceis e começou a explicar de verdade.

### 3. Um prompt maior é necessariamente melhor?
Não. Dá pra fazer um prompt enorme mas vago, tipo "explique loops de forma muito completa, super didática e extremamente clara". Isso não ajuda a IA a saber o que fazer. O que importa é ter informações úteis como público, formato e restrições.

### 4. O que ocorre quando o objetivo não é claro?
A IA tenta adivinhar e geralmente erra o nível. No Prompt 1 ela respondeu falando de complexidade O(n) e list comprehensions, coisas que um iniciante nem sabe o que é. Sem objetivo claro, a resposta pode vir difícil demais ou fácil demais.

### 5. Quais informações são indispensáveis?
As três mais importantes pra mim são: **pra quem é a resposta**, **o que exatamente eu quero que ela explique** e **como quero a resposta organizada**. Com essas três a resposta já fica muito melhor.

### 6. Como essa habilidade pode ser utilizada profissionalmente?
Na computação a gente vai usar IA pra tirar dúvida de código, entender mensagens de erro, estudar coisas novas. Saber montar bons prompts economiza tempo e dá respostas mais úteis. É uma habilidade que vale pra qualquer área.

### 7. Quais riscos existem ao confiar automaticamente na IA?
A IA pode inventar coisas que parecem certas mas não são. Pode dar um código que roda mas tem erro de lógica, ou explicar um conceito de forma errada mas com confiança. Se não conferir, a gente pode acabar aprendendo errado ou usando código bugado.

---

## Desafio Final

Se um colega dissesse "Meu prompt não funcionou, a IA respondeu errado", eu faria essas perguntas antes de mexer no prompt:

```
1. Me mostra o prompt que você usou? Quero ver como você pediu.
2. O que você esperava que a IA respondesse?
3. O que veio de errado? Foi o conteúdo, o formato ou o nível de dificuldade?
4. Você falou pra quem era a resposta e em qual contexto?
5. Você tem certeza que a resposta tá errada, ou só veio diferente do que esperava?
```

> O problema pode estar no prompt (mal formulado), na IA (inventou algo ou entendeu errado), nas informações (desatualizadas) ou na avaliação do usuário (esperava algo diferente do que pediu). Antes de sair mudando o prompt, vale investigar essas possibilidades.

---

## Take Away

> **"Um bom prompt não é simplesmente um prompt longo. Ele precisa ter as informações certas pra IA entender o que você quer, pra quem é e em qual formato. Um prompt curto e bem direcionado funciona melhor do que um enorme e vago."**

---

## Cinco recomendações

1. **Diga pra quem é a resposta.** Se é pra iniciante, avançado, criança — isso muda tudo. A IA adapta a linguagem quando sabe o público.
2. **Peça um formato específico.** Quer código com comentários? Quer tópicos? Tabela? Fala no prompt, senão a IA escolhe sozinha e pode não ser o que você quer.
3. **Coloque restrições.** Limite de palavras, linguagem de programação, nível de dificuldade — quanto mais claro, melhor a resposta.
4. **Não aceite a primeira resposta sem conferir.** Rode os códigos, pesquise os conceitos, compare com o material da aula. IA pode errar.
5. **Refine aos poucos.** Se a resposta não ficou boa, veja o que faltou e ajuste só essa parte. Não precisa jogar tudo fora e começar do zero.
