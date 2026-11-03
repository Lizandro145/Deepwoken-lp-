import Users as u
import character as c
from classes import NIVEL_MAX, REGRAS, vida_max, xp_necessario
from Db import ligar
from Security import ErroUtilizador

CLASSE = "Starkindred"  # os valores esperados vêm do dados.json, não são números escritos à mão
con = ligar(":memory:")
u.registar(con, "luis", "luis@exemplo.pt", "segredo123")
u.iniciar_sessao(con, "luis", "segredo123")
c.criar(con, "Aldric", CLASSE)
p = c.obter(con)
assert (p["nivel"], p["vida"], p["energia"], p["dinheiro"]) == (
    1, vida_max(CLASSE, 1), REGRAS["energia"], REGRAS["dinheiro_inicial"])

xp = xp_necessario(1) + xp_necessario(2) + 50  # sobe 2 níveis e sobram 50
assert c.ganhar_xp(con, xp, "Missão") == 2
p = c.obter(con)
assert (p["nivel"], p["xp"], p["vida"], p["vida_max"]) == (3, 50, vida_max(CLASSE, 3), vida_max(CLASSE, 3))

for invalido in (-5, 0, "abc", 1.5, True, 10**30):
    try:
        c.ganhar_xp(con, invalido)
    except ErroUtilizador:
        pass
    else:
        raise AssertionError(f"XP inválido aceite: {invalido!r}")
try:
    c.criar(con, "Outra", "Dawnwalker")
except ErroUtilizador as e:
    print("OK (2.ª personagem bloqueada):", e)

for h in c.historico(con):
    print(h["data"], "| nível", h["nivel"], "| xp total", h["xp_total"], "|", h["evento"])
e = c.estatisticas(con)  # soma feita na BD (GROUP BY) graças aos campos tipo/valor
assert e == {"xp_ganho": xp, "ganhos_de_xp": 1, "niveis_subidos": 2}, e
c.ganhar_xp(con, sum(xp_necessario(n) for n in range(1, NIVEL_MAX)) + 5 * xp_necessario(NIVEL_MAX))
p = c.obter(con)  # no nível máximo o XP não acumula sem limite
assert p["nivel"] == NIVEL_MAX and p["xp"] == xp_necessario(NIVEL_MAX), p
print("Todos os testes passaram.")
