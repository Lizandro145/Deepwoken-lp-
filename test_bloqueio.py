import character as c
import loja
import Users as u
from Db import ligar
from testes_comuns import falha, sql

con = ligar(":memory:")
u.registar(con, "admin", "a@exemplo.pt", "admin12345", "Administrador")
u.registar(con, "luis", "luis@exemplo.pt", "segredo123")
u.registar(con, "rui", "rui@exemplo.pt", "segredo123")

# só administradores bloqueiam, e nunca a própria conta
u.iniciar_sessao(con, "luis", "segredo123")
falha("jogador a bloquear", u.bloquear, con, "rui")
u.terminar_sessao(); u.iniciar_sessao(con, "admin", "admin12345")
falha("admin a bloquear-se a si próprio", u.bloquear, con, "admin")
falha("bloquear quem não existe", u.bloquear, con, "fantasma")
u.bloquear(con, "luis")
assert {r["username"]: r["bloqueado"] for r in u.listar(con)}["luis"] == "sim"
u.terminar_sessao()

# no login: palavra-passe certa -> diz que está bloqueada; errada -> mensagem genérica (não revela nada)
falha("login de conta bloqueada", u.iniciar_sessao, con, "luis", "segredo123")
falha("login bloqueado com password errada", u.iniciar_sessao, con, "luis", "errada123")
u.iniciar_sessao(con, "admin", "admin12345"); u.desbloquear(con, "luis"); u.terminar_sessao()
u.iniciar_sessao(con, "luis", "segredo123")  # já pode entrar

# sessão aberta e bloqueio feito entretanto (por outro administrador): a ação seguinte é recusada
c.criar(con, "Aldric", "Dawnwalker")
sql(con, "UPDATE utilizadores SET bloqueado = 1 WHERE username = 'luis'")
falha("ação com a sessão aberta depois do bloqueio", loja.comprar, con, "Wood", 1)
assert u.atual is None  # a sessão foi terminada

# direitos sempre atuais: um admin despromovido perde os poderes de imediato
sql(con, "UPDATE utilizadores SET bloqueado = 0 WHERE username = 'luis'")
u.iniciar_sessao(con, "admin", "admin12345")
sql(con, "UPDATE utilizadores SET tipo = 'Jogador' WHERE username = 'admin'")
falha("admin despromovido a listar", u.listar, con)
print("Testes de bloqueio passaram.")
