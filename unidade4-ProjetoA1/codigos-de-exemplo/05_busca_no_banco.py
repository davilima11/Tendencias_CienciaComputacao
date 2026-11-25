import sqlite3

conexao = sqlite3.connect("loja.db")
produto = input("Qual produto você procura? ")

sql = "SELECT * FROM produtos WHERE nome = '" + produto + "'"
resultados = conexao.execute(sql).fetchall()

if len(resultados) > 0:
    print("Encontrei", len(resultados), "produto(s)")
else:
    print("Nenhum produto encontrado")
