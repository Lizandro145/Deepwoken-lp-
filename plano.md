# Plano de Desenvolvimento do Jogo (Deepwoken)

## 1. Visão Geral
Este documento estabelece as etapas de desenvolvimento do jogo, mapeando todas as regras descritas em `docs/jogo.md` para a implementação prática no código.

---

## 2. Fases de Desenvolvimento

### **Fase 1: Estrutura da Base de Dados e Dados do Jogo**
- [ ] **Módulo de Modelos:** Criar as estruturas de dados para:
  - **Jogador:** Nome, Classe, Nível (Power), Vida Atual/Máxima, Ether Atual/Máximo, Ataque, Defesa, Dinheiro, XP, Vitórias e Inventário.
  - **Classes (Oaths):** Estatísticas base e lista de habilidades especiais.
  - **Inimigos:** Estatísticas (Vida, Ataque, Defesa, Dinheiro, XP, Crítico, Fuga).
  - **Itens:** Tipo (Arma, Comida, Poção, Material), Preço, Stock, Efeito.
  - **Missões:** Nome, Objetivo, Recompensas, Estado (*Disponível*, *Em curso*, *Concluída*, *Falhada*).

---

### **Fase 2: Sistema de Economia e Loja**
- [ ] **Loja:**
  - Implementar listagem de itens com filtro por tipo.
  - Função de **Compra**: Verificar saldo e stock antes de debitar dinheiro e adicionar o item ao inventário.
  - Função de **Venda**: Recomprar itens do jogador por 50% do preço original.
- [ ] **Consumo de Itens:**
  - Permitir usar poções e comida para recuperar Vida/Ether.
  - Implementar o uso da Madeira (Wood) para criar fogueiras e regenerar vida fora de combate.

---

### **Fase 3: Motor de Combate**
- [ ] **Início de Combate:** Verificar se o jogador tem pelo menos 1 de Vida.
- [ ] **Turno do Jogador:**
  - Opção 1: **Ataque Básico (M1)** – Custa 0 de Ether, causa dano base e recupera +5 de Ether.
  - Opção 2: **Habilidade de Classe** – Consome Ether (20-25) para aplicar efeitos únicos.
  - Opção 3: **Usar Item** – Consumir poção/comida do inventário.
  - Opção 4: **Fugir** – Lançar o dado contra a probabilidade de fuga do inimigo.
- [ ] **Cálculo de Dano e Sorte:**
  - Aplicar a fórmula: $(\text{Ataque} - \text{Defesa}) \times \text{Variação da Arma}$.
  - Aplicar a percentagem de crítico de acordo com o tipo de arma (Light, Medium, Heavy).
- [ ] **Turno do Inimigo:** O inimigo ataca o jogador com base nos seus atributos.
- [ ] **Resolução:**
  - **Vitória:** Atribuir XP e Dinheiro ao jogador.
  - **Derrota:** Reduzir o dinheiro em 20% e mover o jogador de volta para a vila.
  - **Penalização por Fuga:** Se fugir com sucesso, aplicar -15% de dano e metade da taxa de fuga no combate seguinte.

---

### **Fase 4: Sistema de Progressão e Missões**
- [ ] **Sistema de Nível (Power):**
  - Calcular a XP necessária: $200 \times \text{Nível Atual}$.
  - Ao subir de nível: Aumentar a Vida Máxima (+4) e o Dano Global, restaurando totalmente a Vida e o Ether.
- [ ] **Gestor de Missões:**
  - Permitir aceitar até 2 missões em simultâneo.
  - Atualizar o progresso com base nos inimigos derrotados.
  - Definir a missão como *Falhada* se o jogador for derrotado durante a execução da mesma.

---

###