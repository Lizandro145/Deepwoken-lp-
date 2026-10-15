"""Ligação à base de dados SQLite."""
import sqlite3


def ligar(caminho="deepwoken.db"):
    con = sqlite3.connect(caminho)
    con.row_factory = sqlite3.Row
    con.executescript("""
    CREATE TABLE IF NOT EXISTS utilizadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE COLLATE NOCASE,
        email TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        tipo TEXT NOT NULL CHECK (tipo IN ('Jogador','Administrador')));

    CREATE TABLE IF NOT EXISTS personagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        utilizador_id INTEGER NOT NULL UNIQUE REFERENCES utilizadores(id),
        nome TEXT NOT NULL,
        classe TEXT NOT NULL,
        nivel INTEGER NOT NULL, xp INTEGER NOT NULL, xp_total INTEGER NOT NULL,
        vida INTEGER NOT NULL, vida_max INTEGER NOT NULL,
        energia INTEGER NOT NULL, energia_max INTEGER NOT NULL,
        dinheiro INTEGER NOT NULL,
        ataque INTEGER NOT NULL, defesa INTEGER NOT NULL,
        criado_em TEXT NOT NULL);

    CREATE TABLE IF NOT EXISTS evolucao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        personagem_id INTEGER NOT NULL REFERENCES personagens(id),
        data TEXT NOT NULL, nivel INTEGER NOT NULL, xp_total INTEGER NOT NULL,
        evento TEXT NOT NULL);
    """)
    return con