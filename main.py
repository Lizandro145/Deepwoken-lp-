"""Menu de consola (Requisitos 3.1 a 3.6). O menu está no menu.json. Correr: python main.py"""
import json
import sys
from getpass import getpass
from pathlib import Path

PASTA = Path(__file__).parent
sys.path.insert(0, str(PASTA / "files"))

import Users
import character
import combate
import loja
import missoes
import Ranking
from classes import CLASSES, xp_necessario
from dados import DADOS
from Db import ligar
from Security import ErroUtilizador

MENU = json.loads((PASTA / "menu.json").read_text(encoding="utf-8"))
TEXTOS = {"tipos_objeto": ", ".join(dict.fromkeys(o["tipo"] for o in DADOS["objetos"])),
          "tipos_utilizador": "/".join(DADOS["tipos"]),
          "inimigos": ", ".join(i["nome"] for i in DADOS["inimigos"])}  # preenchem os {…} do menu.json


def entrar(con, username, password):
    Users.iniciar_sessao(con, username, password)
    return f"Sessão iniciada como {Users.atual['username']} ({Users.atual['tipo']})."


def personagem(con):
    if character.obter(con) is None:
        print("Classes:", ", ".join(CLASSES))
        character.criar(con, input("Nome: ").strip(), input("Classe: ").strip())
    p = character.obter(con)
    return (f"{p['nome']} ({p['classe']}) | nível {p['nivel']} | XP {p['xp']}/{xp_necessario(p['nivel'])}"
            f" | vida {p['vida']}/{p['vida_max']} | energia {p['energia']}/{p['energia_max']}"
            f" | dinheiro {p['dinheiro']} | ataque {p['ataque']} | defesa {p['defesa']} | vitórias {p['vitorias']}"
            f" | criada em {p['criado_em']}")


def apagar(con, username, confirmacao):
    if confirmacao != "SIM":
        return "Cancelado."
    Users.apagar_utilizador(con, username)
    return "Utilizador apagado."


def tabela(linhas, *campos):
    corpo = [" | ".join(str(l[c]) for c in campos) for l in linhas]
    return "\n".join([" | ".join(campos)] + corpo) if corpo else ""


def lutar(con, nome):
    e = combate.iniciar(con, nome)
    print(f"Combate contra {e['inimigo']['nome']}!" + (" (Fugiste no combate anterior: -15% de dano e fugir é mais difícil.)" if e["penalizado"] else ""))
    while not e["fim"]:
        p = character.obter(con)
        print(f"\n{e['inimigo']['nome']}: {e['vida']}/{e['inimigo']['vida']} HP | Tu: vida {p['vida']}/{p['vida_max']}, energia {p['energia']}/{p['energia_max']}")
        acao = {"1": "atacar", "2": "item", "3": "fugir"}.get(input("1 Ataque básico (M1) | 2 Usar item | 3 Fugir > ").strip())
        if acao is None:
            print("Opção inválida.")
            continue
        try:
            print("\n".join(combate.turno(con, e, acao, input("Item: ").strip() if acao == "item" else None)))
        except ErroUtilizador as erro:
            print("Erro:", erro)
    return "Fim do combate."


# nome da ação no menu.json -> função (recebe a conexão e as respostas às perguntas)
ACOES = {
    "registar": Users.registar,
    "registar_admin": lambda con, *r: Users.registar(con, *r, "Administrador"),
    "entrar": entrar,
    "terminar": lambda con: Users.terminar_sessao(),
    "personagem": personagem,
    "evolucao": lambda con: tabela(character.historico(con), "data", "nivel", "xp_total", "evento"),
    "ganhar_xp": lambda con, xp: f"Níveis subidos: {character.ganhar_xp(con, xp, 'Teste')}",
    "inimigos": lambda con: tabela(combate.listar_inimigos(con), "nome", "poder", "vida", "ataque", "defesa", "dinheiro", "xp"),
    "combate": lutar,
    "missoes": lambda con: tabela(missoes.listar(con), "nome", "objetivo", "dificuldade", "dinheiro", "xp", "estado_txt"),
    "aceitar_missao": missoes.aceitar,
    "ranking": lambda con: tabela(Ranking.tabela(con), "posicao", "personagem", "jogador", "classe", "nivel", "xp_total", "vitorias", "missoes"),
    "posicao": lambda con: "Estás em %d.º lugar entre %d personagem(ns)." % Ranking.posicao(con),
    "alterar_missao": missoes.alterar_missao,
    "alterar_inimigo": combate.alterar_inimigo,
    "loja": lambda con, tipo: tabela(loja.listar_loja(con, tipo), "nome", "tipo", "preco", "stock", "descricao") or "Sem resultados.",
    "comprar": lambda con, nome, n: f"Compraste {n}x {nome} por {loja.comprar(con, nome, n)} moedas.",
    "vender": lambda con, nome, n: f"Vendeste {n}x {nome} e recebeste {loja.vender(con, nome, n)} moedas.",
    "inventario": lambda con: tabela(loja.inventario(con), "nome", "tipo", "quantidade", "descricao") or "Inventário vazio.",
    "usar": loja.usar,
    "quantidade": lambda con, nome: "%s: %d na loja | %d no teu inventário" % ((nome,) + loja.quantidade(con, nome)),
    "alterar_loja": loja.alterar_loja,
    "alterar_dados": Users.alterar_dados,
    "alterar_password": Users.alterar_password,
    "minha_conta": lambda con: tabela([Users.atual], "username", "email", "tipo"),
    "listar": lambda con: tabela(Users.listar(con), "id", "username", "email", "tipo"),
    "editar_utilizador": Users.editar_utilizador,
    "apagar": apagar,
}


def main():
    con = ligar()
    while True:
        menu = MENU["visitante"] if Users.atual is None else MENU["jogador"] + (MENU["admin"] if Users.e_admin() else [])
        print()
        for numero, o in enumerate(menu, 1):
            print(f"{numero}. {o['texto']}")
        print("0. Sair")
        escolha = input("> ").strip()
        if escolha == "0":
            break
        if not escolha.isdigit() or not 1 <= int(escolha) <= len(menu):
            print("Opção inválida.")
            continue
        o = menu[int(escolha) - 1]
        try:
            perguntas = [p.format(**TEXTOS) for p in o["perguntas"]]
            respostas = [getpass(p[1:] + ": ") if p[0] == "*" else input(p + ": ").strip() for p in perguntas]
            print(ACOES[o["acao"]](con, *respostas) or o.get("ok", ""))
        except ErroUtilizador as erro:
            print("Erro:", erro)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):  # Ctrl+C / Ctrl+D
        print("\nAté já!")