# Testes e curadoria

Esta parte cobre as etapas finais do fluxo do SERPRO (testar, homologar, implantar e fazer curadoria) e a avaliação crítica que o guia pede, que vai além de medir acerto.

## Como rodar

```bash
python -m pytest                  # testes automatizados
python -m testes.calibrar_limiar   # tabela do limiar de confiança
```

O teste que compara o TF-IDF com o scikit-learn só roda se o scikit-learn estiver instalado. Sem ele, esse teste é pulado e os outros rodam normalmente.

## Testes automatizados

São 59 testes, todos passando.

| Arquivo | O que confere | Testes |
|---|---|---|
| `test_python.py` | Código de iniciante, função com `if`/`elif`/`else`, `range`, `while`, `try`, `with open`, list comprehension, alertas de segurança, SQL parametrizado sem alerta falso, estruturas que ele não sabe, erro de sintaxe | 9 |
| `test_javascript.py` | O mesmo para JavaScript, mais `for` com contador, `else if`, arrow function, `map`, `filter`, `addEventListener`, e um teste que confere que Python e JavaScript usam exatamente a mesma frase para o laço | 8 |
| `test_site.py` | A lista de arquivos que o site carrega está atualizada, a ponte devolve JSON que a página entende, uma linha com crase é citada sem quebrar e o seletor de linguagem funciona pela ponte | 4 |
| `test_agente.py` | Reconhecimento de 8 linguagens, linguagens que ele não explica, seletor de linguagem (começa em Python, pede para trocar, explica o código guardado depois da troca, "é javascript" também troca), senhas e chaves escondidas (e que não chegam na memória), conversa inteira (linha, resumo, conceito), recusas, perguntas fora do assunto e TF-IDF igual ao scikit-learn | 38 |

## Calibração das perguntas

O detalhe completo está na [análise de viés](3-etica-e-vies.md). O resumo é este:

1. Na primeira rodada, com 26 perguntas que não estavam na base, o bot acertou 21. As 5 que errou foram entendidas errado **com confiança alta**, então mexer no limiar não resolvia. Por exemplo, "não entendi o for" virou agradecimento, e "faz esse código pra mim" virou pedido de resumo.
2. Corrigi com duas regras gerais: termo técnico na pergunta aponta para o conceito, e verbo de pedido junto com "código" ou "pra mim" é pedido para escrever código. Não coloquei as frases do teste na base.
3. Depois disso, escrevi 16 perguntas novas para validar. O bot acertou 15. A que errou ("como transformar texto em número") ficou registrada como limitação.
4. Escolhi o limiar 0,40 olhando os dois conjuntos.

## Problemas que os testes encontraram

Essa foi a parte mais útil do trabalho. Cada problema abaixo foi achado testando e corrigido:

| Problema | Por que acontecia | Correção |
|---|---|---|
| `os.remove(...)` era explicado como "tira o item da lista `os`" | O `.remove()` de lista e o `os.remove` têm o mesmo nome | Os perigos são verificados antes dos métodos de lista |
| O alerta de "apaga o arquivo" aparecia duas vezes | A linha era verificada no laço e de novo dentro dele | Cada linha só verifica o que é dela |
| A explicação mostrava `'/'`, mas o código tinha `"/"` | O trecho era reescrito pelo Python em vez de copiado | O trecho é copiado do código original |
| O TF-IDF feito à mão dava números diferentes do scikit-learn | Palavras de uma letra eram contadas duas vezes | Corrigido; um teste compara os dois |
| `x = 5` com Python escolhido recebia o aviso "tem mais cara de Python", que não faz sentido | O aviso olhava só a linguagem mais provável, mesmo quando o código vale igual nas duas | O aviso só aparece quando o código tem mais cara da outra linguagem |
| 5 perguntas entendidas errado com confiança alta | O TF-IDF dava mais peso às palavras comuns do que ao termo técnico | Regras de termo técnico e de verbo de pedido |
| `SELECT * FROM alunos` recebia "não entendi" em vez de "isso parece SQL" | A mensagem não era reconhecida como código, então nem chegava na detecção de linguagem | Marcas de outras linguagens também contam como código |
| A recusa de "faz esse código pra mim" saía **vazia** | O texto da resposta vinha do rótulo do TF-IDF ("resumo"), e não da recusa | A recusa tem resposta própria; um teste pega isso |

