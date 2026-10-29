"""Ranking (game.md, secção 8): nível, depois XP total, depois vitórias em combate."""
import character
from Security import ErroUtilizador


def _todos(con):
    linhas = con.execute(
        "SELECT p.id, p.nome AS personagem, u.username AS jogador, p.classe, p.nivel, p.xp_total, p.vitorias, "
        "(SELECT COUNT(*) FROM missoes_personagem m WHERE m.personagem_id = p.id AND m.estado = 'Concluída') AS missoes "
        "FROM personagens p JOIN utilizadores u ON u.id = p.utilizador_id "
        "ORDER BY p.nivel DESC, p.xp_total DESC, p.vitorias DESC, p.id").fetchall()
    return [dict(l, posicao=i) for i, l in enumerate(linhas, 1)]


def tabela(con, limite=10):
    return _todos(con)[:limite]


def posicao(con):
    """(posição da minha personagem, total de personagens)."""
    p = character.obter(con)
    if p is None:
        raise ErroUtilizador("Ainda não tens personagem.")
    todos = _todos(con)
    return next(l["posicao"] for l in todos if l["id"] == p["id"]), len(todos)