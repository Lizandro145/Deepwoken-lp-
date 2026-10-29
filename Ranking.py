"""Sistema de ranking: pontuações dos jogadores e tabela de classificação."""
import Users
from Security import ErroUtilizador, inteiro

MAX_PONTOS = 1_000_000

# Critérios permitidos (lista fixa -> nunca se mete texto do utilizador no SQL)
CRITERIOS = {
    "melhor": "MAX(p.pontos)",   # melhor pontuação individual
    "total": "SUM(p.pontos)",    # soma de todas as pontuações
}


def registar_pontuacao(con, pontos):
    """Guarda uma pontuação para o utilizador com sessão iniciada."""
    Users._exigir_sessao()
    pontos = inteiro(pontos, minimo=0, maximo=MAX_PONTOS)
    con.execute("INSERT INTO pontuacoes (utilizador_id, pontos) VALUES (?, ?)",
                (Users.atual["id"], pontos))
    con.commit()
    return pontos


def _classificacao(criterio):
    if criterio not in CRITERIOS:
        raise ErroUtilizador("Critério inválido. Usa: " + ", ".join(CRITERIOS) + ".")
    # RANK(): empates partilham a posição (1, 2, 2, 4...)
    return f"""
        SELECT RANK() OVER (ORDER BY valor DESC) AS posicao,
               id, username, valor, jogos
        FROM (SELECT u.id, u.username, {CRITERIOS[criterio]} AS valor, COUNT(*) AS jogos
              FROM pontuacoes p JOIN utilizadores u ON u.id = p.utilizador_id
              WHERE u.tipo = 'Jogador'
              GROUP BY u.id)
    """


def top(con, limite=10, criterio="melhor"):
    """Tabela de classificação: lista de linhas (posicao, username, valor, jogos)."""
    limite = inteiro(limite, 1, 100)
    return con.execute(_classificacao(criterio) + " ORDER BY posicao, username LIMIT ?",
                       (limite,)).fetchall()


def posicao_de(con, utilizador_id, criterio="melhor"):
    """Linha do jogador na classificação, ou None se ainda não tem pontuações."""
    return con.execute("SELECT * FROM (" + _classificacao(criterio) + ") WHERE id = ?",
                       (utilizador_id,)).fetchone()


def minhas_pontuacoes(con, limite=10):
    """Últimas pontuações do utilizador com sessão iniciada."""
    Users._exigir_sessao()
    return con.execute("SELECT pontos, data FROM pontuacoes WHERE utilizador_id = ? "
                       "ORDER BY id DESC LIMIT ?",
                       (Users.atual["id"], inteiro(limite, 1, 100))).fetchall()


def limpar_ranking(con):
    """Apaga todas as pontuações (só administradores)."""
    Users._exigir_admin()
    con.execute("DELETE FROM pontuacoes")
    con.commit()


def formatar(linhas):
    """Texto pronto a imprimir."""
    if not linhas:
        return "Ainda não há pontuações."
    out = [f"{'#':>3}  {'Jogador':<20} {'Pontos':>10} {'Jogos':>6}"]
    out += [f"{r['posicao']:>3}  {r['username']:<20} {r['valor']:>10} {r['jogos']:>6}" for r in linhas]
    return "\n".join(out)
