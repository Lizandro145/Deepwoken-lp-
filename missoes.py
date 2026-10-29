"""Missões (game.md, secção 7). Estados: Disponível, Ativa, Concluída, Falhada."""
import character
import Users
from dados import DADOS
from Security import ErroUtilizador, inteiro

MAX_ATIVAS = DADOS["regras"]["missoes_ativas_max"]


def _personagem(con):
    p = character.obter(con)
    if p is None:
        raise ErroUtilizador("Ainda não tens personagem.")
    return p


def _missao(con, nome):
    m = con.execute("SELECT * FROM missoes WHERE nome = ? COLLATE NOCASE", (nome,)).fetchone()
    if m is None:
        raise ErroUtilizador("Essa missão não existe.")
    return m


def listar(con):
    """Todas as missões, com o estado e o progresso da personagem."""
    return con.execute(
        "SELECT m.nome, 'Derrotar ' || m.quantidade || 'x ' || i.nome AS objetivo, m.dificuldade, m.dinheiro, m.xp, "
        "COALESCE(mp.estado, 'Disponível') AS estado, "
        "CASE WHEN mp.estado = 'Ativa' THEN 'Ativa (' || mp.progresso || '/' || m.quantidade || ')' "
        "ELSE COALESCE(mp.estado, 'Disponível') END AS estado_txt "
        "FROM missoes m JOIN inimigos i ON i.id = m.inimigo_id "
        "LEFT JOIN missoes_personagem mp ON mp.missao_id = m.id AND mp.personagem_id = ? ORDER BY m.xp",
        (_personagem(con)["id"],)).fetchall()


def aceitar(con, nome):
    p, m = _personagem(con), _missao(con, nome)
    r = con.execute("SELECT estado FROM missoes_personagem WHERE personagem_id = ? AND missao_id = ?",
                    (p["id"], m["id"])).fetchone()
    if r and r["estado"] == "Ativa":
        raise ErroUtilizador("Já tens essa missão ativa.")
    if r and r["estado"] == "Concluída":
        raise ErroUtilizador("Já concluíste essa missão.")
    ativas = con.execute("SELECT COUNT(*) FROM missoes_personagem WHERE personagem_id = ? AND estado = 'Ativa'",
                         (p["id"],)).fetchone()[0]
    if ativas >= MAX_ATIVAS:
        raise ErroUtilizador(f"Só podes ter {MAX_ATIVAS} missões ativas ao mesmo tempo.")
    with con:  # uma missão falhada pode ser aceite outra vez
        con.execute("INSERT INTO missoes_personagem (personagem_id, missao_id, estado, progresso) VALUES (?, ?, 'Ativa', 0) "
                    "ON CONFLICT (personagem_id, missao_id) DO UPDATE SET estado = 'Ativa', progresso = 0",
                    (p["id"], m["id"]))
    return f"Missão aceite: {m['nome']}."


def registar_vitoria(con, pid, inimigo):
    """Chamado pelo combate (sem commit). Devolve (linhas de progresso, missões concluídas)."""
    alvo = "m.inimigo_id = (SELECT id FROM inimigos WHERE nome = ?)"
    con.execute("UPDATE missoes_personagem SET progresso = progresso + 1 WHERE personagem_id = ? AND estado = 'Ativa' "
                f"AND missao_id IN (SELECT m.id FROM missoes m WHERE {alvo})", (pid, inimigo))
    ativas = con.execute("SELECT m.id, m.nome, m.quantidade, m.dinheiro, m.xp, mp.progresso FROM missoes_personagem mp "
                         f"JOIN missoes m ON m.id = mp.missao_id WHERE mp.personagem_id = ? AND mp.estado = 'Ativa' AND {alvo}",
                         (pid, inimigo)).fetchall()
    progresso, concluidas = [], []
    for m in ativas:
        if m["progresso"] < m["quantidade"]:
            progresso.append(f"Missão {m['nome']}: {m['progresso']}/{m['quantidade']}")
            continue
        con.execute("UPDATE missoes_personagem SET estado = 'Concluída' WHERE personagem_id = ? AND missao_id = ?",
                    (pid, m["id"]))
        con.execute("UPDATE personagens SET dinheiro = dinheiro + ? WHERE id = ?", (m["dinheiro"], pid))
        concluidas.append((m["nome"], m["dinheiro"], m["xp"]))
    return progresso, concluidas


def falhar_ativas(con, pid):
    """Chamado pelo combate quando a personagem é derrotada (sem commit). Devolve quantas falharam."""
    return con.execute("UPDATE missoes_personagem SET estado = 'Falhada' WHERE personagem_id = ? AND estado = 'Ativa'",
                       (pid,)).rowcount


def alterar_missao(con, nome, quantidade, dinheiro, xp):
    """Só administradores."""
    if not Users.e_admin():
        raise ErroUtilizador("Só administradores podem fazer isto.")
    m = _missao(con, nome)
    with con:
        con.execute("UPDATE missoes SET quantidade = ?, dinheiro = ?, xp = ? WHERE id = ?",
                    (inteiro(quantidade), inteiro(dinheiro, 0), inteiro(xp, 0), m["id"]))
