## Game Development Plan (Deepwoken)

## 1. Overview
This document outlines the game's development phases, mapping all specifications from `docs/jogo.md` into practical code implementation.

---

## 2. Development Phases

### **Phase 1: Database Structure & Game Data**
- [ ] **Data Models:** Build core data structures for:
  - **Player:** Name, Class, Level (Power), Current/Max Health, Current/Max Ether, Attack, Defense, Money, XP, Victories, and Inventory.
  - **Classes (Oaths):** Base stats and special skill sets.
  - **Enemies:** Attributes (Health, Attack, Defense, Money, XP, Crit Chance, Escape Chance).
  - **Items:** Type (Weapon, Food, Potion, Material), Price, Stock, Effect.
  - **Quests:** Name, Objective, Rewards, State (*Available*, *Active*, *Completed*, *Failed*).

---

### **Phase 2: Economy & Shop System**
- [ ] **Shop System:**
  - Implement item listing with filtering options by category.
  - **Buy Function:** Check funds and stock before deducting money and adding items to inventory.
  - **Sell Function:** Buy back player items for 50% of original value.
- [ ] **Item Consumption:**
  - Allow consuming potions and food to restore Health/Ether.
  - Implement Wood usage to set up campfires and heal out of combat.

---

### **Phase 3: Combat Engine**
- [ ] **Initiate Battle:** Verify player has at least 1 Health.
- [ ] **Player Turn Options:**
  - Option 1: **Basic Attack (M1)** – Costs 0 Ether, deals base damage, restores +5 Ether.
  - Option 2: **Class Ability** – Spends Ether (20-25) to trigger unique effects.
  - Option 3: **Use Item** – Consume potions/food from inventory.
  - Option 4: **Flee** – Roll against enemy escape probability.
- [ ] **Damage & Luck Formula:**
  - Apply formula: $(\text{Attack} - \text{Defense}) \times \text{Weapon Variance}$.
  - Apply critical strike chance based on weapon class (Light, Medium, Heavy).
- [ ] **Enemy Turn:** Enemy attacks player based on stats.
- [ ] **Combat Resolution:**
  - **Victory:** Award XP and Money.
  - **Defeat:** Deduct 20% money and return player to town.
  - **Escape Penalty:** Apply -15% damage debuff and half escape chance in the following encounter.

---

### **Phase 4: Progression & Quest System**
- [ ] **Level System (Power):**
  - Calculate required XP: $200 \times \text{Current Level}$.
  - Level Up Rewards: $+4$ Max Health and global damage increase; fully restore Health and Ether.
- [ ] **Quest Manager:**
  - Track up to 2 active quests simultaneously.
  - Update quest counters based on slain targets.
  - Mark quest as *Failed* if player dies in combat.

---

### **Phase 5: User Management & Leaderboard**
- [ ] **User Profiles:**
  - **Player:** Character creation/loading, gameplay access, shop, and ranking views.
  - **Admin:** Admin dashboard to adjust shop stocks, enemy values, and manage player accounts.
- [ ] **Leaderboard:**
  - Automatically sort players by:
    1. Level (Power)
    2. Total XP
    3. Combat Victories

---

## 3. Completion Criteria
Development is complete when all requirements in `docs/jogo.md` pass tests, combat executes smoothly in loops, and leaderboard/inventory persistence works reliably.