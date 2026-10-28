"""Demonstração passo a passo do requisito 3.1. Correr com: python demo.py"""
import Users as u
from Db import ligar
from Security import ErroUtilizador

con = ligar(":memory:")  # base de dados temporária (desaparece no fim)


def titulo(texto):
    print("\n" + "=" * 60 + "\n" + texto + "\n" + "=" * 60)


def tentar(descricao, funcao, *args):
    """Executa uma ação e mostra se funcionou ou se foi recusada."""
    try:
        funcao(*args)
        print(f"  [FUNCIONOU] {descricao}")
    except ErroUtilizador as erro:
        print(f"  [RECUSADO ] {descricao}\n              -> motivo: {erro}")


titulo("1. REGISTAR NOVOS UTILIZADORES")
tentar("registar 'luis' (Jogador)", u.registar, con, "luis", "luis@exemplo.pt", "segredo123")
linha = con.execute("SELECT username, tipo, password_hash FROM utilizadores").fetchone()
print(f"  Na base de dados ficou: username={linha['username']}, tipo={linha['tipo']}")
print(f"  password_hash={linha['password_hash'][:30]}...  (a palavra-passe 'segredo123' NÃO é guardada)")

titulo("2. IMPEDIR USERNAMES DUPLICADOS")
tentar("registar 'luis' outra vez", u.registar, con, "luis", "outro@exemplo.pt", "segredo123")
tentar("registar 'LUIS' (maiúsculas contam como igual)", u.registar, con, "LUIS", "outro@exemplo.pt", "segredo123")

titulo("3. VALIDAR OS DADOS INTRODUZIDOS")
tentar("username com símbolos ('a!')", u.registar, con, "a!", "a@exemplo.pt", "segredo123")
tentar("email sem @ ('semarroba')", u.registar, con, "maria", "semarroba", "segredo123")
tentar("palavra-passe curta ('abc')", u.registar, con, "maria", "m@exemplo.pt", "abc")
tentar("palavra-passe só letras ('abcdefghij')", u.registar, con, "maria", "m@exemplo.pt", "abcdefghij")
tentar("dados corretos para 'maria'", u.registar, con, "maria", "m@exemplo.pt", "maria12345")

titulo("4. INICIAR SESSÃO")
tentar("login com palavra-passe errada", u.iniciar_sessao, con, "luis", "errada123")
tentar("login com username que não existe", u.iniciar_sessao, con, "fantasma", "segredo123")
tentar("login correto (luis / segredo123)", u.iniciar_sessao, con, "luis", "segredo123")
print("  Sessão ativa de:", u.atual["username"])

titulo("5. ALTERAR DADOS DA CONTA")
tentar("mudar username para 'maria' (já existe)", u.alterar_dados, con, "maria", "luis@exemplo.pt")
tentar("mudar para 'luis_novo' e email novo", u.alterar_dados, con, "luis_novo", "novo@exemplo.pt")
print("  Agora a conta chama-se:", u.atual["username"], "|", u.atual["email"])

titulo("6. ALTERAR PALAVRA-PASSE")
tentar("trocar com a palavra-passe atual ERRADA", u.alterar_password, con, "xxxxx", "novaPass456")
tentar("nova palavra-passe fraca ('123')", u.alterar_password, con, "segredo123", "123")
tentar("trocar corretamente para 'novaPass456'", u.alterar_password, con, "segredo123", "novaPass456")

titulo("7. TERMINAR SESSÃO")
u.terminar_sessao()
print("  Sessão ativa agora:", u.atual)
tentar("alterar dados SEM sessão", u.alterar_dados, con, "luis_novo", "novo@exemplo.pt")
tentar("login com a palavra-passe ANTIGA", u.iniciar_sessao, con, "luis_novo", "segredo123")
tentar("login com a palavra-passe NOVA", u.iniciar_sessao, con, "luis_novo", "novaPass456")
u.terminar_sessao()

titulo("8. DOIS TIPOS DE UTILIZADOR: Jogador e Administrador")
tentar("registar o 1.º administrador 'admin'", u.registar, con, "admin", "a@exemplo.pt", "admin12345", "Administrador")
tentar("registar com tipo inventado ('Hacker')", u.registar, con, "x_x", "x@exemplo.pt", "segredo123", "Hacker")
u.iniciar_sessao(con, "luis_novo", "novaPass456")
print("  luis_novo é administrador?", u.e_admin())
tentar("jogador tenta criar um administrador", u.registar, con, "falso", "f@exemplo.pt", "segredo123", "Administrador")
u.terminar_sessao()
u.iniciar_sessao(con, "admin", "admin12345")
print("  admin é administrador?", u.e_admin())
tentar("admin cria outro administrador", u.registar, con, "admin2", "b@exemplo.pt", "admin12345", "Administrador")

titulo("RESUMO: utilizadores na base de dados")
for r in con.execute("SELECT id, username, email, tipo FROM utilizadores"):
    print(f"  {r['id']} | {r['username']:10} | {r['email']:18} | {r['tipo']}")
