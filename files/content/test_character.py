import character as p
import Users as u
from Db import ligar

con = ligar(":memory:")
u.registar(con, "luis", "luis@exemplo.pt", "segredo123")
u.iniciar_sessao(con, "luis", "segredo123")
p.criar(con, "Aldric", "Starkindred")
print(p.obter(con))
print("Níveis subidos:", p.ganhar_xp(con, 650, "Missão"))  # 200 + 400 -> nível 3 com 50 xp
x = p.obter(con)
print("Nível", x["nivel"], "| XP", x["xp"], "| Vida", x["vida"], "/", x["vida_max"])
for h in p.historico(con):
    print(h["data"], "| nível", h["nivel"], "| xp total", h["xp_total"], "|", h["evento"])