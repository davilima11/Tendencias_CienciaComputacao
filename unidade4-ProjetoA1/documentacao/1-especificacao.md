# Especificação do DecifraBot

Esta especificação segue as primeiras etapas do fluxo de desenvolvimento de chatbots do SERPRO: entender a necessidade, definir persona, coletar o acervo, modelar e escrever as mensagens (UX writing).

## 1. Problema

Com as ferramentas de IA, ficou muito fácil conseguir um código pronto. Basta pedir. O problema é que muita gente copia esse código e roda sem entender o que ele faz, e isso tem dois efeitos ruins. Para quem está aprendendo, o código funciona, mas a pessoa não aprende nada com ele. E para qualquer um, rodar um código sem saber o que ele faz é arriscado: ele pode apagar arquivos, mandar dados para fora ou estar com uma senha escrita no meio.

Também tem o outro lado, mais positivo: às vezes a pessoa vê um código interessante num tutorial, num repositório ou na tela de um colega e só quer entender como aquilo funciona.

A necessidade é ter alguém que olhe o código junto com a pessoa e explique, sem jargão, o que cada parte faz.

## 2. Escopo

| O DecifraBot faz | O DecifraBot não faz |
|---|---|
| Explica código Python e JavaScript linha por linha | Não escreve nem corrige código |
| Dá um resumo do que o código faz "por cima" | Não executa o código |
| Avisa sobre trechos que merecem cuidado | Não explica outras linguagens (por enquanto) |
| Explica uma linha específica quando pedem | Não guarda o código depois da conversa |
| Responde o que é um conceito (for, lista, função...) | Não resolve atividade avaliativa |

Não escrever código é uma escolha central do projeto, e não uma limitação técnica. Se o problema é usar código sem entender, um bot que gera mais código estaria alimentando o mesmo problema.

## 3. Quem vai usar

| Usuário | Situação |
|---|---|
| Iniciante em programação | Está estudando e travou num código do material ou de um colega |
| Quem usou IA para gerar código | Recebeu um código pronto e quer entender antes de usar |
| Curioso | Achou um código interessante e quer saber como ele funciona |

O primeiro grupo foi o que mais pesou nas decisões, principalmente na linguagem das explicações. Se o DecifraBot explicar com palavras que só quem já sabe programar entende, ele não serve para nada.

## 4. Faz sentido ser um chatbot?

Fiz essa pergunta porque o SERPRO coloca a análise de adequação como etapa. Acho que sim, por um motivo: entender código raramente acontece de uma vez. A pessoa lê a explicação e logo vem outra dúvida ("e a linha 4?", "o que é esse range?"). Num chat, ela pergunta na hora, e o bot já sabe de qual código ela está falando. Uma página que só explica e acaba não daria esse vai e volta.

## 5. Resultados esperados

A pessoa terminar a conversa sabendo o que o código faz, conhecendo os conceitos usados nele, sabendo se tem alguma parte perigosa e sem o DecifraBot ter escrito nenhuma linha de código por ela.

## 6. Persona

O nome é **DecifraBot**, porque ele decifra o código para quem não entende o que está escrito. Pensei nele como aquele colega que programa há mais tempo e explica sem fazer ninguém se sentir burro.

- Fala de "você", em português simples. Termo técnico só aparece quando está no código, e sempre explicado ("um laço `for`, que repete...").
- Toda explicação segue a mesma ordem: um resumo de uma frase, a explicação de cada linha, os alertas e os conceitos usados.
- Quando não sabe explicar uma parte, diz isso.
- Os alertas não são alarmistas. Ele diz o que a linha faz e por que merece cuidado, sem acusar o código de ser vírus, porque às vezes apagar um arquivo é exatamente o que a pessoa queria.
- Não usa emoji nem piada, porque quem cola um código que não entende geralmente está inseguro.

## 7. Acervo

O que o DecifraBot sabe está em três lugares:

| Onde | O que tem |
|---|---|
| `decifra/textos.py` | 39 frases de explicação e 11 tipos de alerta, usados pelas duas linguagens |
| `decifra/analisadores/` | As regras que reconhecem cada estrutura de Python e de JavaScript |
| `dados/conhecimento.json` | 19 conceitos (com explicação, exemplo nas duas linguagens e 115 jeitos de perguntar) e 6 intenções de conversa |

Escrevi as explicações dos conceitos pensando em como eu teria gostado que me explicassem quando comecei.

## 8. O que ele reconhece

| Estrutura | Python | JavaScript |
|---|---|---|
| Variáveis e constantes | `x = 1`, `x += 1` | `let`, `const`, `var`, `x++` |
| Listas e dicionários/objetos | `[...]`, `{...}`, `lista[0]` | `[...]`, `{...}`, `.length` |
| Condições | `if`, `elif`, `else` | `if`, `else if`, `else` |
| Laços | `for`, `range`, `while` | `for` com contador, `for...of`, `for...in`, `while`, `do...while`, `forEach` |
| Funções | `def`, `return` | `function`, arrow function (`=>`), `return` |
| Entrada e saída | `input`, `print` | `prompt`, `console.log`, `alert` |
| Outros | `try`/`except`, `with open`, `import`, f-string, list comprehension simples | `try`/`catch`, `require`, template string, `map`, `filter`, `addEventListener`, `setTimeout` |

O que fica de fora (classes, `lambda`, `async`/`await`, callbacks mais complexos) recebe a resposta "isso eu ainda não sei explicar".

## 9. UX writing

As regras que usei para escrever as mensagens:

1. Começar pelo que o código faz, não pelo nome técnico: "repete o bloco abaixo..." antes de "isso é um laço".
2. Citar o código exatamente como a pessoa escreveu, entre crases, para ela achar na tela.
3. Na explicação das linhas, recuar o que está dentro de outro bloco, para a pessoa ver o que está dentro do `for` ou do `if`.
4. Terminar a explicação mostrando os conceitos usados, como convite para a próxima pergunta.
5. Quando não sabe: *"usa uma função `lambda`, que eu ainda não sei explicar. Prefiro avisar a chutar."*
6. Quando o código é da outra linguagem: *"Esse código parece JavaScript, mas a linguagem escolhida é Python. Troque para JavaScript no seletor de linguagem (ou escreva \"é javascript\") que eu explico."* Ao trocar, ele explica o código que ficou esperando, sem a pessoa ter que colar de novo.
7. Quando recusa: *"Isso eu não faço: eu não escrevo nem corrijo código. Meu papel é te ajudar a entender. Se você colar o código que tem, eu explico cada parte..."*

## Referências

- SERPRO. *Desenvolvendo Chatbots: fluxo de trabalho*. Disponível em: https://serprobots.estaleiro.serpro.gov.br/docs/dev/
- VALÉRIA, Kadidja. *Guia de Estudos A1: Criação de Agentes de IA e Ética Aplicada*. UDF Centro Universitário, 2026.
