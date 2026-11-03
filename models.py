"""Modelo da personagem: os dados e as regras que só dependem dela (sem base de dados)."""
from dataclasses import dataclass, fields

from classes import NIVEL_MAX, vida_max, xp_necessario


@dataclass
class Personagem:
    id: int
    utilizador_id: int
    nome: str
    classe: str
    nivel: int
    xp: int
    xp_total: int
    vida: int
    vida_max: int
    energia: int
    energia_max: int
    dinheiro: int
    ataque: int
    defesa: int
    sorte: int
    vitorias: int
    fuga_pendente: int
    criado_em: str

    @classmethod
    def de_linha(cls, linha):
        """Cria um objeto Personagem a partir de uma linha da tabela personagens."""
        return cls(**{f.name: linha[f.name] for f in fields(cls)})

    # permite p["vida"] como antes: o código que usava dicionários continua a funcionar
    def __getitem__(self, campo):
        return getattr(self, campo)

    def __setitem__(self, campo, valor):
        setattr(self, campo, valor)

    @property
    def esta_vivo(self):
        return self.vida > 0

    @property
    def xp_para_subir(self):
        return xp_necessario(self.nivel)

    def pode_pagar(self, custo):
        return custo <= self.dinheiro

    def curar(self, valor):
        """Restaura vida sem passar do máximo. Devolve quanto restaurou."""
        antes = self.vida
        self.vida = min(self.vida_max, self.vida + valor)
        return self.vida - antes

    def recuperar_energia(self, valor):
        antes = self.energia
        self.energia = min(self.energia_max, self.energia + valor)
        return self.energia - antes

    def receber_dano(self, dano):
        """Desconta vida (nunca abaixo de 0). Devolve a vida que ficou."""
        self.vida = max(0, self.vida - dano)
        return self.vida

    def ganhar_xp(self, xp):
        """Soma XP e sobe de nível sempre que chega a 200 x nível. Devolve os níveis alcançados."""
        self.xp += xp
        self.xp_total += xp
        subidos = []
        while self.nivel < NIVEL_MAX and self.xp >= self.xp_para_subir:  # while, não if: pode subir vários
            self.xp -= self.xp_para_subir
            self.nivel += 1
            self.vida_max = vida_max(self.classe, self.nivel)
            self.vida, self.energia = self.vida_max, self.energia_max
            subidos.append(self.nivel)
        if self.nivel == NIVEL_MAX:  # no nível máximo a barra fica cheia, sem acumular
            self.xp = min(self.xp, xp_necessario(NIVEL_MAX))
        return subidos

    def resumo(self):
        return (f"{self.nome} ({self.classe}) | nível {self.nivel} | XP {self.xp}/{self.xp_para_subir}"
                f" | vida {self.vida}/{self.vida_max} | energia {self.energia}/{self.energia_max}"
                f" | dinheiro {self.dinheiro} | ataque {self.ataque} | defesa {self.defesa} | sorte {self.sorte}"
                f" | vitórias {self.vitorias} | criada em {self.criado_em}")
