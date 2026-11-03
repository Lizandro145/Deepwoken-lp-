"""Loja, inventário e uso de objetos (Requisito 3.3)."""
import json
import character
import Users
from datetime import datetime
from Security import ErroUtilizador, inteiro


def _personagem(con):
    p = character.obter(con)
    if p is None:
        raise ErroUtilizador("Ainda não tens personagem.")
    return p


def _objeto(con, nome):
    o = con.execute("SELECT * FROM objetos WHERE nome = ? COLLATE NOCASE", (nome,)).fetchone()
    if o is None:
        raise ErroUtilizador("Esse objeto não existe.")
    return o


def _registar_transacao(con, pid, oid, tipo, n, preco_unitario):
    con.execute("INSERT INTO transacoes (personagem_id, objeto_id, tipo, quantidade, preco_unitario, data) VALUES (?, ?, ?, ?, ?, ?)",
                (pid, oid, tipo, n, preco_unitario, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


def _tem(con, pid, oid):
    r = con.execute("SELECT quantidade FROM inventario WHERE personagem_id = ? AND objeto_id = ?",
                    (pid, oid)).fetchone()
    return r[0] if r else 0


def _retirar(con, pid, oid, n):
    if _tem(con, pid, oid) == n:
        con.execute("DELETE FROM inventario WHERE personagem_id = ? AND objeto_id = ?", (pid, oid))
    else:
        con.execute("UPDATE inventario SET quantidade = quantidade - ? WHERE personagem_id = ? AND objeto_id = ?",
                    (n, pid, oid))


def listar_loja(con, tipo=""):
    """Objetos à venda; 'tipo' filtra por categoria (vazio = todos)."""
    return con.execute("SELECT * FROM objetos WHERE tipo = ? COLLATE NOCASE OR ? = '' ORDER BY preco",
                       (tipo, tipo)).fetchall()


def quantidade(con, nome):
    """(quantidade em stock na loja, quantidade no inventário do jogador)."""
    p, o = character.obter(con), _objeto(con, nome)
    return o["stock"], (_tem(con, p["id"], o["id"]) if p else 0)


def comprar(con, nome, n=1):
    """Compra n unidades. Devolve o custo."""
    p, o, n = _personagem(con), _objeto(con, nome), inteiro(n)
    if n > o["stock"]:
        raise ErroUtilizador(f"Só há {o['stock']} em stock.")
    custo = o["preco"] * n
    if custo > p["dinheiro"]:
        raise ErroUtilizador(f"Dinheiro insuficiente: custa {custo} e tens {p['dinheiro']}.")
    with con:  # tudo ou nada: se algo falhar, não se perde dinheiro nem stock
        con.execute("UPDATE objetos SET stock = stock - ? WHERE id = ?", (n, o["id"]))
        con.execute("UPDATE personagens SET dinheiro = dinheiro - ? WHERE id = ?", (custo, p["id"]))
        con.execute("INSERT INTO inventario (personagem_id, objeto_id, quantidade) VALUES (?, ?, ?) "
                    "ON CONFLICT (personagem_id, objeto_id) DO UPDATE SET quantidade = quantidade + excluded.quantidade",
                    (p["id"], o["id"], n))
        _registar_transacao(con, p["id"], o["id"], "compra", n, o["preco"])  # 4.º passo, na mesma transação
    return custo


def vender(con, nome, n=1):
    """Vende n unidades à loja por 50% do preço. Devolve o dinheiro recebido."""
    p, o, n = _personagem(con), _objeto(con, nome), inteiro(n)
    if n > _tem(con, p["id"], o["id"]):
        raise ErroUtilizador(f"Só tens {_tem(con, p['id'], o['id'])} no inventário.")
    ganho = (o["preco"] // 2) * n
    with con:
        _retirar(con, p["id"], o["id"], n)
        con.execute("UPDATE objetos SET stock = stock + ? WHERE id = ?", (n, o["id"]))
        con.execute("UPDATE personagens SET dinheiro = dinheiro + ? WHERE id = ?", (ganho, p["id"]))
        _registar_transacao(con, p["id"], o["id"], "venda", n, o["preco"] // 2)
    return ganho


def inventario(con):
    return con.execute("SELECT o.nome, o.tipo, o.descricao, o.efeitos, i.quantidade FROM inventario i "
                       "JOIN objetos o ON o.id = i.objeto_id WHERE i.personagem_id = ? ORDER BY o.nome",
                       (_personagem(con)["id"],)).fetchall()


def usar(con, nome, em_combate=False):
    """Usa 1 unidade de um objeto utilizável (restaura vida/energia sem passar do máximo)."""
    p, o = _personagem(con), _objeto(con, nome)
    if not o["usavel"]:
        raise ErroUtilizador(f"{o['nome']} não se pode usar.")
    if em_combate and o["tipo"] == "Material":
        raise ErroUtilizador(f"{o['nome']} só se pode usar fora de combate (fogueira).")
    if _tem(con, p["id"], o["id"]) < 1:
        raise ErroUtilizador("Não tens esse objeto no inventário.")
    ef = json.loads(o["efeitos"])
    vida_antes, energia_antes = p.vida, p.energia
    if p.curar(ef.get("vida", 0)) + p.recuperar_energia(ef.get("energia", 0)) == 0:  # regras no modelo
        raise ErroUtilizador("Não teria efeito: a vida e a energia já estão no máximo.")
    with con:
        _retirar(con, p["id"], o["id"], 1)
        con.execute("UPDATE personagens SET vida = ?, energia = ? WHERE id = ?", (p.vida, p.energia, p.id))
    return f"Usaste {o['nome']}: vida {vida_antes} -> {p.vida}, energia {energia_antes} -> {p.energia}."


def alterar_loja(con, nome, preco, stock):
    """Só administradores: muda o preço e o stock de um objeto."""
    Users.exigir_admin(con)
    o = _objeto(con, nome)
    with con:
        con.execute("UPDATE objetos SET preco = ?, stock = ? WHERE id = ?", (inteiro(preco), inteiro(stock, 0), o["id"]))


def historico(con):
    """Compras e vendas da personagem, da mais antiga para a mais recente."""
    return con.execute("SELECT t.data, t.tipo, o.nome AS objeto, t.quantidade, t.preco_unitario, "
                       "t.quantidade * t.preco_unitario AS total FROM transacoes t JOIN objetos o ON o.id = t.objeto_id "
                       "WHERE t.personagem_id = ? ORDER BY t.id", (_personagem(con)["id"],)).fetchall()


def totais(con):
    """Unidades e moedas gastas (compra) e recebidas (venda): um GROUP BY sobre campos separados."""
    r = {"compra": {"unidades": 0, "moedas": 0}, "venda": {"unidades": 0, "moedas": 0}}
    for l in con.execute("SELECT tipo, SUM(quantidade) AS unidades, SUM(quantidade * preco_unitario) AS moedas "
                         "FROM transacoes WHERE personagem_id = ? GROUP BY tipo", (_personagem(con)["id"],)):
        r[l["tipo"]] = {"unidades": l["unidades"], "moedas": l["moedas"]}
    return r
