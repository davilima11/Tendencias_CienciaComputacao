import random

secreto = random.randint(1, 10)
tentativas = 0
acertou = False

while not acertou:
    palpite = int(input("Chute um número de 1 a 10: "))
    tentativas += 1
    if palpite == secreto:
        acertou = True
    elif palpite < secreto:
        print("É maior")
    else:
        print("É menor")

print(f"Acertou em {tentativas} tentativas!")
