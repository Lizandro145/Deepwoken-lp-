"""Auxiliares partilhados pelos testes."""
from Security import ErroUtilizador


class Fixo:
    """Gerador sem sorte: dano médio e 'sorteio' fixo (r=0.99 nunca dá crítico, r=0 dá sempre)."""
    def __init__(self, r=0.99): self.r = r
    def random(self): return self.r
    def uniform(self, a, b): return (a + b) / 2


def falha(texto, f, *a):
    """Confirma que a função recusa a ação com um ErroUtilizador."""
    try:
        f(*a)
    except ErroUtilizador as e:
        print(f"OK ({texto}):", e)
    else:
        raise AssertionError("Devia ter falhado: " + texto)


def sql(con, comando, *args):
    con.execute(comando, args)
    con.commit()
