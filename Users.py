"""Registo, sessão e gestão de utilizadores (Requisito 3.1)."""
import sqlite3

from Security import (ErroUtilizador, gerar_hash, precisa_rehash, validar,
                      verificar, verificar_falso)

TIPOS = ("Jogador", "Administrador")
atual = None  # {"id", "username", "email", "tipo"} do utilizador com sessão (ou None)

ESQUEMA = """
CREATE TABLE IF NOT EXISTS utilizadores (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE COLLATE NOCASE,
    email         TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    salt          TEXT NOT NULL,
    tipo          TEXT NOT NULL CHECK (tipo IN ('Jogador', 'Administrador'))
);
CREATE TABLE IF NOT EXISTS pontuacoes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    utilizador_id INTEGER NOT NULL REFERENCES utilizadores(id) ON DELETE CASCADE,
    pontos        INTEGER NOT NULL CHECK (pontos >= 0),
    data          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_pontuacoes_utilizador ON pontuacoes(utilizador_id);
"""


def ligar(caminho="jogo.db"):
    """Abre a BD (com Row e chaves estrangeiras ativas) e cria as tabelas se faltarem."""
    con = sqlite3.connect(caminho)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(ESQUEMA)
    return con


# ---------- auxiliares ----------

def _guardar(con, sql, args):
    try:
        con.execute(sql, args)
        con.commit()
    except sqlite3.IntegrityError as e:
        con.rollback()
        msg = "Esse email já está registado." if "email" in str(e) else "Esse username já existe."
        raise ErroUtilizador(msg) from None


def e_admin():
    return atual is not None and atual["tipo"] == "Administrador"


def _exigir_sessao():
    if atual is None:
        raise ErroUtilizador("É necessário iniciar sessão.")


def _exigir_admin():
    if not e_admin():
        raise ErroUtilizador("Só administradores podem fazer isto.")


def _n_admins(con):
    return con.execute("SELECT COUNT(*) FROM utilizadores WHERE tipo = 'Administrador'").fetchone()[0]


def _obter(con, id_):
    u = con.execute("SELECT id, username, email, tipo FROM utilizadores WHERE id = ?", (id_,)).fetchone()
    if u is None:
        raise ErroUtilizador("Utilizador não encontrado.")
    return u


# ---------- registo e sessão ----------

def registar(con, username, email, password, tipo="Jogador"):
    """Cria conta. Só um administrador pode criar outros (o primeiro é livre)."""
    if tipo not in TIPOS:
        raise ErroUtilizador("Tipo de utilizador inválido.")
    if tipo == "Administrador" and not e_admin() and _n_admins(con) > 0:
        raise ErroUtilizador("Só um administrador pode criar administradores.")
    validar(username=username, email=email, password=password)
    h, salt = gerar_hash(password)
    _guardar(con, "INSERT INTO utilizadores (username, email, password_hash, salt, tipo) "
                  "VALUES (?, ?, ?, ?, ?)", (username, email, h, salt, tipo))


def iniciar_sessao(con, username, password):
    global atual
    if not isinstance(username, str) or not isinstance(password, str):
        raise ErroUtilizador("Username ou palavra-passe incorretos.")
    u = con.execute("SELECT * FROM utilizadores WHERE username = ?", (username,)).fetchone()
    ok = verificar(password, u["password_hash"], u["salt"]) if u else verificar_falso(password)
    if not ok:
        raise ErroUtilizador("Username ou palavra-passe incorretos.")
    if precisa_rehash(u["password_hash"]):  # atualiza hashes feitos com menos iterações
        h, salt = gerar_hash(password)
        _guardar(con, "UPDATE utilizadores SET password_hash = ?, salt = ? WHERE id = ?",
                 (h, salt, u["id"]))
    atual = {k: u[k] for k in ("id", "username", "email", "tipo")}


def terminar_sessao():
    global atual
    atual = None


# ---------- o próprio utilizador ----------

def alterar_dados(con, username, email):
    _exigir_sessao()
    validar(username=username, email=email)
    _guardar(con, "UPDATE utilizadores SET username = ?, email = ? WHERE id = ?",
             (username, email, atual["id"]))
    atual.update(username=username, email=email)


def alterar_password(con, antiga, nova):
    _exigir_sessao()
    u = con.execute("SELECT password_hash, salt FROM utilizadores WHERE id = ?",
                    (atual["id"],)).fetchone()
    if not isinstance(antiga, str) or not verificar(antiga, u["password_hash"], u["salt"]):
        raise ErroUtilizador("Palavra-passe atual incorreta.")
    validar(password=nova)
    h, salt = gerar_hash(nova)
    _guardar(con, "UPDATE utilizadores SET password_hash = ?, salt = ? WHERE id = ?",
             (h, salt, atual["id"]))


# ---------- administração ----------

def listar(con):
    """Lista todas as contas (só administradores)."""
    _exigir_admin()
    return con.execute("SELECT id, username, email, tipo FROM utilizadores ORDER BY id").fetchall()


def editar_utilizador(con, id_alvo, username, email, tipo=None):
    """Um administrador edita qualquer conta (substitui o 'editar_utilizador' em falta no main.py)."""
    _exigir_admin()
    alvo = _obter(con, id_alvo)
    tipo = tipo or alvo["tipo"]
    if tipo not in TIPOS:
        raise ErroUtilizador("Tipo de utilizador inválido.")
    if alvo["tipo"] == "Administrador" and tipo != "Administrador" and _n_admins(con) <= 1:
        raise ErroUtilizador("Não podes retirar o último administrador.")
    validar(username=username, email=email)
    _guardar(con, "UPDATE utilizadores SET username = ?, email = ?, tipo = ? WHERE id = ?",
             (username, email, tipo, id_alvo))
    if id_alvo == atual["id"]:
        atual.update(username=username, email=email, tipo=tipo)


def remover_utilizador(con, id_alvo):
    """Apaga uma conta e as respetivas pontuações (ON DELETE CASCADE)."""
    _exigir_admin()
    alvo = _obter(con, id_alvo)
    if id_alvo == atual["id"]:
        raise ErroUtilizador("Não podes apagar a tua própria conta.")
    if alvo["tipo"] == "Administrador" and _n_admins(con) <= 1:
        raise ErroUtilizador("Não podes apagar o último administrador.")
    con.execute("DELETE FROM utilizadores WHERE id = ?", (id_alvo,))
    con.commit()