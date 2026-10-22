"""Menu de consola (Requisitos 3.1 e 3.2). Correr com: python main.py"""
import sys
from getpass import getpass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "files"))

import Users
import character
from classes import CLASSES, xp_necessario
from Db import ligar
from Security import ErroUtilizador


def pedir(texto):
    return input(texto + ": ").strip()


def registar(con):
    Users.registar(con, pedir("Username"), pedir("Email"), getpass("Palavra-passe: "))
    print("Conta criada.")


def criar_admin(con):
    Users.registar(con, pedir("Username"), pedir("Email"), getpass("Palavra-passe: "), "Administrador")
    print("Administrador criado.")


def criar_utilizador(con):
    Users.registar(con, pedir("Username"), pedir("Email"), getpass("Palavra-passe: "),
                   pedir("Tipo (Jogador/Administrador)"))
    print("Utilizador criado.")


def editar_utilizador(con):
    Users.editar_utilizador(con, pedir("Utilizador a editar"), pedir("Novo username"),
                            pedir("Novo email"), pedir("Novo tipo (Jogador/Administrador)"))
    print("Utilizador editado.")


def apagar_utilizador(con):
    nome = pedir("Utilizador a apagar")
    if pedir(f"Apagar '{nome}' e a sua personagem? Escreve SIM para confirmar") != "SIM":
        print("Cancelado.")
        return
    Users.apagar_utilizador(con, nome)
    print("Utilizador apagado.")


def minha_conta(con):
    u = Users.atual
    print(f"Username: {u['username']} | Email: {u['email']} | Tipo: {u['tipo']}")


def listar_utilizadores(con):
    for r in Users.listar(con):
        print(f"{r['id']} | {r['username']} | {r['email']} | {r['tipo']}")


def entrar(con):
    Users.iniciar_sessao(con, pedir("Username"), getpass("Palavra-passe: "))
    print("Sessão iniciada como", Users.atual["username"], f"({Users.atual['tipo']}).")


def ver_personagem(con):
    p = character.obter(con)
    if p is None:
        print("Ainda não tens personagem. Classes:", ", ".join(CLASSES))
        character.criar(con, pedir("Nome"), pedir("Classe"))
        p = character.obter(con)
    print(f"{p['nome']} ({p['classe']}) | nível {p['nivel']} | XP {p['xp']}/{xp_necessario(p['nivel'])}"
          f" | vida {p['vida']}/{p['vida_max']} | energia {p['energia']}/{p['energia_max']}"
          f" | dinheiro {p['dinheiro']} | ataque {p['ataque']} | defesa {p['defesa']}"
          f" | criada em {p['criado_em']}")


def evolucao(con):
    for h in character.historico(con):
        print(f"{h['data']} | nível {h['nivel']} | XP total {h['xp_total']} | {h['evento']}")


def ganhar_xp(con):
    try:
        xp = int(pedir("XP a ganhar"))
    except ValueError:
        raise ErroUtilizador("Escreve um número inteiro.")
    print("Níveis subidos:", character.ganhar_xp(con, xp, "Teste"))


def alterar_dados(con):
    Users.alterar_dados(con, pedir("Novo username"), pedir("Novo email"))
    print("Dados alterados.")


def alterar_password(con):
    Users.alterar_password(con, getpass("Palavra-passe atual: "), getpass("Nova palavra-passe: "))
    print("Palavra-passe alterada.")


def terminar(con):
    Users.terminar_sessao()
    print("Sessão terminada.")


def main():
    con = ligar()
    while True:
        if Users.atual is None:
            opcoes = {"1": ("Registar (Jogador)", registar), "2": ("Iniciar sessão", entrar),
                      "3": ("Registar Administrador (só o 1.º)", criar_admin)}
        else:
            opcoes = {"1": ("Personagem", ver_personagem), "2": ("Evolução da personagem", evolucao),
                      "3": ("Ganhar XP (teste)", ganhar_xp), "4": ("Alterar dados", alterar_dados),
                      "5": ("Alterar palavra-passe", alterar_password), "6": ("Terminar sessão", terminar),
                      "7": ("A minha conta", minha_conta)}
            if Users.e_admin():
                opcoes["8"] = ("[Admin] Criar utilizador", criar_utilizador)
                opcoes["9"] = ("[Admin] Listar utilizadores", listar_utilizadores)
                opcoes["10"] = ("[Admin] Editar utilizador", editar_utilizador)
                opcoes["11"] = ("[Admin] Apagar utilizador", apagar_utilizador)
        opcoes["0"] = ("Sair", None)
        print()
        for chave, (nome, _) in opcoes.items():
            print(f"{chave}. {nome}")
        escolha = input("> ").strip()
        if escolha == "0":
            break
        if escolha not in opcoes:
            print("Opção inválida.")
            continue
        try:
            opcoes[escolha][1](con)
        except ErroUtilizador as erro:
            print("Erro:", erro)


if __name__ == "__main__":
    main()