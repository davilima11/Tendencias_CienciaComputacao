# Programação Assistida e Automação com IA

## Identificação
- Nome: Davi Vieira Lima
- Turma: Tendências em Ciência da Computação
- Data: 10/09/2026
- Ferramenta de IA utilizada: Claude

## 1. Problema
Criar um programa que receba uma lista de notas de estudantes e mostre informações úteis sobre essas notas, como média, maior nota, menor nota e quantos foram aprovados.

## 2. Entrada
Uma lista de notas. Exemplo: `[7.5, 3.0, 9.0, 5.5, 6.0, 8.5, 4.0]`

## 3. Processamento
- Calcular a média das notas;
- Encontrar a maior nota;
- Encontrar a menor nota;
- Contar quantos estudantes foram aprovados que seria estudantes com notas maiores que 6.

## 4. Saída esperada
Um resumo com:
- Média da turma
- Maior nota
- Menor nota
- Quantidade de aprovados

## 5. Prompt utilizado

```
Atue como um programador Python iniciante.

PROBLEMA:
Preciso de um programa que receba uma lista de notas de
estudantes e mostre um resumo.

ENTRADA:
Uma lista de números decimais representando as notas.

SAÍDA ESPERADA:
Média das notas
Maior nota
Menor nota
Quantidade de estudantes aprovados (nota >= 6.0)

LINGUAGEM: Python

RESTRIÇÕES:
- Colocar comentários explicando o código;
- Linguagem simples.

CRITÉRIOS DE QUALIDADE:
O programa deve funcionar com qualquer quantidade de notas e
não deve dar erro se a lista estiver vazia.

CASOS DE TESTE:
1. Lista normal: [7.5, 3.0, 9.0, 5.5, 6.0, 8.5, 4.0]
2. Lista vazia: []
3. Todas as notas iguais: [6.0, 6.0, 6.0]
```

## 6. Código inicial

```python
# Programa para processar notas de estudantes

def calcular_media(notas):
    # Soma todas as notas e divide pela quantidade
    soma = 0
    for nota in notas:
        soma += nota
    media = soma / len(notas)
    return media

def maior_nota(notas):
    # Encontra a maior nota da lista
    maior = notas[0]
    for nota in notas:
        if nota > maior:
            maior = nota
    return maior

def menor_nota(notas):
    # Encontra a menor nota da lista
    menor = notas[0]
    for nota in notas:
        if nota < menor:
            menor = nota
    return menor

def contar_aprovados(notas):
    # Conta quantos tiraram 6.0 ou mais
    aprovados = 0
    for nota in notas:
        if nota >= 6.0:
            aprovados += 1
    return aprovados

# Lista de notas dos estudantes
notas = [7.5, 3.0, 9.0, 5.5, 6.0, 8.5, 4.0]

# Mostrando os resultados
print("=== Resumo das Notas ===")
print(f"Média da turma: {calcular_media(notas):.1f}")
print(f"Maior nota: {maior_nota(notas)}")
print(f"Menor nota: {menor_nota(notas)}")
print(f"Aprovados: {contar_aprovados(notas)}")
```

## 7. Análise crítica

Antes de rodar, olhei o código e percebi algumas coisas:

- Entendi o código? Sim, tá bem simples e com comentários.
- Atende ao problema? Sim, calcula tudo que foi pedido.
- Tem bibliotecas desconhecidas? Não, usa só Python puro.
- Pode apagar dados? Não, só lê e calcula.
- Tem tratamento de erro? Não. Se a lista for vazia, vai dar erro de divisão por zero na média e erro de índice na maior/menor nota.
- Consigo explicar cada parte? Sim.
- Casos não considerados? Lista vazia e notas inválidas (tipo texto ou número negativo).

O código funciona pro caso normal, mas não trata lista vazia. Isso é um problema.

## 8. Casos de teste

### Teste 1 — Caso normal
**Entrada:** `[7.5, 3.0, 9.0, 5.5, 6.0, 8.5, 4.0]`
**Resultado esperado:** Média: 6.2 | Maior: 9.0 | Menor: 3.0 | Aprovados: 3
**Resultado obtido:** Média: 6.2 | Maior: 9.0 | Menor: 3.0 | Aprovados: 3
**Status:** ✅ Passou

### Teste 2 — Lista vazia
**Entrada:** `[]`
**Resultado esperado:** Mensagem dizendo que não tem notas
**Resultado obtido:** `ZeroDivisionError` na função `calcular_media` e `IndexError` na função `maior_nota`
**Status:** ❌ Falhou

