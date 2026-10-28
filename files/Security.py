"""Hashing de palavras-passe e validação de dados (regras no dados.json)."""
import hashlib, hmac, os, re
from dados import DADOS


class ErroUtilizador(Exception):
    pass


def gerar_hash(password, salt=None):
    salt = salt or os.urandom(16)
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, DADOS["seguranca"]["iteracoes"]).hex(), salt.hex()


def verificar(password, hash_, salt):
    return hmac.compare_digest(gerar_hash(password, bytes.fromhex(salt))[0], hash_)


def validar(**campos):
    """Ex.: validar(username="ana", email="a@b.pt"). Valor que não seja texto também é recusado."""
    for nome, valor in campos.items():
        regra = DADOS["validacao"][nome]
        if not isinstance(valor, str) or not re.fullmatch(regra["regex"], valor):
            raise ErroUtilizador(regra["erro"])


def inteiro(valor, minimo=1, maximo=1_000_000_000):
    """Converte para inteiro. Recusa texto, decimais e números fora dos limites."""
    try:
        n = int(str(valor).strip())
    except ValueError:
        n = None
    if n is None or not minimo <= n <= maximo:
        raise ErroUtilizador(f"Escreve um número inteiro entre {minimo} e {maximo}.")
    return n