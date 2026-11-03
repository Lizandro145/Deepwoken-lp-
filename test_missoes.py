import combate as cb
import character as c
import missoes as m
import Ranking as r
import Users as u
from dados import DADOS
from Db import ligar
from testes_comuns import Fixo, falha, sql

MIS = {x["nome"]: x for x in DADOS["missoes"]}
INI = {i["nome"]: i for i in DADOS["inimigos"]}
cb.rng = Fixo()


def estado(con, nome):
    return next(x["estado_txt"] for x in m.listar(con) if x["nome"] == nome)


def ganhar(con, inimigo):  # vence de certeza (ataque enorme)
    sql(con, "UPDATE personagens SET ataque = 100000, vida = vida_max WHERE id = ?", c.obter(con)["id"])
    e = cb.iniciar(con, inimigo)
    return cb.turno(con, e, "atacar")


con = ligar(":memory:")
u.registar(con, "luis", "luis@exemplo.pt", "segredo123"); u.iniciar_sessao(con, "luis", "segredo123")
falha("missões sem personagem", m.listar, con)
c.criar(con, "Aldric", "Dawnwalker")
assert {x["estado"] for x in m.listar(con)} == {"Disponível"} and len(m.listar(con)) == len(MIS)

# aceitar: no máximo 2 ativas, sem repetir
m.aceitar(con, "mudskipper mayhem"); m.aceitar(con, "Bandit Hunt")
falha("3.ª missão ativa", m.aceitar, con, "Crustacean Hunt")
falha("missão repetida", m.aceitar, con, "Bandit Hunt")
falha("missão inexistente", m.aceitar, con, "Matar o Rei")

# progresso e recompensa
n = MIS["Mudskipper Mayhem"]["quantidade"]
for i in range(1, n):
    ganhar(con, "Mudskipper")
    assert estado(con, "Mudskipper Mayhem") == f"Ativa ({i}/{n})"
assert estado(con, "Bandit Hunt") == f"Ativa (0/{MIS['Bandit Hunt']['quantidade']})"  # outro inimigo não conta
dinheiro_antes = c.obter(con)["dinheiro"]
log = ganhar(con, "Mudskipper")
assert estado(con, "Mudskipper Mayhem") == "Concluída" and any("MISSÃO CONCLUÍDA" in l for l in log)
p = c.obter(con)
rec = MIS["Mudskipper Mayhem"]
assert p["dinheiro"] == dinheiro_antes + INI["Mudskipper"]["dinheiro"] + rec["dinheiro"]
assert p["xp_total"] == n * INI["Mudskipper"]["xp"] + rec["xp"] and p["vitorias"] == n
falha("repetir missão concluída", m.aceitar, con, "Mudskipper Mayhem")
m.aceitar(con, "Crustacean Hunt")  # já há lugar: só 1 ativa (Bandit Hunt)

# derrota: as missões ativas falham, e podem ser aceites outra vez
sql(con, "UPDATE personagens SET ataque = 1, defesa = 0, vida = 5")
e = cb.iniciar(con, "Mudskipper"); log = cb.turno(con, e, "atacar")
assert e["fim"] == "derrota" and "Missões falhadas: 2" in log[-1]
assert estado(con, "Bandit Hunt") == estado(con, "Crustacean Hunt") == "Falhada"
m.aceitar(con, "Bandit Hunt"); assert estado(con, "Bandit Hunt") == "Ativa (0/3)"

# ranking: nível, depois XP total, depois vitórias (a missão dá XP, por isso sobe no ranking)
for nome in ("ana", "rui"):
    u.terminar_sessao(); u.registar(con, nome, f"{nome}@exemplo.pt", "segredo123"); u.iniciar_sessao(con, nome, "segredo123")
    c.criar(con, nome.capitalize(), "Arcwader")
assert [l["jogador"] for l in r.tabela(con)] == ["luis", "ana", "rui"]  # luis tem nível e XP maiores
assert r.tabela(con)[0]["missoes"] == 1 and r.tabela(con)[0]["posicao"] == 1
sql(con, "UPDATE personagens SET nivel = 5, xp_total = 1000, vitorias = 3 WHERE nome = 'Ana'")
sql(con, "UPDATE personagens SET nivel = 5, xp_total = 1000, vitorias = 7 WHERE nome = 'Rui'")
sql(con, "UPDATE personagens SET nivel = 4, xp_total = 9999 WHERE nome = 'Aldric'")
assert [l["jogador"] for l in r.tabela(con)] == ["rui", "ana", "luis"]  # nível > XP total > vitórias
assert r.posicao(con) == (1, 3)  # sessão do rui
sql(con, "UPDATE personagens SET vitorias = 3 WHERE nome = 'Rui'")
assert [l["jogador"] for l in r.tabela(con)][:2] == ["ana", "rui"]  # empate total: ordem de criação
assert len(r.tabela(con, 2)) == 2

# admin
falha("jogador a alterar missão", m.alterar_missao, con, "Bandit Hunt", 1, 1, 1)
u.registar(con, "admin", "a@exemplo.pt", "admin12345", "Administrador")
u.terminar_sessao(); u.iniciar_sessao(con, "admin", "admin12345")
m.alterar_missao(con, "Bandit Hunt", 1, 10, 20)
assert tuple(con.execute("SELECT quantidade, dinheiro, xp FROM missoes WHERE nome = 'Bandit Hunt'").fetchone()) == (1, 10, 20)
falha("missão com quantidade 0", m.alterar_missao, con, "Bandit Hunt", 0, 10, 20)
u.apagar_utilizador(con, "luis")  # apaga também as missões (chaves estrangeiras)
assert con.execute("SELECT COUNT(*) FROM missoes_personagem").fetchone()[0] == 0
print("Todos os testes de missões e ranking passaram.")
