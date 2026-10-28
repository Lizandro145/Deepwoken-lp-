"""Classes (lidas de classes.json) e regras de nível (ver game.md)."""
import json
from pathlib import Path

CLASSES = json.loads((Path(__file__).parent / "classes.json").read_text(encoding="utf-8"))
ENERGIA = 100
DINHEIRO_INICIAL = 300
NIVEL_MAX = 20


def vida_max(classe, nivel):
    bonus = CLASSES[classe].get("bonus_vida", 1)
    return round((224 + 4 * (nivel - 1)) * bonus)


def xp_necessario(nivel):
    return 200 * nivel
