"""Registo, sessão e gestão de contas (Requisito 3.1)."""
import sqlite3
from dados import DADOS
from Security import ErroUtilizador, gerar_hash, precisa_rehash, validar, verificar, verificar_falso

TIPOS = DADOS["tipos"]
atual = None  # {"id", "username", "email", "tipo"} do utilizador com sessão (ou None)


def _gravar(con, sql, args):
    try:
        con.execute(sql, args)
        con.commit()
    except sqlite3.IntegrityError as e:
        con.rollback()
        raise ErroUtilizador("Esse email já está registado." if "email" in str(e) else "Esse username já existe.") from None


def e_admin():
    return atual is not None and atual["tipo"] == "Administrador"


def verificar_sessao(con):
    """Confirma na BD que a sessão ainda é válida: a conta pode ter sido bloqueada, apagada ou despromovida."""
    global atual
    if atual is None:
        raise ErroUtilizador("É necessário iniciar sessão.")
    r = con.execute("SELECT username, email, tipo, bloqueado FROM utilizadores WHERE id = ?", (atual["id"],)).fetchone()
    if r is None or r["bloqueado"]:
        atual = None
        raise ErroUtilizador("A tua conta foi bloqueada ou removida. Sessão terminada.")
    atual.update(username=r["username"], email=r["email"], tipo=r["tipo"])  # direitos sempre atuais


def _exigir(con, admin=False):
    verificar_sessao(con)
    if admin and not e_admin():
        raise ErroUtilizador("Só administradores podem fazer isto.")


def exigir_admin(con):
    """Usado pelos outros serviços (loja, missões, combate) para proteger as ações de administrador."""
    _exigir(con, admin=True)


def _procurar(con, username):
    u = con.execute("SELECT * FROM utilizadores WHERE username = ?", (username,)).fetchone()
    if u is None:
        raise ErroUtilizador("Utilizador não encontrado.")
    return u


def _n_admins(con):
    return con.execute("SELECT COUNT(*) FROM utilizadores WHERE tipo = 'Administrador'").fetchone()[0]


# ---------- Qualquer utilizador ----------
def registar(con, username, email, password, tipo="Jogador"):
    """Só um administrador pode criar administradores (o primeiro é livre)."""
    if tipo not in TIPOS:
        raise ErroUtilizador("Tipo de utilizador inválido.")
    if tipo == "Administrador" and _n_admins(con) and not e_admin():
        raise ErroUtilizador("Só um administrador pode criar administradores.")
    validar(username=username, email=email, password=password)
    h, salt = gerar_hash(password)
    _gravar(con, "INSERT INTO utilizadores (username, email, password_hash, salt, tipo) "
                 "VALUES (?, ?, ?, ?, ?)", (username, email, h, salt, tipo))


def iniciar_sessao(con, username, password):
    global atual
    if not isinstance(username, str) or not isinstance(password, str):
        raise ErroUtilizador("Username ou palavra-passe incorretos.")
    u = con.execute("SELECT * FROM utilizadores WHERE username = ?", (username,)).fetchone()
    if not (verificar(password, u["password_hash"], u["salt"]) if u else verificar_falso(password)):
        raise ErroUtilizador("Username ou palavra-passe incorretos.")
    if u["bloqueado"]:  # só se diz depois de acertar na palavra-passe (não revela contas a quem não as conhece)
        raise ErroUtilizador("Esta conta está bloqueada. Fala com um administrador.")
    if precisa_rehash(u["password_hash"]):  # atualiza hashes feitos com menos iterações
        h, salt = gerar_hash(password)
        _gravar(con, "UPDATE utilizadores SET password_hash = ?, salt = ? WHERE id = ?", (h, salt, u["id"]))
    atual = {k: u[k] for k in ("id", "username", "email", "tipo")}


def terminar_sessao():
    global atual
    atual = None


def alterar_dados(con, username, email):
    _exigir(con)
    validar(username=username, email=email)
    _gravar(con, "UPDATE utilizadores SET username = ?, email = ? WHERE id = ?", (username, email, atual["id"]))
    atual.update(username=username, email=email)


def alterar_password(con, antiga, nova):
    _exigir(con)
    u = con.execute("SELECT password_hash, salt FROM utilizadores WHERE id = ?", (atual["id"],)).fetchone()
    if not isinstance(antiga, str) or not verificar(antiga, u["password_hash"], u["salt"]):
        raise ErroUtilizador("Palavra-passe atual incorreta.")
    validar(password=nova)
    h, salt = gerar_hash(nova)
    _gravar(con, "UPDATE utilizadores SET password_hash = ?, salt = ? WHERE id = ?", (h, salt, atual["id"]))


# ---------- Só administradores ----------
def listar(con):
    _exigir(con, admin=True)
    return con.execute("SELECT id, username, email, tipo, CASE WHEN bloqueado THEN 'sim' ELSE 'não' END AS bloqueado "
                       "FROM utilizadores ORDER BY id").fetchall()


def editar_utilizador(con, username, novo_username, novo_email, novo_tipo):
    _exigir(con, admin=True)
    u = _procurar(con, username)
    if novo_tipo not in TIPOS:
        raise ErroUtilizador("Tipo de utilizador inválido.")
    validar(username=novo_username, email=novo_email)
    if u["tipo"] == "Administrador" and novo_tipo != "Administrador" and _n_admins(con) == 1:
        raise ErroUtilizador("Não podes remover o último administrador.")
    _gravar(con, "UPDATE utilizadores SET username = ?, email = ?, tipo = ? WHERE id = ?",
            (novo_username, novo_email, novo_tipo, u["id"]))
    if u["id"] == atual["id"]:
        atual.update(username=novo_username, email=novo_email, tipo=novo_tipo)


def apagar_utilizador(con, username):
    """Apaga a conta, a personagem, o histórico, o inventário e as missões dela."""
    _exigir(con, admin=True)
    u = _procurar(con, username)
    if u["id"] == atual["id"]:
        raise ErroUtilizador("Não podes apagar a tua própria conta.")
    with con:  # tudo ou nada
        for sql in ("DELETE FROM evolucao WHERE personagem_id IN (SELECT id FROM personagens WHERE utilizador_id = ?)",
                    "DELETE FROM transacoes WHERE personagem_id IN (SELECT id FROM personagens WHERE utilizador_id = ?)",
                    "DELETE FROM inventario WHERE personagem_id IN (SELECT id FROM personagens WHERE utilizador_id = ?)",
                    "DELETE FROM missoes_personagem WHERE personagem_id IN (SELECT id FROM personagens WHERE utilizador_id = ?)",
                    "DELETE FROM personagens WHERE utilizador_id = ?", "DELETE FROM utilizadores WHERE id = ?"):
            con.execute(sql, (u["id"],))


def _definir_bloqueio(con, username, bloqueado):
    _exigir(con, admin=True)
    u = _procurar(con, username)
    if bloqueado and u["id"] == atual["id"]:
        raise ErroUtilizador("Não podes bloquear a tua própria conta.")
    with con:
        con.execute("UPDATE utilizadores SET bloqueado = ? WHERE id = ?", (int(bloqueado), u["id"]))


def bloquear(con, username):
    """Só administradores. Quem tiver sessão aberta é expulso na ação seguinte (ver verificar_sessao)."""
    _definir_bloqueio(con, username, True)


def desbloquear(con, username):
    _definir_bloqueio(con, username, False)
