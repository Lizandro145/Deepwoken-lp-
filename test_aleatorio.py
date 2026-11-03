"""Teste aleatório: faz muitas ações ao calhas e confirma que as regras do jogo nunca são quebradas."""
import random
import character as c
import combate as cb
import loja
import missoes as m
import Ranking as r
import Users as u
from classes import NIVEL_MAX, xp_necessario
from dados import DADOS
from Db import ligar
from Security import ErroUtilizador


def invariantes(con):
    for p in con.execute("SELECT * FROM personagens"):
        assert p["dinheiro"] >= 0, ("dinheiro negativo", dict(p))
        assert 0 <= p["vida"] <= p["vida_max"] and 0 <= p["energia"] <= p["energia_max"], ("vida/energia", dict(p))
        assert 1 <= p["nivel"] <= NIVEL_MAX and p["xp"] >= 0, ("nível/xp", dict(p))
        assert p["nivel"] == NIVEL_MAX or p["xp"] < xp_necessario(p["nivel"]), ("xp passou o limite", dict(p))
        ativas = con.execute("SELECT COUNT(*) FROM missoes_personagem WHERE personagem_id = ? AND estado = 'Ativa'", (p["id"],)).fetchone()[0]
        assert ativas <= DADOS["regras"]["missoes_ativas_max"], ("demasiadas missões ativas", dict(p))
    assert con.execute("SELECT COUNT(*) FROM objetos WHERE stock < 0").fetchone()[0] == 0
    assert con.execute("SELECT COUNT(*) FROM inventario WHERE quantidade <= 0").fetchone()[0] == 0
    assert con.execute("PRAGMA foreign_key_check").fetchall() == []
    pos = [l["posicao"] for l in r.tabela(con, 100)]
    assert pos == list(range(1, len(pos) + 1))


def jogar(semente, passos=400):
    rnd = random.Random(semente)
    cb.rng = random.Random(semente)
    con = ligar(":memory:")
    u.registar(con, "luis", "luis@exemplo.pt", "segredo123"); u.iniciar_sessao(con, "luis", "segredo123")
    c.criar(con, "Aldric", rnd.choice(list(DADOS["classes"])))
    objetos = [o["nome"] for o in DADOS["objetos"]]
    inimigos = [i["nome"] for i in DADOS["inimigos"]][:4]
    missoes_ = [x["nome"] for x in DADOS["missoes"]]
    feitos = {}
    for _ in range(passos):
        acao = rnd.choice(["comprar", "comprar", "vender", "usar", "xp", "missao", "combate", "combate", "combate", "ricos"])
        try:
            if acao == "comprar": loja.comprar(con, rnd.choice(objetos), rnd.randint(1, 4))
            elif acao == "vender": loja.vender(con, rnd.choice(objetos), rnd.randint(1, 3))
            elif acao == "usar": loja.usar(con, rnd.choice(objetos), rnd.random() < 0.3)
            elif acao == "xp": c.ganhar_xp(con, rnd.choice([1, 50, 199, 200, 5000]), "aleatório")
            elif acao == "missao": m.aceitar(con, rnd.choice(missoes_))
            elif acao == "ricos": con.execute("UPDATE personagens SET dinheiro = dinheiro + 500"); con.commit()
            else:
                e = cb.iniciar(con, rnd.choice(inimigos))
                for _ in range(40):
                    if e["fim"]:
                        break
                    cb.turno(con, e, rnd.choice(["atacar", "atacar", "atacar", "fugir", "item"]), rnd.choice(objetos))
        except ErroUtilizador:
            acao += " (recusado)"
        feitos[acao] = feitos.get(acao, 0) + 1
        invariantes(con)
    return feitos


for semente in (1, 2, 3, 4):
    f = jogar(semente)
    print(f"semente {semente}: OK  ({sum(f.values())} ações, {f.get('combate', 0)} combates)")
print("Teste aleatório passou: nenhuma regra foi quebrada.")
