# Deepwoken

## 1. Theme and Goal
The game takes place in Lumen, a fragmented world filled with hostile waters, bustling villages, ruined sanctuaries, and nightmarish geometries. The player embodies an explorer who must cultivate power and defy the dangers of this realm. To progress, one must explore challenging dungeons and defeat lethal monsters and enemies. 1st place on the leaderboard is achieved by the player who accumulates the most combat victories and demonstrates complete dominance.


## 2. Character Classes
| Class | Health | Attack | Defense | Ether | Class Abilities |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Dawnwalker** | 224 | 16 | 7 | 100 | **Blinding Dawn, Radiant Kick, Radiant Dawn:** Blinding and high-impact solar strikes that bypass part of enemy defense. |
| **Starkindred** | 242 *(+8% HP)* | 14 | 6 | 100 | **Ascension, Sinister Halo, Celestial Assault:** Aerial mobility, damaging halo, and celestial rush. Has +8% base health. |
| **Contractor** | 224 | 15 | 8 | 100 | **Lord's Slice, Equalizer, Judgement:** Precise slashes that execute fatal judgements. |
| **Arcwader** | 224 | 15 | 9 | 100 | **Arc Beam, Arc Wave, Arc Suit:** Electric beams and waves. Activating *Arc Suit* reduces all incoming damage by 20%. |
| **Jetstriker** | 224 | 17 | 5 | 100 | **Fake Strike, Jet Kick, Rush of Ancients:** High-speed combat. *Rush of Ancients* allows attacking twice in a row. |
| **Linkstrider** | 224 | 13 | 7 | 100 | **Link, Symbiotic Sustain, Parasitic Leech:** Support class. Requires active *Link* on target to heal allies (*Symbiotic Sustain*) or steal health from opponents (*Parasitic Leech*). |
| **Silentheart** | 224 | 18 | 8 | 100 | **Manikati, Ankle Cutter, Rising Star, Mayhem, Relentless Hunt:** Pure physical combat master. Takes reduced magic damage and relentlessly hunts targets. |
| **Bladeharper** | 224 | 16 | 6 | 100 | **Decimate, Palmstrike, Soaring Storm:** Fluid and lethal combinations of blade and palm strikes. |
| **Chainwarden** | 224 | 14 | 10 | 100 | **Rupture, Impel, Restrain:** Heavy crowd control utilizing chains to immobilize and restrain opponents. |

Starting Money: 300 coins.

## 3. Experience and Levels
- **XP needed to level up (Power):** $200 \times \text{current level}$
- **Upon leveling up Power (Level 1 to 20):**
  - $+4$ Max Health per Power (scales from 224 at Power 1 up to 300 at Power 20, maintaining class percentage bonuses).
  - Global damage increase against all enemies (non-player characters).
  - Health and Ether fully restored.
- **Ways to earn XP:** Combat and Quests.

## 4. Shop Items
| Name | Type | Price | Stock | Effect |
| :--- | :--- | :---: | :---: | :--- |
| **Ysley's Pyre Keeper** | Heavy Weapon (Greatsword) | 450 | 5 | +15 Attack |
| **Sanguine Transfuser** | Light Weapon (Dagger) | 200 | 15 | +6 Attack, Lifesteal on hit |
| **Eyes of Ethiron** | Medium Weapon (Dual Sword) | 350 | 10 | +11 Attack, +5% Critical Chance |
| **Rimebreakers** | Light Weapon (Fists) | 180 | 15 | +5 Attack |
| **Red Death** | Medium Weapon (Spear) | 320 | 10 | +10 Attack |
| **Gransudaruska** | Heavy Weapon (Greataxe) | 480 | 5 | +16 Attack |
| **Wood** | Material | 20 | 100 | Used to build a campfire (restores health out of combat) |
| **Seafood Boil** | Food | 45 | 50 | Restores 40 Health and gradually regenerates Ether |
| **Mushroom Bisque** | Food | 30 | 50 | Restores 25 Health |
| **Health Potion** | Potion | 50 | 100 | Instantly restores 50 Health |

- **Sell rule:** The shop buys items for 50% of their original price.
- **Usable items:** Health Potion, Seafood Boil, Mushroom Bisque, Wood.

## 5. Enemies
| Name | Power | Health | Attack | Defense | Money | XP | Crit Chance | Escape Chance |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Mudskipper** | 1 | 50 | 8 | 2 | 20 | 50 | 5% | 15% |
| **Bandit** | 3 | 90 | 14 | 5 | 50 | 120 | 8% | 10% |
| **Crab** | 6 | 160 | 22 | 12 | 110 | 250 | 10% | 5% |
| **Megalodaunt** | 10 | 320 | 38 | 18 | 300 | 600 | 15% | 2% |
| **Bloodlord** | 15 | 550 | 55 | 25 | 600 | 1200 | 18% | 1% |
| **Deepowl (Boss)** | 20 | 950 | 80 | 35 | 1200 | 2500 | 25% | 2% |

## 6. Combat Rules
1. **Combat Requirements:** Must have at least 1 Health.
2. **Ether Usage and Cost:** Special abilities cost an average of 20 to 25 Ether. The player has a basic attack (**M1**) that **costs 0 Ether** and **restores 5 Ether** on hit.
3. **Turn Order:** The player always strikes first.
4. **Damage Calculation:** $(\text{Attacker Attack} - \text{Defender Defense}) \times \text{Luck Factor}$. Guaranteed minimum damage of 1.
5. **Luck and Critical Factor:**
   - **Light Weapons:** Damage varies between 90% and 110% (+15% crit chance).
   - **Medium Weapons:** Damage varies between 85% and 115% (+8% crit chance).
   - **Heavy Weapons:** Damage varies between 75% and 125% (+3% crit chance).
6. **End of Combat:** Combat ends when Player Health reaches 0, Enemy Health reaches 0, or if the player successfully escapes.
7. **Victory, Defeat, and Fleeing:**
   - **Victory:** Grants enemy Money and XP.
   - **Defeat:** Player loses 20% of current money and respawns in town with minimum health.
   - **Fleeing:** On a successful escape, the player deals -15% damage and has their escape chance halved in the next fight.

## 7. Quests
| Name | Objective | Difficulty | Money | XP |
| :--- | :--- | :---: | :---: | :---: |
| **Mudskipper Mayhem** | Defeat 6 Mudskippers | Easy | 80 | 120 |
| **Bandit Hunt** | Defeat 3 Bandits | Medium | 150 | 250 |
| **Crustacean Hunt** | Defeat 1 Crab | Hard | 250 | 400 |
| **Bravery** | Defeat 1 Megalodaunt | Very Hard | 500 | 900 |

- **Quest States:** Available, Active, Completed, Failed.
- **Quest Failure:** A quest fails if the player is defeated (Health = 0) while it is active.
- **Active Quest Limit:** The player can have a maximum of **2 active quests** at a time.

## 8. Leaderboard
Ranking criteria (tie-breakers in order):
1. Level (Power)
2. Total XP
3. Combat Victories

## 9. User Roles
- **Player:** Can create a character, select a class, engage in combat, buy/sell shop items, accept/complete quests, and view their position on the leaderboard.
- **Admin:** Can manage players (create, edit, delete), modify shop stock/prices, edit quests, and adjust global parameters for combat or enemies.
