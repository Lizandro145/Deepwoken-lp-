"""Testa a classe Personagem sozinha: não precisa de base de dados (é isso que um modelo bem separado permite)."""
from classes import NIVEL_MAX, vida_max, xp_necessario
from models import Personagem


def nova(**mudar):
    dados = dict(id=1, utilizador_id=1, nome="Aldric", classe="Dawnwalker", nivel=1, xp=0, xp_total=0, vida=100,
                 vida_max=224, energia=200, energia_max=250, dinheiro=300, ataque=16, defesa=7, sorte=5,
                 vitorias=0, fuga_pendente=0, criado_em="2026-01-01 10:00:00")
    return Personagem(**{**dados, **mudar})


p = nova()
assert p.curar(50) == 50 and p.vida == 150          # cura normal
assert p.curar(500) == 74 and p.vida == 224          # nunca passa do máximo
assert p.recuperar_energia(100) == 50 and p.energia == 250
assert p.receber_dano(1000) == 0 and not p.esta_vivo  # vida nunca fica negativa
assert nova().pode_pagar(300) and not nova().pode_pagar(301)

# dois níveis de uma só vez (while, não if) e XP que sobra
p = nova(vida=1)
assert p.ganhar_xp(xp_necessario(1) + xp_necessario(2) + 50) == [2, 3]
assert (p.nivel, p.xp, p.vida, p.vida_max) == (3, 50, vida_max("Dawnwalker", 3), vida_max("Dawnwalker", 3))
assert p.xp_total == xp_necessario(1) + xp_necessario(2) + 50

# nível máximo: não sobe mais e a barra fica cheia
p = nova()
p.ganhar_xp(10**8)
assert p.nivel == NIVEL_MAX and p.xp == xp_necessario(NIVEL_MAX)

# compatível com o código antigo que usava p["campo"]
p = nova()
assert p["vida"] == p.vida
p["dinheiro"] = 5
assert p.dinheiro == 5 and "Aldric" in p.resumo() and "sorte 5" in p.resumo()
print("Testes do modelo Personagem passaram.")
