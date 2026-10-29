"""Hashing de palavras-passe e validação de dados (regras no dados.json)."""
import hashlib
import hmac
import os
import re

from dados import DADOS


class ErroUtilizador(Exception):
    pass


def _pbkdf2(password, salt, iteracoes):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iteracoes).hex()


def gerar_hash(password, salt=None, iteracoes=None):
    """Devolve (hash, salt). O hash guarda o nº de iterações: '<iter>$<hex>'."""
    salt = salt or os.urandom(16)
    iteracoes = iteracoes or DADOS["seguranca"]["iteracoes"]
    return f"{iteracoes}${_pbkdf2(password, salt, iteracoes)}", salt.hex()


def _separar(hash_):
    """'600000$abc' -> (600000, 'abc'). Hashes antigos (sem '$') usam o valor atual."""
    iter_txt, sep, h = hash_.rpartition("$")
    return (int(iter_txt) if sep else DADOS["seguranca"]["iteracoes"]), h


def verificar(password, hash_, salt):
    iteracoes, h = _separar(hash_)
    return hmac.compare_digest(_pbkdf2(password, bytes.fromhex(salt), iteracoes), h)


def precisa_rehash(hash_):
    """True se o hash foi feito com menos iterações do que as configuradas agora."""
    return _separar(hash_)[0] < DADOS["seguranca"]["iteracoes"]


_HASH_FALSO, _SALT_FALSO = gerar_hash("palavra-passe-falsa")


def verificar_falso(password):
    """Gasta o mesmo tempo de uma verificação real (evita descobrir usernames pelo tempo)."""
    verificar(password, _HASH_FALSO, _SALT_FALSO)
    return False


def validar(**campos):
    """Ex.: validar(username="ana", email="a@b.pt"). Valor que não seja texto é recusado."""
    for nome, valor in campos.items():
        regra = DADOS["validacao"][nome]
        if not isinstance(valor, str) or not re.fullmatch(regra["regex"], valor):
            raise ErroUtilizador(regra["erro"])


def inteiro(valor, minimo=1, maximo=1_000_000_000):
    """Converte para inteiro. Recusa texto, decimais, '1_000' e números fora dos limites."""
    texto = str(valor).strip()
    if not re.fullmatch(r"[+-]?\d+", texto) or not minimo <= int(texto) <= maximo:
        raise ErroUtilizador(f"Escreve um número inteiro entre {minimo} e {maximo}.")
    return int(texto)