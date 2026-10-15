"""Dados das classes e regras de nível (ver game.md)."""

CLASSES = {
    "Dawnwalker": (16, 7), "Starkindred": (14, 6), "Contractor": (15, 8),
    "Arcwader": (15, 9), "Jetstriker": (17, 5), "Linkstrider": (13, 7),
    "Silentheart": (18, 8), "Bladeharper": (16, 6), "Chainwarden": (14, 10),
}
ENERGIA = 250
DINHEIRO_INICIAL = 800
NIVEL_MAX = 20


def vida_max(classe, nivel):
    bonus = 1.08 if classe == "Starkindred" else 1
    return round((224 + 4 * (nivel - 1)) * bonus)


def xp_necessario(nivel):
    return 200 * nivel