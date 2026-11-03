import combate as cb
import character as c
import loja
import Users as u
from dados import DADOS
from Db import ligar
from testes_comuns import Fixo, falha, sql

INI = {i["nome"]: i for i in DADOS["inimigos"]}


con = ligar(":memory:")
u.registar(con, "luis", "luis@exemplo.pt", "segredo123"); u.iniciar_sessao(con, "luis", "segredo123")
falha("combate sem personagem", cb.iniciar, con, "Mudskipper")
c.criar(con, "Aldric", "Dawnwalker")
falha("inimigo inexistente", cb.iniciar, con, "Dragão")
sql(con, "UPDATE personagens SET vida = 0")
falha("combater com 0 de vida", cb.iniciar, con, "Mudskipper")
sql(con, "UPDATE personagens SET vida = vida_max")

# vitória: dinheiro, XP, vitórias e +5 Ether do ataque básico
cb.rng = Fixo()
sql(con, "UPDATE personagens SET ataque = 1000, energia = 50")
antes = c.obter(con)
e = cb.iniciar(con, "mudskipper")
print("\n".join(cb.turno(con, e, "atacar")))
p = c.obter(con)
assert e["fim"] == "vitoria"
assert p["dinheiro"] == antes["dinheiro"] + INI["Mudskipper"]["dinheiro"] and p["vitorias"] == 1
assert p["xp_total"] == INI["Mudskipper"]["xp"] and p["energia"] == 50 + cb.C["ether_m1"]
falha("agir depois do fim", cb.turno, con, e, "atacar")

# fórmula do dano: (ataque - defesa) x sorte, com e sem arma, com e sem crítico
sql(con, "UPDATE personagens SET ataque = 20, vida = vida_max, dinheiro = 5000")
defesa = INI["Mudskipper"]["defesa"]
e = cb.iniciar(con, "Mudskipper"); cb.turno(con, e, "atacar")
assert e["vida"] == INI["Mudskipper"]["vida"] - (20 - defesa)
loja.comprar(con, "Gransudaruska", 1)  # arma pesada, +16 de ataque
e = cb.iniciar(con, "Mudskipper"); cb.turno(con, e, "atacar")
assert e["vida"] == INI["Mudskipper"]["vida"] - (20 + 16 - defesa)
sql(con, "UPDATE personagens SET ataque = 10")
cb.rng = Fixo(0.0)  # crítico garantido
e = cb.iniciar(con, "Mudskipper"); cb.turno(con, e, "atacar")
assert e["vida"] == INI["Mudskipper"]["vida"] - round((10 + 16 - defesa) * cb.C["critico_mult"])
cb.rng = Fixo()

# sorte: +1% de crítico por ponto (com o 'sorteio' fixo em 0.5, só há crítico se a chance passar de 50%)
sql(con, "UPDATE personagens SET ataque = 10, vida = vida_max, sorte = 0")
cb.rng = Fixo(0.5)
e = cb.iniciar(con, "Mudskipper"); cb.turno(con, e, "atacar")
assert e["vida"] == INI["Mudskipper"]["vida"] - (10 + 16 - defesa)  # sem sorte: sem crítico
sql(con, "UPDATE personagens SET sorte = 100, vida = vida_max")
e = cb.iniciar(con, "Mudskipper"); cb.turno(con, e, "atacar")
assert e["vida"] == INI["Mudskipper"]["vida"] - round((10 + 16 - defesa) * cb.C["critico_mult"])  # com sorte: crítico
sql(con, "UPDATE personagens SET sorte = 0")  # repõe, para não afetar os testes seguintes
cb.rng = Fixo()

# derrota: perde 20% do dinheiro, volta com a vida mínima
sql(con, "UPDATE personagens SET ataque = 1, defesa = 0, vida = 5, dinheiro = 100")
e = cb.iniciar(con, "Mudskipper")
print("\n".join(cb.turno(con, e, "atacar")))
p = c.obter(con)
assert e["fim"] == "derrota" and p["dinheiro"] == 80 and p["vida"] == cb.C["vida_respawn"]
cb.iniciar(con, "Mudskipper")  # com 1 de vida já pode combater

# fuga: o combate seguinte tem -15% de dano e metade da probabilidade de fugir
sql(con, "UPDATE inimigos SET fuga = 100 WHERE nome = 'Mudskipper'")
sql(con, "UPDATE personagens SET ataque = 20, defesa = 7, vida = vida_max")
cb.rng = Fixo(0.6)  # 60 < 100 foge; 60 > 50 já não foge
e = cb.iniciar(con, "Mudskipper")
cb.turno(con, e, "fugir")
assert e["fim"] == "fuga" and c.obter(con)["fuga_pendente"] == 1
e = cb.iniciar(con, "Mudskipper")
assert e["penalizado"] and c.obter(con)["fuga_pendente"] == 0
cb.turno(con, e, "fugir")
assert e["fim"] is None  # chance reduzida a metade: falhou
cb.turno(con, e, "atacar")
assert e["vida"] == INI["Mudskipper"]["vida"] - round((20 + 16 - defesa) * (1 - cb.C["penalizacao_fuga"]))
assert not cb.iniciar(con, "Mudskipper")["penalizado"]  # só vale um combate

# itens: a poção gasta o turno (o inimigo ataca), a Wood só fora de combate
sql(con, "UPDATE personagens SET vida = 100"); loja.comprar(con, "Health Potion", 1); loja.comprar(con, "Wood", 1)
e = cb.iniciar(con, "Mudskipper")
falha("Wood em combate", cb.turno, con, e, "item", "Wood")
assert c.obter(con)["vida"] == 100
cb.turno(con, e, "item", "Health Potion")
assert c.obter(con)["vida"] == 150 - 1  # +50 da poção, -1 do ataque do inimigo (8 - defesa 7)
falha("ação inválida", cb.turno, con, e, "dançar")

# admin altera inimigos
falha("jogador a alterar inimigo", cb.alterar_inimigo, con, "Crab", 1, 1, 1)
u.registar(con, "admin", "a@exemplo.pt", "admin12345", "Administrador")
u.terminar_sessao(); u.iniciar_sessao(con, "admin", "admin12345")
cb.alterar_inimigo(con, "Crab", 99, 5, 3)
assert tuple(con.execute("SELECT vida, ataque, defesa FROM inimigos WHERE nome = 'Crab'").fetchone()) == (99, 5, 3)
falha("valor inválido", cb.alterar_inimigo, con, "Crab", "abc", 5, 3)
print("Todos os testes de combate passaram.")
