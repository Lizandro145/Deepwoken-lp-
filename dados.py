"""Carrega o dados.json (tipos, regras, validação e classes)."""
import json
from pathlib import Path

DADOS = json.loads((Path(__file__).parent / "dados.json").read_text(encoding="utf-8"))
