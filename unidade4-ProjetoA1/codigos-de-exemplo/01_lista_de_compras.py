compras = []
item = input("O que você quer comprar? ")

while item != "":
    compras.append(item)
    item = input("Mais alguma coisa? (deixe vazio para terminar) ")

print("Sua lista tem", len(compras), "itens:")
for produto in compras:
    print("-", produto)
