"""Registo e sessão (Requisito 3.1)."""
import sqlite3
from Security import ErroUtilizador, gerar_hash, verificar, validar

atual = None  # utilizador com sessão iniciada (ou None)


def _guardar(con, sql, args):
    try:
        con.execute(sql, args)
        con.commit()
    except sqlite3.IntegrityError:
        raise ErroUtilizador("Esse username já existe.")


def _exigir_sessao():
    if atual is None:
        raise ErroUtilizador("É necessário iniciar sessão.")


def registar(con, username, email, password, tipo="Jogador"):
    validar(username, email, password)
    h, salt = gerar_hash(password)
    _guardar(con, "INSERT INTO utilizadores (username, email, password_hash, salt, tipo) "
                  "VALUES (?, ?, ?, ?, ?)", (username, email, h, salt, tipo))


def iniciar_sessao(con, username, password):
    global atual
    u = con.execute("SELECT * FROM utilizadores WHERE username = ?", (username,)).fetchone()
    if u is None or not verificar(password, u["password_hash"], u["salt"]):
        raise ErroUtilizador("Username ou palavra-passe incorretos.")
    atual = dict(u)


def terminar_sessao():
    global atual
    atual = None


def alterar_dados(con, username, email):
    _exigir_sessao()
    validar(username, email)
    _guardar(con, "UPDATE utilizadores SET username = ?, email = ? WHERE id = ?",
             (username, email, atual["id"]))
    atual.update(username=username, email=email)


def alterar_password(con, antiga, nova):
    _exigir_sessao()
    if not verificar(antiga, atual["password_hash"], atual["salt"]):
        raise ErroUtilizador("Palavra-passe atual incorreta.")
    validar(password=nova)
    h, salt = gerar_hash(nova)
    _guardar(con, "UPDATE utilizadores SET password_hash = ?, salt = ? WHERE id = ?",
             (h, salt, atual["id"]))
    atual.update(password_hash=h, salt=salt)


def e_admin():
    return atual is not None and atual["tipo"] == "Administrador"