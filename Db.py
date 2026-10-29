"""Ligação à base de dados SQLite."""
import json
import sqlite3
from pathlib import Path

from dados import DADOS

# Fica sempre na pasta do projeto, não importa de onde o programa é corrido
CAMINHO = Path(__file__).resolve().parent.parent / "deepwoken.db"


def ligar(caminho=CAMINHO):
    con = sqlite3.connect(caminho)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
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
        dinheiro INTEGER NOT NULL CHECK (dinheiro >= 0),
        ataque INTEGER NOT NULL, defesa INTEGER NOT NULL,
        vitorias INTEGER NOT NULL DEFAULT 0,
        fuga_pendente INTEGER NOT NULL DEFAULT 0,
        criado_em TEXT NOT NULL);

    CREATE TABLE IF NOT EXISTS evolucao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        personagem_id INTEGER NOT NULL REFERENCES personagens(id),
        data TEXT NOT NULL, nivel INTEGER NOT NULL, xp_total INTEGER NOT NULL,
        evento TEXT NOT NULL);

    CREATE TABLE IF NOT EXISTS objetos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE COLLATE NOCASE,
        descricao TEXT NOT NULL, tipo TEXT NOT NULL,
        preco INTEGER NOT NULL CHECK (preco > 0),
        stock INTEGER NOT NULL CHECK (stock >= 0),
        efeitos TEXT NOT NULL, usavel INTEGER NOT NULL);

    CREATE TABLE IF NOT EXISTS inventario (
        personagem_id INTEGER NOT NULL REFERENCES personagens(id),
        objeto_id INTEGER NOT NULL REFERENCES objetos(id),
        quantidade INTEGER NOT NULL CHECK (quantidade > 0),
        PRIMARY KEY (personagem_id, objeto_id));

    CREATE TABLE IF NOT EXISTS inimigos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE COLLATE NOCASE,
        poder INTEGER NOT NULL,
        vida INTEGER NOT NULL CHECK (vida > 0),
        ataque INTEGER NOT NULL, defesa INTEGER NOT NULL,
        dinheiro INTEGER NOT NULL, xp INTEGER NOT NULL,
        critico INTEGER NOT NULL, fuga INTEGER NOT NULL);

    CREATE TABLE IF NOT EXISTS missoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE COLLATE NOCASE,
        inimigo_id INTEGER NOT NULL REFERENCES inimigos(id),
        quantidade INTEGER NOT NULL CHECK (quantidade > 0),
        dificuldade TEXT NOT NULL,
        dinheiro INTEGER NOT NULL, xp INTEGER NOT NULL);

    CREATE TABLE IF NOT EXISTS missoes_personagem (
        personagem_id INTEGER NOT NULL REFERENCES personagens(id),
        missao_id INTEGER NOT NULL REFERENCES missoes(id),
        estado TEXT NOT NULL CHECK (estado IN ('Ativa','Concluída','Falhada')),
        progresso INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (personagem_id, missao_id));
    """)
    colunas = {r[1] for r in con.execute("PRAGMA table_info(personagens)")}  # bases de dados antigas
    for coluna in ("vitorias", "fuga_pendente"):
        if coluna not in colunas:
            con.execute(f"ALTER TABLE personagens ADD COLUMN {coluna} INTEGER NOT NULL DEFAULT 0")
    for o in DADOS["objetos"]:  # só insere os que ainda não existem
        con.execute("INSERT OR IGNORE INTO objetos (nome, descricao, tipo, preco, stock, efeitos, usavel) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)", (o["nome"], o["descricao"], o["tipo"], o["preco"],
                                                     o["stock"], json.dumps(o["efeitos"]), int(o["usavel"])))
    for i in DADOS["inimigos"]:
        con.execute("INSERT OR IGNORE INTO inimigos (nome, poder, vida, ataque, defesa, dinheiro, xp, critico, fuga) "
                    "VALUES (:nome, :poder, :vida, :ataque, :defesa, :dinheiro, :xp, :critico, :fuga)", i)
    for m in DADOS["missoes"]:
        con.execute("INSERT OR IGNORE INTO missoes (nome, inimigo_id, quantidade, dificuldade, dinheiro, xp) "
                    "VALUES (:nome, (SELECT id FROM inimigos WHERE nome = :inimigo), :quantidade, :dificuldade, :dinheiro, :xp)", m)
    con.commit()
    return con