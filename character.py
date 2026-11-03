"""Personagem, experiência e evolução (Requisito 3.2)."""
from datetime import datetime
import Users
from classes import CLASSES, DINHEIRO_INICIAL, ENERGIA, SORTE_BASE, vida_max
from models import Personagem
from Security import ErroUtilizador, inteiro, validar


def _agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _registar_evolucao(con, p, evento, tipo, valor):
    con.execute("INSERT INTO evolucao (personagem_id, data, nivel, xp_total, evento, tipo, valor) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)", (p["id"], _agora(), p["nivel"], p["xp_total"], evento, tipo, valor))


def obter(con):
    """Personagem do utilizador com sessão iniciada (ou None)."""
    Users.verificar_sessao(con)  # também recusa quem foi bloqueado entretanto
    r = con.execute("SELECT * FROM personagens WHERE utilizador_id = ?", (Users.atual["id"],)).fetchone()
    return Personagem.de_linha(r) if r else None


def criar(con, nome, classe):
    if obter(con):
        raise ErroUtilizador("Já tens uma personagem.")
    validar(nome=nome or "")
    classe = next((c for c in CLASSES if c.lower() == (classe or "").strip().lower()), None)
    if classe is None:
        raise ErroUtilizador("Classe inválida: " + ", ".join(CLASSES))
    vida = vida_max(classe, 1)
    ataque, defesa = CLASSES[classe]["ataque"], CLASSES[classe]["defesa"]
    with con:  # tudo ou nada
        cur = con.execute(
            "INSERT INTO personagens (utilizador_id, nome, classe, nivel, xp, xp_total, vida, vida_max, "
            "energia, energia_max, dinheiro, ataque, defesa, sorte, criado_em) VALUES (?,?,?,1,0,0,?,?,?,?,?,?,?,?,?)",
            (Users.atual["id"], nome, classe, vida, vida, ENERGIA, ENERGIA,
             DINHEIRO_INICIAL, ataque, defesa, SORTE_BASE, _agora()))
        _registar_evolucao(con, {"id": cur.lastrowid, "nivel": 1, "xp_total": 0}, "Personagem criada", "criacao", 0)


def ganhar_xp(con, xp, motivo="Combate"):
    """Soma XP e sobe de nível sempre que atinge 200 x nível. Devolve níveis subidos."""
    xp = inteiro(xp)
    p = obter(con)
    if p is None:
        raise ErroUtilizador("Ainda não tens personagem.")
    nivel_antes = p.nivel
    niveis = p.ganhar_xp(xp)  # as regras estão no modelo; aqui só se guarda
    with con:  # tudo ou nada
        _registar_evolucao(con, {"id": p.id, "nivel": nivel_antes, "xp_total": p.xp_total}, f"+{xp} XP ({motivo})", "xp", xp)
        for n in niveis:
            _registar_evolucao(con, {"id": p.id, "nivel": n, "xp_total": p.xp_total}, f"Subiu para o nível {n}", "nivel", n)
        con.execute("UPDATE personagens SET nivel=?, xp=?, xp_total=?, vida=?, vida_max=?, energia=? WHERE id=?",
                    (p.nivel, p.xp, p.xp_total, p.vida, p.vida_max, p.energia, p.id))
    return len(niveis)


def historico(con):
    """Evolução da personagem, da mais antiga para a mais recente."""
    p = obter(con)
    if p is None:
        raise ErroUtilizador("Ainda não tens personagem.")
    return con.execute("SELECT data, nivel, xp_total, evento FROM evolucao "
                       "WHERE personagem_id = ? ORDER BY id", (p["id"],)).fetchall()


def estatisticas(con):
    """XP ganho e níveis subidos, somados na BD (só é possível porque o histórico tem campos separados)."""
    p = obter(con)
    if p is None:
        raise ErroUtilizador("Ainda não tens personagem.")
    r = {"xp": (0, 0), "nivel": (0, 0)}
    for l in con.execute("SELECT tipo, COUNT(*) AS n, SUM(valor) AS total FROM evolucao WHERE personagem_id = ? GROUP BY tipo", (p.id,)):
        r[l["tipo"]] = (l["n"], l["total"])
    return {"xp_ganho": r["xp"][1], "ganhos_de_xp": r["xp"][0], "niveis_subidos": r["nivel"][0]}