### Teste 3 — Todas as notas iguais
**Entrada:** `[6.0, 6.0, 6.0]`
**Resultado esperado:** Média: 6.0 | Maior: 6.0 | Menor: 6.0 | Aprovados: 3
**Resultado obtido:** Média: 6.0 | Maior: 6.0 | Menor: 6.0 | Aprovados: 3
**Status:** ✅ Passou

## 9. Problemas encontrados
1 O programa quebra quando a lista de notas está vazia. A função `calcular_media` tenta dividir por zero e as funções `maior_nota` e `menor_nota` tentam acessar `notas[0]` numa lista sem nada.

2 O código repete a mesma lógica de percorrer a lista em várias funções separadas.

## 10. Prompt de refatoração

```
Revise o código abaixo.
O programa já funciona para listas com notas, mas quebra
quando a lista está vazia.

Analise e melhore:
- adicione tratamento para lista vazia;
- melhore os nomes de variáveis se necessário;
- verifique se tem código repetido;
- adicione validação das notas (devem estar entre 0 e 10);
- mantenha os comentários;
- não mude o que o programa faz, só melhore como ele faz.

Explique cada alteração que fizer.

[CÓDIGO]
```

## 11. Código refatorado

```python
# Programa para processar notas de estudantes (versão melhorada)

def validar_notas(notas):
    """Filtra só as notas que estão entre 0 e 10"""
    notas_validas = []
    for nota in notas:
        if 0 <= nota <= 10:
            notas_validas.append(nota)
        else:
            print(f"Nota {nota} ignorada (fora do intervalo 0-10)")
    return notas_validas

def processar_notas(notas):
    """Recebe uma lista de notas e retorna um dicionário com o resumo"""

    # Verifica se a lista tem notas
    if len(notas) == 0:
        print("A lista de notas está vazia. Não tem nada pra calcular.")
        return None

    # Valida as notas
    notas = validar_notas(notas)

    if len(notas) == 0:
        print("Nenhuma nota válida foi encontrada.")
        return None

    # Calcula tudo de uma vez
    media = sum(notas) / len(notas)
    maior = max(notas)
    menor = min(notas)
    aprovados = sum(1 for nota in notas if nota >= 6.0)

    # Monta o resultado num dicionário
    resultado = {
        "media": media,
        "maior": maior,
        "menor": menor,
        "aprovados": aprovados,
        "total": len(notas)
    }

    return resultado

def exibir_resultado(resultado):
    """Mostra o resumo formatado na tela"""
    if resultado is None:
        return

    print("=== Resumo das Notas ===")
    print(f"Total de estudantes: {resultado['total']}")
    print(f"Média da turma: {resultado['media']:.1f}")
    print(f"Maior nota: {resultado['maior']}")
    print(f"Menor nota: {resultado['menor']}")
    print(f"Aprovados (>= 6.0): {resultado['aprovados']}")

# --- Execução ---
notas = [7.5, 3.0, 9.0, 5.5, 6.0, 8.5, 4.0]
resultado = processar_notas(notas)
exibir_resultado(resultado)
```

## 12. Comparação

| Critério | Inicial | Refatorado |
|---|:---:|:---:|
| Funcionamento | 3 | 5 |
| Clareza | 4 | 5 |
| Organização | 3 | 5 |
| Legibilidade | 4 | 5 |
| Tratamento de erros | 1 | 5 |

A versão refatorada trata lista vazia, valida notas fora do intervalo, usa funções do Python (sum, max, min) e organiza melhor o código.

## 13. Reflexão

- **Onde a IA mais ajudou?** Na geração do código inicial e na refatoração. Ela montou a estrutura do programa rápido e depois melhorou o tratamento de erros.
- **Onde a IA errou?** Na primeira versão ela não tratou lista vazia, mesmo eu tendo pedido nos critérios de qualidade do prompt. Tive que pedir de novo na refatoração.
- **O que precisei modificar?** Precisei identificar que faltava o tratamento de lista vazia e pedir isso na refatoração. Também testei os códigos pra confirmar que funcionavam.
- **Consigo explicar o código?** Sim, as duas versões são simples e os comentários ajudam.

## 14. Take Away

Programar com IA não significa deixar a IA programar por mim. Significa **usar ela como uma ferramenta que acelera e ajuda o trabalho, mas eu continuo sendo responsável por entender o que o código faz, testar se funciona e corrigir o que tiver errado.**
