"""Combate por turnos (game.md, secção 6)."""
import json
import random
import character
import loja
import missoes
import Users
from dados import DADOS
from Security import ErroUtilizador, inteiro

C = DADOS["combate"]
rng = random.Random()  # nos testes troca-se por um gerador com semente


def listar_inimigos(con):
    return con.execute("SELECT nome, poder, vida, ataque, defesa, dinheiro, xp FROM inimigos ORDER BY poder").fetchall()


def _arma(con, pid):
    """Melhor arma do inventário: (ataque extra, peso, crítico extra)."""
    melhor = (0, C["desarmado"], 0)
    for r in con.execute("SELECT o.efeitos FROM inventario i JOIN objetos o ON o.id = i.objeto_id "
                         "WHERE i.personagem_id = ? AND o.tipo = 'Arma'", (pid,)):
        ef = json.loads(r[0])
        if ef["ataque"] > melhor[0]:
            melhor = (ef["ataque"], ef["peso"], ef.get("critico", 0))
    return melhor


def _golpe(ataque, defesa, variancia, critico, mult=1.0):
    """Dano = (ataque - defesa) x sorte, no mínimo 1. Devolve (dano, foi_crítico)."""
    crit = rng.random() * 100 < critico
    dano = (ataque - defesa) * rng.uniform(*variancia) * mult * (C["critico_mult"] if crit else 1)
    return max(1, round(dano)), crit


def iniciar(con, nome):
    p = character.obter(con)
    if p is None:
        raise ErroUtilizador("Ainda não tens personagem.")
    if p["vida"] < 1:
        raise ErroUtilizador("Precisas de pelo menos 1 de vida para combater.")
    ini = con.execute("SELECT * FROM inimigos WHERE nome = ? COLLATE NOCASE", (nome,)).fetchone()
    if ini is None:
        raise ErroUtilizador("Esse inimigo não existe.")
    with con:  # a penalização de uma fuga só vale para o combate seguinte
        con.execute("UPDATE personagens SET fuga_pendente = 0 WHERE id = ?", (p["id"],))
    return {"inimigo": dict(ini), "vida": ini["vida"], "penalizado": bool(p["fuga_pendente"]), "fim": None}


def turno(con, e, acao, item=None):
    """Um turno: o jogador age primeiro (atacar, item ou fugir) e depois o inimigo. Devolve as linhas do relato."""
    if e["fim"]:
        raise ErroUtilizador("O combate já terminou.")
    p, ini, log = character.obter(con), e["inimigo"], []
    if acao == "atacar":
        extra, peso, crit_arma = _arma(con, p["id"])
        regra = C["armas"][peso]
        mult = 1 - C["penalizacao_fuga"] if e["penalizado"] else 1
        dano, crit = _golpe(p["ataque"] + extra, ini["defesa"], regra["variancia"], regra["critico"] + crit_arma, mult)
        e["vida"] = max(0, e["vida"] - dano)
        energia = min(p["energia_max"], p["energia"] + C["ether_m1"])
        with con:
            con.execute("UPDATE personagens SET energia = ? WHERE id = ?", (energia, p["id"]))
        ganho = energia - p["energia"]
        log.append(f"Acertas em {ini['nome']} e causas {dano} de dano{' (CRÍTICO!)' if crit else ''}."
                   + (f" +{ganho} Ether." if ganho else ""))
    elif acao == "item":
        log.append(loja.usar(con, item, em_combate=True))
    elif acao == "fugir":
        chance = ini["fuga"] / (2 if e["penalizado"] else 1)
        if rng.random() * 100 < chance:
            with con:
                con.execute("UPDATE personagens SET fuga_pendente = 1 WHERE id = ?", (p["id"],))
            e["fim"] = "fuga"
            return ["Conseguiste fugir! No próximo combate causas -15% de dano e fugir fica mais difícil."]
        log.append("Não conseguiste fugir!")
    else:
        raise ErroUtilizador("Ação inválida.")
    if e["vida"] == 0:
        return log + _vitoria(con, e)
    p = character.obter(con)  # o item pode ter mudado a vida
    dano, crit = _golpe(ini["ataque"], p["defesa"], C["variancia_inimigo"], ini["critico"])
    vida = max(0, p["vida"] - dano)
    with con:
        con.execute("UPDATE personagens SET vida = ? WHERE id = ?", (vida, p["id"]))
    log.append(f"{ini['nome']} acerta-te e causa {dano} de dano{' (CRÍTICO!)' if crit else ''}.")
    return log + (_derrota(con, e) if vida == 0 else [])


def _vitoria(con, e):
    p, ini = character.obter(con), e["inimigo"]
    with con:  # tudo ou nada
        con.execute("UPDATE personagens SET dinheiro = dinheiro + ?, vitorias = vitorias + 1 WHERE id = ?",
                    (ini["dinheiro"], p["id"]))
        progresso, concluidas = missoes.registar_vitoria(con, p["id"], ini["nome"])
    e["fim"] = "vitoria"
    log = [f"Venceste {ini['nome']}! +{ini['dinheiro']} moedas e +{ini['xp']} XP."] + progresso
    subidos = character.ganhar_xp(con, ini["xp"], f"Vitória contra {ini['nome']}")
    for nome, dinheiro, xp in concluidas:
        log.append(f"MISSÃO CONCLUÍDA: {nome}! +{dinheiro} moedas e +{xp} XP.")
        subidos += character.ganhar_xp(con, xp, f"Missão {nome}")
    if subidos:
        log.append(f"Subiste {subidos} nível(eis)! Vida e energia restauradas.")
    return log


def _derrota(con, e):
    p = character.obter(con)
    perda = int(p["dinheiro"] * C["perda_derrota"])
    with con:
        con.execute("UPDATE personagens SET dinheiro = dinheiro - ?, vida = ? WHERE id = ?",
                    (perda, C["vida_respawn"], p["id"]))
        falhadas = missoes.falhar_ativas(con, p["id"])
    e["fim"] = "derrota"
    return [f"Foste derrotado! Perdes {perda} moedas e voltas à cidade com {C['vida_respawn']} de vida."
            + (f" Missões falhadas: {falhadas}." if falhadas else "")]


def alterar_inimigo(con, nome, vida, ataque, defesa):
    """Só administradores."""
    if not Users.e_admin():
        raise ErroUtilizador("Só administradores podem fazer isto.")
    ini = con.execute("SELECT id FROM inimigos WHERE nome = ? COLLATE NOCASE", (nome,)).fetchone()
    if ini is None:
        raise ErroUtilizador("Esse inimigo não existe.")
    with con:
        con.execute("UPDATE inimigos SET vida = ?, ataque = ?, defesa = ? WHERE id = ?",
                    (inteiro(vida), inteiro(ataque, 0), inteiro(defesa, 0), ini["id"]))
