import Users as u
from Db import ligar
from Security import ErroUtilizador

con = ligar(":memory:")
u.registar(con, "luis", "luis@exemplo.pt", "segredo123")
u.registar(con, "admin", "a@exemplo.pt", "admin12345", "Administrador")  # 1.º admin: livre


def deve_falhar(texto, funcao, *args):
    try:
        funcao(*args)
    except ErroUtilizador as e:
        print(f"OK ({texto}):", e)
    else:
        raise AssertionError("Devia ter falhado: " + texto)


deve_falhar("username duplicado", u.registar, con, "LUIS", "x@exemplo.pt", "segredo123")
deve_falhar("password em falta", u.registar, con, "novo1", "a@b.pt", None)
deve_falhar("username em falta", u.registar, con, None, "a@b.pt", "segredo123")
deve_falhar("email duplicado", u.registar, con, "outro", "LUIS@exemplo.pt", "segredo123")
deve_falhar("tipo inválido", u.registar, con, "abc", "a@b.pt", "segredo123", "Hacker")
deve_falhar("jogador a criar admin", u.registar, con, "falso", "f@b.pt", "segredo123", "Administrador")
u.iniciar_sessao(con, "luis", "segredo123")
deve_falhar("jogador a criar admin com sessão", u.registar, con, "falso", "f@b.pt", "segredo123", "Administrador")
u.alterar_password(con, "segredo123", "novaPass456")
u.alterar_dados(con, "luis", "luis@novo.pt")
u.terminar_sessao()
u.iniciar_sessao(con, "admin", "admin12345")
u.registar(con, "admin2", "b@exemplo.pt", "admin12345", "Administrador")
print("OK | admin:", u.e_admin())

# --- poderes do administrador ---
u.editar_utilizador(con, "luis", "luis2", "l2@exemplo.pt", "Jogador")
deve_falhar("editar para username existente", u.editar_utilizador, con, "luis2", "admin", "l2@exemplo.pt", "Jogador")
deve_falhar("tipo inválido", u.editar_utilizador, con, "luis2", "luis2", "l2@exemplo.pt", "Rei")
deve_falhar("apagar a própria conta", u.apagar_utilizador, con, "admin")
deve_falhar("apagar quem não existe", u.apagar_utilizador, con, "fantasma")
u.apagar_utilizador(con, "luis2")
assert len(u.listar(con)) == 2  # admin e admin2
u.terminar_sessao()
u.iniciar_sessao(con, "admin2", "admin12345")
u.editar_utilizador(con, "admin", "admin", "a@exemplo.pt", "Jogador")  # admin2 despromove admin
deve_falhar("despromover o último admin", u.editar_utilizador, con, "admin2", "admin2", "b@exemplo.pt", "Jogador")
u.terminar_sessao()
u.iniciar_sessao(con, "admin", "admin12345")
deve_falhar("jogador a listar utilizadores", u.listar, con)
print("Poderes de administrador OK")
