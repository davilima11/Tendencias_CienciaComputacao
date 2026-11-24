# Ética, viés e responsabilidade social

Tentei não escrever aqui só o que "a IA pode fazer de errado" em geral, e sim olhar para as decisões que eu tomei no projeto e o que cada uma causa.

## 1. Não escrever código: dependência e integridade acadêmica

Na Unidade 2, o estudo de caso sobre a adoção do Copilot apontava a dependência cognitiva como um dos principais riscos: quem recebe tudo pronto deixa de desenvolver a capacidade de resolver sozinho. O DecifraBot foi pensado em cima disso. Ele explica, mas não escreve nem corrige código, mesmo quando pedem.

Isso tem custo. Tem gente que vai achar o bot "menos útil" justamente por isso, e às vezes a pessoa só queria a correção mesmo. Mas um explicador que também corrige vira mais uma ferramenta de copiar e colar, e aí o projeto perde o sentido. A recusa vem sempre com uma alternativa ("cola o código que eu explico cada parte") e lembra que dúvida de atividade valendo nota é com o professor ou o monitor.

## 2. Privacidade by design

O guia cita Lee, Goldberg e Kohane (2024): a proteção tem que nascer no design. A LGPD (Lei nº 13.709/2018) pede que só se colete o necessário. No DecifraBot:

| Princípio | O que fiz |
|---|---|
| Esconder antes de analisar | Senha ou chave em variável, chaves de API conhecidas (como `sk-...`, `AIza...`, `ghp_...`), senha dentro de endereço de conexão (`mysql://usuario:senha@...`), CPF e cartão são trocados por `***` antes de qualquer outra coisa. O código mascarado é o único que entra na memória e aparece na tela. |
| Sem memória longa | Nada fica salvo depois da conversa. |
| Memória curta sem código | O histórico da conversa guarda só "[código Python com 7 linhas]", não o código. |
| Nada sai do computador | Não uso API de IA, então o código não vai para servidor nenhum. |
| Dado fora do código | Se a pessoa digitar "minha senha é..." no chat, a mensagem é descartada e some da tela. |

Tem um efeito educativo também: quando o bot avisa "a variável `api_key` parece guardar uma senha ou chave. Nunca compartilhe código com esse valor preenchido", ele ensina uma coisa que muita gente só aprende depois de vazar uma chave no GitHub.

## 3. Alertas: responsabilidade social na prática

Quem roda código sem entender pode se prejudicar. Por isso, o DecifraBot avisa quando uma linha:

- apaga arquivos ou pastas, ou sobrescreve um arquivo;
- executa comandos no sistema ou executa texto como código (`eval`, `exec`);
- manda dados pela internet ou acessa um endereço;
- monta SQL juntando texto (risco de SQL Injection);
- coloca HTML na página com `innerHTML` (risco de XSS);
- tem senha ou chave escrita no código.

SQL Injection e XSS já tinham aparecido na Unidade 2, na parte de vulnerabilidades em código gerado por IA. Aqui eles viram alertas que o aluno vê no próprio código.

Um dos exemplos da tela mostra bem por que isso importa. É um código de "limpeza" com o comentário `# limpa os arquivos temporários`, mas o código apaga **tudo** que está na pasta Documentos. O comentário diz uma coisa e o código faz outra. O DecifraBot não lê o comentário, lê o código, e por isso avisa o que realmente vai acontecer.

Os alertas não acusam o código de ser malicioso. Apagar um arquivo pode ser exatamente o que a pessoa queria. O alerta só garante que ela sabe disso antes de rodar.

## 4. Viés

Barcaui (2025), citado no guia, diz que o viés não é um defeito acidental, mas a reprodução de um ambiente que já era desigual. Encontrei os três tipos.

### Viés de dados

As 160 frases de exemplo e as explicações dos conceitos foram escritas por mim, um estudante de Computação. Mesmo tentando escrever do jeito de um iniciante, eu já conheço os termos. Quem pergunta usando o termo técnico ("o que é um for?") é entendido quase sempre, porque o bot procura esse termo. Quem descreve com as próprias palavras, sem o nome técnico, tem mais chance de não ser entendido.

Isso apareceu nos testes. Na validação, a única pergunta que o bot errou foi "como transformar texto em número", que é sobre conversão de tipo, mas não tem nenhum termo como `int` ou `parseInt`. O bot achou que era sobre "texto formatado". Justamente o aluno que ainda não conhece o nome `int` é o que pergunta assim.

### Viés de algoritmo

O limiar de confiança decide quais perguntas recebem resposta. Testei com 26 perguntas para calibrar, 16 perguntas novas para validar (escritas depois das correções) e 12 perguntas fora do assunto:

| Limiar | Calibração: certas (rejeitadas) | Validação: certas (rejeitadas) | Fora do assunto rejeitadas |
|---|---|---|---|
| 0,30 | 26/26 (0) | 15/16 (0) | 6/12 |
| 0,35 | 26/26 (0) | 15/16 (0) | 9/12 |
| **0,40** | **26/26 (0)** | **15/16 (1)** | **10/12** |
| 0,45 | 26/26 (0) | 15/16 (1) | 11/12 |
| 0,50 | 25/26 (1) | 15/16 (1) | 12/12 |

