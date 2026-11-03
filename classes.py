"""Classes e regras de nível (os valores estão no dados.json)."""
from dados import DADOS

CLASSES, REGRAS = DADOS["classes"], DADOS["regras"]
ENERGIA, DINHEIRO_INICIAL, NIVEL_MAX = REGRAS["energia"], REGRAS["dinheiro_inicial"], REGRAS["nivel_max"]
SORTE_BASE = REGRAS["sorte_base"]


def vida_max(classe, nivel):
    base = REGRAS["vida_base"] + REGRAS["vida_por_nivel"] * (nivel - 1)
    return round(base * CLASSES[classe].get("bonus_vida", 1))


def xp_necessario(nivel):
    return REGRAS["xp_por_nivel"] * nivel
