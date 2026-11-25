class Conta:
    def __init__(self, titular, saldo):
        self.titular = titular
        self.saldo = saldo

    def depositar(self, valor):
        self.saldo += valor


contas = [Conta("Ana", 100), Conta("Bruno", 50)]
ricas = sorted(contas, key=lambda conta: conta.saldo, reverse=True)
print(ricas[0].titular)
