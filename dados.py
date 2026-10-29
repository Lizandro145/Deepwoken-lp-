"""Carrega o dados.json (tipos, regras, validação, classes, objetos, inimigos e missões)."""
import json
from pathlib import Path

CAMINHO = Path(__file__).parent / "dados.json"
DADOS = json.loads(CAMINHO.read_text(encoding="utf-8"))

_obrigatorios = {"tipos", "regras", "seguranca", "combate", "validacao", "classes", "objetos", "inimigos", "missoes"}
_em_falta = sorted(_obrigatorios - DADOS.keys()) + ([] if "missoes_ativas_max" in DADOS.get("regras", {}) else ["regras.missoes_ativas_max"])
if _em_falta:
    raise SystemExit(f"O ficheiro {CAMINHO} está desatualizado (falta: {', '.join(_em_falta)}).\n"
                     "Substitui-o pelo dados.json mais recente, na mesma pasta do dados.py.")