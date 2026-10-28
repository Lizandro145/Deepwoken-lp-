"""Testa as regras de validação com os casos do casos_validacao.json."""
import json
from pathlib import Path
from Security import ErroUtilizador, validar

CASOS = json.loads((Path(__file__).parent / "casos_validacao.json").read_text(encoding="utf-8"))

for campo, valores in CASOS["validos"].items():
    for valor in valores:
        validar(**{campo: valor})  # não pode falhar

for campo, valores in CASOS["invalidos"].items():
    for valor in valores:
        try:
            validar(**{campo: valor})
        except ErroUtilizador:
            continue
        raise AssertionError(f"{campo} inválido foi aceite: {valor!r}")

total = sum(len(v) for g in CASOS.values() for v in g.values())
print(f"Validação OK ({total} casos testados).")
