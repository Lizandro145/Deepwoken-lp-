"""Ligação à base de dados SQLite."""
import json
import sqlite3
from pathlib import Path

from dados import DADOS

# Fica sempre na pasta do projeto, não importa de onde o programa é corrido
CAMINHO = Path(__file__).resolve().parent / "deepwoken.db"


def ligar(caminho=CAMINHO):
    con = sqlite3.connect(caminho)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript("""
    CREATE TABLE IF NOT EXISTS utilizadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE COLLATE NOCASE,
        email TEXT NOT NULL UNIQUE COLLATE NOCASE,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        bloqueado INTEGER NOT NULL DEFAULT 0,
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
        sorte INTEGER NOT NULL DEFAULT 0,
        vitorias INTEGER NOT NULL DEFAULT 0,
        fuga_pendente INTEGER NOT NULL DEFAULT 0,
        criado_em TEXT NOT NULL);

    CREATE TABLE IF NOT EXISTS evolucao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        personagem_id INTEGER NOT NULL REFERENCES personagens(id),
        data TEXT NOT NULL, nivel INTEGER NOT NULL, xp_total INTEGER NOT NULL,
        evento TEXT NOT NULL,
        tipo TEXT NOT NULL DEFAULT 'outro',   -- criacao | xp | nivel
        valor INTEGER NOT NULL DEFAULT 0);    -- XP ganho ou nível alcançado

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

    CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        personagem_id INTEGER NOT NULL REFERENCES personagens(id),
        objeto_id INTEGER NOT NULL REFERENCES objetos(id),
        tipo TEXT NOT NULL CHECK (tipo IN ('compra','venda')),
        quantidade INTEGER NOT NULL CHECK (quantidade > 0),
        preco_unitario INTEGER NOT NULL CHECK (preco_unitario >= 0),
        data TEXT NOT NULL);

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
    for tabela, novas in {"utilizadores": {"bloqueado": "INTEGER NOT NULL DEFAULT 0"},  # bases de dados antigas
                          "personagens": {"sorte": "INTEGER NOT NULL DEFAULT 0", "vitorias": "INTEGER NOT NULL DEFAULT 0",
                                          "fuga_pendente": "INTEGER NOT NULL DEFAULT 0"},
                          "evolucao": {"tipo": "TEXT NOT NULL DEFAULT 'outro'", "valor": "INTEGER NOT NULL DEFAULT 0"}}.items():
        existentes = {r[1] for r in con.execute(f"PRAGMA table_info({tabela})")}
        for coluna, definicao in novas.items():
            if coluna not in existentes:
                con.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}")
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
