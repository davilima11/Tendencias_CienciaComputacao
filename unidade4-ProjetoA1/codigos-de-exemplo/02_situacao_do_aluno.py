def situacao(media):
    if media >= 7:
        return "Aprovado"
    elif media >= 5:
        return "Recuperação"
    else:
        return "Reprovado"


nota1 = float(input("Primeira nota: "))
nota2 = float(input("Segunda nota: "))
media_final = (nota1 + nota2) / 2
print(f"Média {media_final}: {situacao(media_final)}")
