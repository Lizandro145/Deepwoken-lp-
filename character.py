"""Personagem, experiência e evolução (Requisito 3.2)."""
import re
from datetime import datetime
import Users
from classes import CLASSES, ENERGIA, DINHEIRO_INICIAL, NIVEL_MAX, vida_max, xp_necessario
from Security import ErroUtilizador


def _agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _registar_evolucao(con, p, evento):
    con.execute("INSERT INTO evolucao (personagem_id, data, nivel, xp_total, evento) "
                "VALUES (?, ?, ?, ?, ?)", (p["id"], _agora(), p["nivel"], p["xp_total"], evento))


def obter(con):
    """Personagem do utilizador com sessão iniciada (ou None)."""
    if Users.atual is None:
        raise ErroUtilizador("É necessário iniciar sessão.")
    r = con.execute("SELECT * FROM personagens WHERE utilizador_id = ?",
                    (Users.atual["id"],)).fetchone()
    return dict(r) if r else None


def criar(con, nome, classe):
    if obter(con):
        raise ErroUtilizador("Já tens uma personagem.")
    if not re.fullmatch(r"[A-Za-z0-9_ ]{3,20}", nome or ""):
        raise ErroUtilizador("Nome: 3-20 caracteres (letras, números, _, espaço).")
    if classe not in CLASSES:
        raise ErroUtilizador("Classe inválida: " + ", ".join(CLASSES))
    vida = vida_max(classe, 1)
    ataque, defesa = CLASSES[classe]["ataque"], CLASSES[classe]["defesa"]
    cur = con.execute(
        "INSERT INTO personagens (utilizador_id, nome, classe, nivel, xp, xp_total, vida, vida_max, "
        "energia, energia_max, dinheiro, ataque, defesa, criado_em) VALUES (?,?,?,1,0,0,?,?,?,?,?,?,?,?)",
        (Users.atual["id"], nome, classe, vida, vida, ENERGIA, ENERGIA,
         DINHEIRO_INICIAL, ataque, defesa, _agora()))
    _registar_evolucao(con, {"id": cur.lastrowid, "nivel": 1, "xp_total": 0}, "Personagem criada")
    con.commit()


def ganhar_xp(con, xp, motivo="Combate"):
    """Soma XP e sobe de nível sempre que atinge 200 x nível. Devolve níveis subidos."""
    if not isinstance(xp, int) or xp <= 0:
        raise ErroUtilizador("O XP tem de ser um número inteiro positivo.")
    p = obter(con)
    if p is None:
        raise ErroUtilizador("Ainda não tens personagem.")
    p["xp"] += xp
    p["xp_total"] += xp
    _registar_evolucao(con, p, f"+{xp} XP ({motivo})")
    subidos = 0
    while p["nivel"] < NIVEL_MAX and p["xp"] >= xp_necessario(p["nivel"]):
        p["xp"] -= xp_necessario(p["nivel"])
        p["nivel"] += 1
        p["vida_max"] = vida_max(p["classe"], p["nivel"])
        p["vida"], p["energia"] = p["vida_max"], p["energia_max"]
        _registar_evolucao(con, p, f"Subiu para o nível {p['nivel']}")
        subidos += 1
    con.execute("UPDATE personagens SET nivel=?, xp=?, xp_total=?, vida=?, vida_max=?, energia=? "
                "WHERE id=?", (p["nivel"], p["xp"], p["xp_total"], p["vida"], p["vida_max"],
                               p["energia"], p["id"]))
    con.commit()
    return subidos


def historico(con):
    """Evolução da personagem, da mais antiga para a mais recente."""
    p = obter(con)
    return con.execute("SELECT data, nivel, xp_total, evento FROM evolucao "
                       "WHERE personagem_id = ? ORDER BY id", (p["id"],)).fetchall()
