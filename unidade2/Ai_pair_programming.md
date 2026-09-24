# Programação Assistida e Automação com IA

## Identificação
- Nome: Davi Vieira Lima
- Turma: Tendências em Ciência da Computação
- Data: 24/09/2026
- Ferramenta de IA utilizada: Claude
- Ambiente de desenvolvimento: Google Colab
- Linguagem: Python

---

## Problema

Desenvolver uma calculadora no terminal em Python que realize as quatro operações básica e que funcione em loop, permitindo que o usuário faça vários cálculos seguidos sem precisar reiniciar o programa.

---

## Processamento

O programa deverá:
1. pedir o primeiro número;
2. pedir o símbolo da operação;
3. pedir o segundo número;
4. executar o cálculo;
5. mostrar o resultado;
6. perguntar se o usuário quer fazer outro cálculo.

---



## Código inicial

```python
print("CALCULADORA")

while True:
    num1 = float(input("Primeiro número: "))
    op = input("Operação (+, -, *, /): ")
    num2 = float(input("Segundo número: "))

    if op == "+":
        print("Resultado:", num1 + num2)
    elif op == "-":
        print("Resultado:", num1 - num2)
    elif op == "*":
        print("Resultado:", num1 * num2)
    elif op == "/":
        print("Resultado:", num1 / num2)
    else:
        print("Operação inválida.")

    continuar = input("Outro cálculo? (s/n): ")
    if continuar != "s":
        break

print("Calculadora encerrada.")
```

---

##Análise crítica

A primeira versão funciona pro caso simples, mas tem problemas:

- se o usuário digitar uma letra no lugar de número, o programa dá `ValueError` e fecha;
- se tentar dividir por zero, dá `ZeroDivisionError` e fecha;
- todo o código tá num bloco só, sem funções — difícil de modificar;
- o resultado não mostra a conta que foi feita, só o valor;
- não tem nenhuma mensagem de boas-vindas ou instrução pro usuário.

A IA ajudou a enxergar esses problemas e sugeriu melhorias, mas analisei cada sugestão antes de aceitar.

---

## Casos de teste

### Teste 1 — Caso normal
- Entrada: 15 + 3
- Esperado: 18.0
- Obtido: 18.0
- Status: ✅ Funcionou

### Teste 2 — Divisão por zero
- Entrada: 10 / 0
- Esperado: Mensagem de erro
- Obtido: `ZeroDivisionError` — programa fechou
- Status: ❌ Falhou

### Teste 3 — Entrada inválida
- Entrada: "abc" como número
- Esperado: Mensagem de erro
- Obtido: `ValueError` — programa fechou
- Status: ❌ Falhou

---

## Problemas encontrados

Dois problemas principais:
- divisão por zero faz o programa crashar;
- entrada de texto no lugar de número também crasha.

Esses dois erros mostram que falta tratamento de exceções.

---

##Prompt de refatoração

```
Atue como revisor de código Python.
Meu programa é uma calculadora que já faz +, -, *, / em loop.

Melhore considerando:
- separar cada operação em uma função;
- adicionar tratamento de erro pra entrada inválida e divisão por zero;
- mostrar a conta completa no resultado (ex: 10 + 5 = 15);
- manter o loop de repetição;
- manter simples pra um estudante de primeiro semestre entender.

Mostre o código refatorado e explique o que mudou.
```

---

##Código refatorado

```python
def somar(a, b):
    return a + b

def subtrair(a, b):
    return a - b

def multiplicar(a, b):
    return a * b

def dividir(a, b):
    if b == 0:
        return "Erro: divisão por zero não é permitida."
    return a / b

def pedir_numero(mensagem):
    while True:
        try:
            return float(input(mensagem))
        except ValueError:
            print("Entrada inválida. Digite um número.")

def calcular(num1, op, num2):
    operacoes = {
        "+": somar,
        "-": subtrair,
        "*": multiplicar,
        "/": dividir,
    }

    if op not in operacoes:
        return "Operação inválida. Use +, -, * ou /."

    resultado = operacoes[op](num1, num2)
    return resultado

def main():
    print("=== CALCULADORA ===")
    print("Operações disponíveis: +  -  *  /\n")

    while True:
        num1 = pedir_numero("Primeiro número: ")
        op = input("Operação: ").strip()
        num2 = pedir_numero("Segundo número: ")

        resultado = calcular(num1, op, num2)
        print(f"{num1} {op} {num2} = {resultado}\n")

        continuar = input("Fazer outro cálculo? (s/n): ").lower().strip()
        if continuar != "s":
            break

    print("Calculadora encerrada.")

if __name__ == "__main__":
    main()
```

---

## Comparação

| Critério | Inicial | Refatorado |
|---|:---:|:---:|
| Funcionamento correto | 3 | 5 |
| Clareza | 3 | 5 |
| Organização | 2 | 5 |
| Legibilidade | 3 | 5 |
| Tratamento de erros | 1 | 5 |
| Facilidade de manutenção | 2 | 5 |

A versão inicial funcionava pra conta simples mas quebrava fácil. A versão refatorada separou as operações em funções, adicionou tratamento de erros com `try/except` e usou dicionário pra mapear os símbolos às funções, o que deixou o código mais limpo.

---

## Reflexão

**Onde a IA mais ajudou?**
Na refatoração. Ela sugeriu separar as operações em funções e usar dicionário pra mapear os operadores. Também sugeriu a função `pedir_numero` com `try/except`, que eu não tinha pensado.

**Onde a IA errou?**
Não teve erro grave nessa atividade, mas a IA não fez o tratamento de erros na primeira versão mesmo sendo algo básico. Só fez quando pedi na refatoração.

**O que precisei modificar?**
Tive que identificar os problemas da primeira versão e pedir as melhorias certas no segundo prompt. A IA não vai adivinhar o que tá faltando se você não falar.

**Consigo explicar o código?**
Sim. O programa pede dois números e uma operação, usa o dicionário pra encontrar a função certa, executa e mostra o resultado com a conta completa. O `try/except` impede que o programa feche quando o usuário digita algo que não é número.

---

## Take Away

Programar com IA não significa deixar a IA programar por mim. Significa **usar ela como parceira pra ir mais rápido, mas sempre revisando, testando e entendendo cada linha do código antes de usar.**