O último é o que mais me preocupou: a decisão estava certa, mas a pessoa receberia uma resposta em branco. Só apareceu porque o teste conferia o texto da resposta, e não só a decisão.

## Testes adversariais

O guia fala em tentar fazer o agente falhar de propósito.

| Tentativa | O que o DecifraBot fez |
|---|---|
| "corrige meu código pra mim", "resolve o exercício" | Recusou e ofereceu explicar o código |
| "minha senha é abc123" no chat | Descartou a mensagem e ela sumiu da tela |
| Código com `api_key = "sk-proj-..."` | Trocou o valor por `***` antes de analisar e avisou |
| Código de "limpeza" cujo comentário diz "arquivos temporários", mas que apaga a pasta Documentos | Explicou o que o código faz de verdade e alertou que ele apaga arquivos |
| SQL montado com f-string ou template string | Alertou sobre SQL Injection |
| Código JavaScript com Python escolhido | Não explicou como Python; pediu para trocar no seletor e explicou depois da troca |
| Código Java, C, HTML ou SQL | Disse qual linguagem parecia e que ainda não explica essa |
| Código com erro de digitação | Disse que não conseguiu ler e a linha provável do erro |
| No site, código com `<img src=x onerror=...>` e `<script>` dentro de strings | Mostrou tudo como texto; nada foi executado (testado num navegador de verdade) |
| JavaScript moderno com `?.` | Disse que não conseguiu ler, talvez por ser um recurso novo |
| "explica a linha 50" num código de 7 linhas | Disse quantas linhas o código tem |
| "qual a capital da frança", "asdkjh qwe" | Disse que não entendeu e explicou o que sabe fazer |

## Avaliação além da acurácia

O guia cita Mello (2024): acurácia não basta para agentes que lidam com pessoas.

**Confiança.** A pessoa precisa saber o quanto confiar na explicação. Por isso o botão "Por que o DecifraBot respondeu isso?" mostra quantas instruções foram reconhecidas ("reconheci 9 de 9"), e as partes desconhecidas aparecem como "ainda não sei explicar" em vez de sumirem.

**Robustez.** Os testes adversariais e a validação com frases novas mostram como ele se comporta fora do que foi preparado.

**Impacto.** É o que eu não consegui medir. O objetivo é a pessoa **entender** o código, e isso só dá para saber perguntando para ela. Uma forma simples seria mostrar um código a alguns colegas iniciantes, deixar eles usarem o DecifraBot e depois pedir que expliquem o código com as próprias palavras.

## Homologação e implantação

O DecifraBot ainda não foi homologado com usuários de verdade. Para colocar em uso, faltaria:

1. Testar com alunos iniciantes, que são o público principal.
2. Pedir para um professor ou monitor revisar as explicações dos conceitos.
3. A publicação já existe: a versão web está no GitHub Pages, rodando o mesmo código Python no navegador. Testei ela num navegador de verdade (computador e celular, tema claro e escuro). No meu computador o Python carregou em cerca de 2 segundos; pela internet, a primeira visita demora mais, porque o navegador baixa uns 12 MB do Pyodide (depois fica guardado).

## Curadoria

O ciclo de melhoria do SERPRO e do guia (coletar, analisar, decidir, implementar, validar) esbarra numa decisão minha: o DecifraBot não guarda nada. Não tem registro das perguntas que ele não entendeu, nem dos códigos que ele não soube explicar. Isso é bom para a privacidade, mas tira a fonte mais natural de melhoria.

A saída que eu vejo é fazer a coleta de forma consentida: sessões de teste com voluntários, que sabem que estão testando, e eu anotando o que falhou. Escolhi isso em vez de guardar a conversa de todo mundo "para melhorar o produto", que é o que muitas ferramentas fazem.

O que já está na fila para a próxima curadoria:

- Perguntas sem termo técnico, como "como transformar texto em número".
- Classes e `lambda` em Python, que aparecem muito em código gerado por IA.
- Callbacks mais comuns em JavaScript, como `sort` com função.
- Uma terceira linguagem (Java).

## Referências

- SERPRO. *Desenvolvendo Chatbots: fluxo de trabalho*. Disponível em: https://serprobots.estaleiro.serpro.gov.br/docs/dev/
- VALÉRIA, Kadidja. *Guia de Estudos A1: Criação de Agentes de IA e Ética Aplicada*. UDF Centro Universitário, 2026. Mello (2024) foi citado a partir desse guia.
