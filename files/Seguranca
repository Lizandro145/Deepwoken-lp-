"""Hashing de palavras-passe e validação de dados."""
import hashlib, hmac, os, re


class ErroUtilizador(Exception):
    pass


def gerar_hash(password, salt=None):
    salt = salt or os.urandom(16)
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000).hex(), salt.hex()


def verificar(password, hash_, salt):
    return hmac.compare_digest(gerar_hash(password, bytes.fromhex(salt))[0], hash_)


def validar(username=None, email=None, password=None):
    if username is not None and not re.fullmatch(r"[A-Za-z0-9_]{3,20}", username):
        raise ErroUtilizador("Username: 3-20 caracteres (letras, números, _).")
    if email is not None and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ErroUtilizador("Email inválido.")
    if password is not None and not re.fullmatch(r"(?=.*[A-Za-z])(?=.*\d).{8,}", password):
        raise ErroUtilizador("Palavra-passe: mínimo 8 caracteres, com letras e números.")