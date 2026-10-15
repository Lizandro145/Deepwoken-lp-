import Users as u
from Db import ligar
from Security import ErroUtilizador

con = ligar(":memory:")
u.registar(con, "luis", "luis@exemplo.pt", "segredo123")
u.registar(con, "admin", "a@exemplo.pt", "admin12345", "Administrador")
try:
    u.registar(con, "LUIS", "x@exemplo.pt", "segredo123")
except ErroUtilizador as e:
    print("Duplicado bloqueado:", e)
u.iniciar_sessao(con, "luis", "segredo123")
u.alterar_password(con, "segredo123", "novaPass456")
u.alterar_dados(con, "luis", "luis@novo.pt")
u.terminar_sessao()
u.iniciar_sessao(con, "admin", "admin12345")
print("OK | admin:", u.e_admin())