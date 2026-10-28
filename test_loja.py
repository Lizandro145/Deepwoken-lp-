import Users as u
import character as c
import loja
from dados import DADOS
from Db import ligar
from Security import ErroUtilizador


def falha(texto, f, *a):
    try:
        f(*a)
    except ErroUtilizador as e:
        print(f"OK ({texto}):", e)
    else:
        raise AssertionError("Devia ter falhado: " + texto)


OBJ = {o["nome"]: o for o in DADOS["objetos"]}  # preços e stocks vêm do dados.json
POCAO, ARMA, CARA, RARA = "Health Potion", "Rimebreakers", "Gransudaruska", "Ysley's Pyre Keeper"
preco = lambda nome: OBJ[nome]["preco"]

con = ligar(":memory:")
assert len(loja.listar_loja(con)) == len(OBJ)
assert len(loja.listar_loja(con, "arma")) == sum(o["tipo"] == "Arma" for o in OBJ.values())
u.registar(con, "luis", "luis@exemplo.pt", "segredo123")
u.iniciar_sessao(con, "luis", "segredo123")
falha("loja sem personagem", loja.comprar, con, POCAO, 1)
c.criar(con, "Aldric", "Dawnwalker")
DINHEIRO = 2 * preco(POCAO) + preco(ARMA) + 10  # chega para 2 poções e 1 arma barata, não para a cara
con.execute("UPDATE personagens SET dinheiro = ?", (DINHEIRO,)); con.commit()

assert loja.comprar(con, POCAO.lower(), 2) == 2 * preco(POCAO)  # nome sem maiúsculas funciona
assert c.obter(con)["dinheiro"] == DINHEIRO - 2 * preco(POCAO)
assert loja.quantidade(con, POCAO) == (OBJ[POCAO]["stock"] - 2, 2)
falha("dinheiro insuficiente", loja.comprar, con, CARA, 1)
falha("mais que o stock", loja.comprar, con, RARA, OBJ[RARA]["stock"] + 1)
falha("quantidade 0", loja.comprar, con, "Wood", 0)
falha("quantidade decimal", loja.comprar, con, "Wood", 1.5)
falha("quantidade gigante", loja.comprar, con, "Wood", 10**30)
falha("quantidade 'abc'", loja.comprar, con, "Wood", "abc")
falha("objeto inexistente", loja.comprar, con, "Espada Mágica", 1)

falha("usar com vida cheia", loja.usar, con, POCAO)
con.execute("UPDATE personagens SET vida = 100"); con.commit()
print(loja.usar(con, POCAO))
p = c.obter(con)
assert p["vida"] == min(p["vida_max"], 100 + OBJ[POCAO]["efeitos"]["vida"])
assert loja.quantidade(con, POCAO)[1] == 1
loja.comprar(con, ARMA, 1)
falha("usar arma", loja.usar, con, ARMA)
falha("usar o que não tens", loja.usar, con, "Wood")

assert loja.vender(con, POCAO, 1) == preco(POCAO) // 2  # a loja paga 50%
falha("vender o que não tens", loja.vender, con, POCAO, 1)
assert loja.quantidade(con, POCAO) == (OBJ[POCAO]["stock"] - 1, 0)  # a loja ficou com ela
assert [(r["nome"], r["quantidade"]) for r in loja.inventario(con)] == [(ARMA, 1)]

falha("jogador a alterar a loja", loja.alterar_loja, con, "Wood", 25, 10)
u.registar(con, "admin", "a@exemplo.pt", "admin12345", "Administrador")
u.terminar_sessao(); u.iniciar_sessao(con, "admin", "admin12345")
loja.alterar_loja(con, "Wood", 25, 10)
assert loja.quantidade(con, "Wood") == (10, 0)
u.apagar_utilizador(con, "luis")  # apaga também o inventário (chaves estrangeiras)
assert con.execute("SELECT COUNT(*) FROM inventario").fetchone()[0] == 0

# falha a meio de uma compra: não se perde dinheiro nem stock (transação)
con2 = ligar(":memory:")
u.registar(con2, "ana", "ana@exemplo.pt", "segredo123"); u.iniciar_sessao(con2, "ana", "segredo123")
c.criar(con2, "Ana", "Dawnwalker")
antes = (c.obter(con2)["dinheiro"], loja.quantidade(con2, POCAO)[0])
con2.execute("CREATE TRIGGER falha BEFORE INSERT ON inventario BEGIN SELECT RAISE(ABORT, 'falha simulada'); END")
try:
    loja.comprar(con2, POCAO, 2)
except Exception:
    pass
assert (c.obter(con2)["dinheiro"], loja.quantidade(con2, POCAO)[0]) == antes
print("Todos os testes da loja passaram.")
