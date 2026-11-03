# Deepwoken

Jogo de consola em Python + SQLite (Linguagens de Programação).

## Como correr
```
python main.py
```
O menu está no `menu.json`. A base de dados (`deepwoken.db`) é criada sozinha na pasta do projeto.
Para recomeçar do zero, apaga o `deepwoken.db`.

## Estrutura
| Ficheiro | Para que serve |
|---|---|
| `main.py` + `menu.json` | interface de consola (só pergunta e mostra) |
| `Db.py` | base de dados: liga, cria as 9 tabelas e insere os dados iniciais |
| `Security.py` | hashing de palavras-passe (PBKDF2) e validação de dados |
| `Users.py` | contas, sessão, bloqueio e gestão de utilizadores (req. 3.1) |
| `models.py` | classe `Personagem`: dados e regras da personagem (sem base de dados) |
| `character.py` + `classes.py` | criar personagem, XP, níveis e histórico (req. 3.2) |
| `loja.py` | loja, inventário, uso de objetos e registo de transações (req. 3.3) |
| `combate.py` | combate por turnos (ataque básico, itens, fuga, sorte) |
| `missoes.py` | missões: aceitar, progresso, recompensas e falhas |
| `Ranking.py` | ranking por nível, XP total e vitórias |
| `dados.json` | classes, objetos, inimigos, missões, regras do jogo/combate e validação |

## Testes
Na pasta do projeto, um a um (ou em PowerShell, todos de uma vez):
```
foreach ($t in "Testuser","test_validacao","test_models","test_character","test_loja","test_combate","test_missoes","test_bloqueio","test_aleatorio") { python "$t.py" }
```
`test_models.py` testa a classe `Personagem` sem base de dados. `test_aleatorio.py` faz centenas de ações ao calhas e confirma que as regras nunca são quebradas. `python demo.py` mostra o requisito 3.1 passo a passo.
