"""Ligação à base de dados SQLite."""
import sqlite3
 
 
def ligar(caminho="deepwoken.db"):
    con = sqlite3.connect(caminho)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS utilizadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE COLLATE NOCASE,
        email TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        tipo TEXT NOT NULL CHECK (tipo IN ('Jogador','Administrador')))""")
    return con