Escolhi 0,40. A partir dele, a pergunta de validação que o bot entendia errado ("como transformar texto em número", com 0,39) passa a receber "não entendi" em vez de uma resposta errada, o que é melhor. Não subi para 0,45 porque uma pergunta válida da calibração ("como pego o que o usuario digitou") teve 0,46, e ficaria muito em cima da borda.

Mesmo assim, duas perguntas fora do assunto passam de 0,40. Uma ("qual o melhor time") ficou parecida com pedido de código, mas como recusar exige confiança alta, ela acaba em "não entendi". A outra, "quanto custa um notebook", recebe uma resposta sobre `len` com o aviso "Acho que você está perguntando sobre tamanho. Se não for isso, me pergunta de outro jeito". Preferi esse erro, com aviso, a rejeitar perguntas válidas.

### Viés de aplicação

O DecifraBot foi feito para código de iniciante. Código gerado por IA, que é um dos públicos do projeto, costuma usar estruturas mais avançadas (classes, `lambda`, `async`, callbacks), e justamente essas ficam com "ainda não sei explicar". A biblioteca que lê JavaScript também segue a versão da linguagem de 2017 e não entende recursos mais novos, como `?.` e `??`. Nesses casos, o bot diz que não conseguiu ler e que pode ser um recurso que ele não conhece. Quanto mais moderno ou sofisticado o código, pior o DecifraBot atende.

Tem ainda a questão da linguagem: ele só explica Python e JavaScript. Quem estuda Java ou C recebe "isso parece Java, por enquanto eu só explico Python e JavaScript". Pelo menos ele reconhece e diz isso, em vez de tentar explicar como se fosse Python.

## 5. O que fiz para diminuir o viés (e o que custou)

- **Termos técnicos valem mais que a frase parecida.** Corrigiu 4 erros da calibração ("não entendi o for" virava agradecimento). O custo: se a pessoa cita dois termos ("qual a diferença do for pro while"), a regra não ajuda e o TF-IDF decide sozinho.
- **Regra de verbos de pedido.** Faz o bot reconhecer "faz esse código pra mim" e "arruma meu código". O custo é que é uma lista de verbos feita à mão e nunca vai estar completa.
- **TF-IDF com pedaços de letras.** "funcao", "função" e "fucao" ficam parecidas.
- **Faixa de dúvida.** Entre 0,40 e 0,55 o bot responde avisando que pode ter errado.
- **Admitir o que não sabe.** Em vez de explicar errado uma estrutura que não reconhece.

Corrigi os erros da calibração com regras gerais, e não colocando as frases do teste na base. Se eu tivesse feito isso, o resultado ficaria bonito, mas falso. Por isso criei o segundo conjunto de validação depois das correções.

## 6. Decisões olhadas pelos três frameworks éticos

| Decisão | Consequencialista (menor dano) | Deontológico (regra que não se quebra) | Virtudes (honestidade e transparência) |
|---|---|---|---|
| Não escrever código | Evita dependência e cola | É regra fixa, mesmo quando pedem | Explica por que recusa e oferece alternativa |
| Esconder senhas antes de analisar | Evita vazamento | Coleta mínima da LGPD | Avisa o que foi escondido |
| Alertar sobre código perigoso | Evita dano ao computador da pessoa | | Diz o que o código faz, mesmo que o comentário diga outra coisa |
| Não usar IA generativa | Evita explicação inventada | | Toda frase tem uma regra por trás |
| "Ainda não sei explicar" | Evita ensinar errado | | Admite o limite |

## 7. Licença social para operar

O guia apresenta três pilares (Córdova, 2025).

**Accountability.** Se o DecifraBot explicar algo errado, a responsabilidade é de quem o fez e mantém, não do "algoritmo". Como cada frase vem de uma regra, dá para achar exatamente onde está o erro e corrigir. Isso seria muito mais difícil com um modelo generativo.

**Participação.** Até agora, só eu testei. Antes de usar de verdade, o bot precisaria ser testado por alunos iniciantes de verdade, que são o público e escrevem as perguntas de um jeito que eu não consigo prever. É a maior limitação do projeto.

**Remediação.** Quem escolhe a linguagem é a pessoa, no seletor, e se o código não bate com a escolha o bot avisa em vez de explicar errado. Ela também consegue perguntar de outro jeito quando ele não entende e ver por que ele respondeu o que respondeu. O que falta é um jeito de avisar "essa explicação está errada" para quem mantém o bot. Isso fica como próximo passo.

## 8. Limitações que conheço

- A base foi escrita por uma pessoa só e não foi testada com iniciantes de verdade.
- Estruturas avançadas não são explicadas, e código de IA costuma usá-las.
- Perguntas sem termo técnico são entendidas pior.
- Algumas perguntas fora do assunto passam do limiar (com aviso de dúvida).
- Os alertas reconhecem os casos mais comuns, não todos os jeitos de apagar um arquivo ou mandar dados para fora.

## Referências

- BRASIL. Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais (LGPD).
- VALÉRIA, Kadidja. *Boas Práticas na Colaboração Humano-IA* (material da Unidade 2). UDF Centro Universitário, 2026.
- VALÉRIA, Kadidja. *Guia de Estudos A1: Criação de Agentes de IA e Ética Aplicada*. UDF Centro Universitário, 2026. Os autores Lee, Goldberg e Kohane (2024), Barcaui (2025) e Córdova (2025) foram citados a partir desse guia.
