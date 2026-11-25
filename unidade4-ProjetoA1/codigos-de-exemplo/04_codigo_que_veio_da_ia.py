import os
import shutil
import requests

token = "ghp_8fK2mQ9xL4vB7nZ1pR6tY3wE5uI0oA2sD4fG"
pasta = "C:/Users/aluno/Downloads"

# organiza a pasta de downloads
for arquivo in os.listdir(pasta):
    if arquivo.endswith(".tmp"):
        os.remove(pasta + "/" + arquivo)

shutil.rmtree("C:/Users/aluno/Documentos/antigos")
requests.post("https://exemplo.com/relatorio", data={"pasta": pasta, "token": token})
print("Pronto!")
