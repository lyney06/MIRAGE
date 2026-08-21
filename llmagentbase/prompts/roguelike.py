# ==============================================================
# GAME-domain -- INSTRUCTION PROMPT
# ==============================================================

game_instruction = """
In this task, you will play through a turn-based roguelike RPG with the goal of defeating the final-floor boss **while following the supplied strategy guide**.

At every time step you receive a textual *Observation* that contains:
1. The current **level type** (growth, combat, shop, or boss) and a short environmental description.
2. Lists of **Collectible Items**, **Containers**, **NPCs/Enemies**, **Readable Objects**, plus any shop stock or rumours.
3. Your character sheet: HP, coins, inventory weight / capacity, full inventory with elemental tags, and Max Steps remaining.

You may issue actions only from the following action list (one per time step):

    think[...]                -> Private reasoning or planning (the environment echoes back “OK.”). Do not overuse it. Specifically, you cannot think with similar output multiple times, which causes useless duplication.
    collect <item>            -> Pick up a listed collectible item.
    open <container>          -> Open a container and automatically scoop up its contents.
    craft <item>              -> Combine the exact required materials in your inventory.
    discard <item>            -> Drop an item to free weight.
    unequip                   -> for all environments
    equip <weapon>            -> Wield a weapon from your inventory.
    attack <enemy> or attack  -> Strike the target. 
    buy <item>                -> Purchase from a shop if you meet the cost.
    talk <npc>                -> Speak with an NPC.
    read <object>             -> Read flavour or clue text.
    leave                     -> Exit the current level and advance to the next.
    recipes                   -> Show a list of available crafting recipes.

Movement between rooms is abstracted: *leave* is the only navigation verb.



Game constraints and tips
-------------------------
* **Inventory weight** cannot exceed the stated capacity; discard or skip surplus loot.
* **Crafting** instantly consumes materials; partial recipes are invalid.
* Elemental effectiveness matters in combat: e.g. FIRE > ICE, WATER > FIRE.
* Feel free to interleave `think[...]` steps to plan, but don't overuse it. they do **not** cost extra time beyond one action.

Good luck, adventurer!
"""

game_instruction_back = """
In this task, you will play through a turn-based roguelike RPG with the goal of defeating the final-floor boss **while following the supplied strategy guide**.

At every time step you receive a textual *Observation* that contains:
1. The current **level type** (growth, combat, shop, or boss) and a short environmental description.
2. Lists of **Collectible Items**, **Containers**, **NPCs/Enemies**, **Readable Objects**, plus any shop stock or rumours.
3. Your character sheet: HP, coins, inventory weight / capacity, full inventory with elemental tags, and Max Steps remaining.

You may issue actions only from the following action list (one per time step):

    think[...]                -> Private reasoning or planning (the environment echoes back “OK.”). Do not overuse it. Specifically, you cannot think with similar output multiple times, which causes useless duplication.
    collect <item>            -> Pick up a listed collectible item.
    open <container>          -> Open a container and automatically scoop up its contents.
    craft <item>              -> Combine the exact required materials in your inventory.
    discard <item>            -> Drop an item to free weight.
    unequip                   -> for all environments
    equip <weapon>            -> Wield a weapon from your inventory.
    attack <enemy> or attack  -> Strike the target. 
    buy <item>                -> Purchase from a shop if you meet the cost.
    talk <npc>                -> Speak with an NPC.
    read <object>             -> Read flavour or clue text.
    leave                     -> Exit the current level and advance to the next.
    back                      -> back to last level. 
    recipes                   -> Show a list of available crafting recipes.

Movement between rooms is abstracted: *leave* to advance and *back* to return to the previous level.



Game constraints and tips
-------------------------
* **Inventory weight** cannot exceed the stated capacity; discard or skip surplus loot.
* **Crafting** instantly consumes materials; partial recipes are invalid.
* Elemental effectiveness matters in combat: e.g. FIRE > ICE, WATER > FIRE.
* Feel free to interleave `think[...]` steps to plan, but don't overuse it. they do **not** cost extra time beyond one action.

Good luck, adventurer!
"""

# ==============================================================
# GAME-domain -- REAct PROMPT (single worked example)
# ==============================================================

game_react = """

Here is one example from ANOTHER task. it shows the command and strategy you interact with the enviroment. Note that the item you need in your task can be DIFFERENT:

Observation: Welcome to RougelikeRPG (Easy Mode)!
Your starting inventory:
Coin(s): 0
Inventory (Weight: 4/12):
Materials:
  - Frost Particle
  - Weapon Prototype

You are now entering **Level 1: Growth** — a sun-dappled forest.  
Collectible Items: Fire Essence, Light Shard, Shadow Dust, Leaf Fragment, Frost Particle  
Containers: bird nest

Action: recipes
Observation: You review the crafting recipes you know...

# Crafting Recipe Book

## Weapons
- Fire Staff: Recipe for Fire Staff: 1 Fire Essence, 1 Weapon Prototype [Available]
- Water Wand: Recipe for Water Wand: 1 Water Crystal, 1 Weapon Prototype [Missing materials]
- Nature Bow: Recipe for Nature Bow: 1 Leaf Fragment, 1 Weapon Prototype [Missing materials]
- Light Mace: Recipe for Light Mace: 1 Light Shard, 1 Weapon Prototype [Missing materials]
- Dark Dagger: Recipe for Dark Dagger: 1 Shadow Dust, 1 Weapon Prototype [Missing materials]
- Lightning Rod: Recipe for Lightning Rod: 1 Lightning Spark, 1 Weapon Prototype [Missing materials]
- Ice Sword: Recipe for Ice Sword: 1 Frost Particle, 1 Weapon Prototype [Missing materials]
- Earth Hammer: Recipe for Earth Hammer: 1 Earth Stone, 1 Weapon Prototype [Missing materials]

## Enhancers
- Fire Enhancer: Recipe for Fire Enhancer: 2 Fire Essence, 1 Magic Catalyst [Missing materials]
- Water Enhancer: Recipe for Water Enhancer: 2 Water Crystal, 1 Magic Catalyst [Missing materials]
- Nature Enhancer: Recipe for Nature Enhancer: 2 Leaf Fragment, 1 Magic Catalyst [Missing materials]
- Light Enhancer: Recipe for Light Enhancer: 2 Light Shard, 1 Magic Catalyst [Missing materials]
- Dark Enhancer: Recipe for Dark Enhancer: 2 Shadow Dust, 1 Magic Catalyst [Missing materials]
- Lightning Enhancer: Recipe for Lightning Enhancer: 2 Lightning Spark, 1 Magic Catalyst [Missing materials]
- Ice Enhancer: Recipe for Ice Enhancer: 2 Frost Particle, 1 Magic Catalyst [Missing materials]
- Earth Enhancer: Recipe for Earth Enhancer: 2 Earth Stone, 1 Magic Catalyst [Missing materials]

## Advanced Weapons
- Inferno Blaster: Recipe for Inferno Blaster: 1 Fire Staff, 1 Fire Enhancer, 1 Enchanted Cloth [Missing materials]
- Tsunami Trident: Recipe for Tsunami Trident: 1 Water Wand, 1 Water Enhancer, 1 Enchanted Cloth [Missing materials]
- Gaia's Vengeance: Recipe for Gaia's Vengeance: 1 Nature Bow, 1 Nature Enhancer, 1 Enchanted Cloth [Missing materials]
- Divine Scepter: Recipe for Divine Scepter: 1 Light Mace, 1 Light Enhancer, 1 Enchanted Cloth [Missing materials]
- Void Reaper: Recipe for Void Reaper: 1 Dark Dagger, 1 Dark Enhancer, 1 Enchanted Cloth [Missing materials]
- Storm Caller: Recipe for Storm Caller: 1 Lightning Rod, 1 Lightning Enhancer, 1 Enchanted Cloth [Missing materials]
- Glacier Blade: Recipe for Glacier Blade: 1 Ice Sword, 1 Ice Enhancer, 1 Enchanted Cloth [Missing materials]
- Mountain Breaker: Recipe for Mountain Breaker: 1 Earth Hammer, 1 Earth Enhancer, 1 Enchanted Cloth [Missing materials]

Action: collect Fire Essence
Observation: You collected the Fire Essence. Added Fire Essence to inventory.

Action: think[I will open the containers one by one to check if there are other useful things. If other junks are inside I will just discard them.]
Observation: OK.

Action: open bird nest
Observation: You found **Magic Catalyst**! Added to inventory.

Action: think[Frost Particle is unnecessary weight as I need a fire weapon. Discard it.]
Observation: OK.

Action: discard Frost Particle
Observation: Frost Particle removed.

Action: think[Now craft the Fire Staff.]
Observation: OK.

Action: craft Fire Staff
Observation: **Fire Staff** created!

Action: think[There're no more useful items here. Leave the level.]
Observation: OK.

Action: leave
Observation: You proceed to **Level 2: Growth** — a sunny shoreline.  
Collectible Items: Water Crystal, Magic Catalyst, Light Shard.
Containers: Tide Pools, Magic Box

Action: think[I can see a Water Crystal, maybe a water weapon will also be good. I can grab it.]
Observation: OK.

Action: collect Water Crystal
Observation: Water Crystal added to inventory.

Action: think[Let's also do the search on containers to see if they contain useful materials.]
Observation: OK.

Action: open magic box
Observation: You found a **Earth Fragment**! Added to inventory.

Action: think[Earth Fragment is NOT in my plan of collected item now or future. My inventory has very limited capacity, I need to discard it.]
Observation: OK.

Action: discard Earth Fragment
Observation: You discarded Earth Fragment.

Action: open tide pool
Observation: You found **Fire Essence**! Added to inventory.

Action: leave
Observation: You enter **Level 3: Combat** beside a roaring river.  
Enemy: Restless Rain Phantom (WATER)

Action: think[I must equip weapon before fighting.]
Observation: OK.

Action: equip Fire Staff
Observation: Fire Staff equipped.

Action: attack Restless Rain Phantom
Observation: You deal 7 damage (not very effective); take 5 damage. HP = 110.

Action: think[Repeat attacks until it falls.]
Observation: OK.

Action: attack Restless Rain Phantom
… (several repeats) …
Observation: Rain Phantom defeated! Loot: Enchanted Cloth, coin, Weapon Prototype, Light Shard.

Action: think[Keep Enchanted Cloth, discard junk, then leave.]
Observation: OK.

Action: discard Light Shard
Observation: Light Shard removed.

Action: discard Weapon Prototype
Observation: Weapon Prototype removed.

Action: leave
Observation: You step into **Level 4: Growth** — a damp cave.

Action: collect Magic Catalyst
Observation: Magic Catalyst added.

Action: leave
Observation: You arrive at **Level 5: Shop** (Thorne the Artificer).  
For sale: Fire Essence (cost = 1 Water Crystal), …

Action: think[I need two Fire Essences for Fire Enhancer. Trade Water Crystal.]
Observation: OK.

Action: buy Fire Essence
Observation: Purchased Fire Essence.

Action: craft Fire Enhancer
Observation: **Fire Enhancer** crafted!

Action: craft Inferno Blaster
Observation: **Inferno Blaster** crafted!

Action: think[Shop checkpoint met (one Inferno Blaster). Onward!]
Observation: OK.

Action: leave
Observation: **Level 6: Boss** — snow swirls around the Eternal Frost Titan (ICE).

Action: equip Inferno Blaster
Observation: Inferno Blaster equipped.

Action: think[Fire beats Ice. Attack until it's down.]
Observation: OK.

Action: attack Eternal Frost Titan
Observation: You deal 50 damage (super-effective); HP drops to 67.

… (two more attacks) …

Observation: **Eternal Frost Titan defeated! Task completed successfully.**
"""



game_react_type0 = """
Here is one example from ANOTHER task. it shows the command and strategy you interact with the enviroment. Note that the item you need in your task can be DIFFERENT:

The guide for THAT example:
You will face a ICE-element boss on the final floor.
To counter it effectively, we recommend using a FIRE-element weapon: Inferno Blaster.

To craft Inferno Blaster, follow these steps:
- Craft Fire Staff using 1 Fire Essence, 1 Weapon Prototype
- Craft Fire Enhancer using 2 Fire Essences, 1 Magic Catalyst
- Craft Inferno Blaster using 1 Fire Staff, 1 Fire Enhancer, 1 Enchanted Cloth

Make sure that you have the following items in your inventory when you leave each of the levels:
  Level 1 (growth):
    - Fire Staff ×1
    - Magic Catalyst ×1
  Level 2 (growth):
    - Fire Staff ×1
    - Fire Essence ×1
    - Magic Catalyst ×1
    - Water Crystal ×1
  Level 3 (combat):
    - Fire Staff ×1
    - Fire Essence ×1
    - Magic Catalyst ×1
    - Water Crystal ×1
    - Enchanted Cloth ×1
  Level 4 (growth):
    - Fire Staff ×1
    - Fire Essence ×1
    - Magic Catalyst ×1
    - Water Crystal ×1
    - Enchanted Cloth ×1
  Level 5 (shop):
    - Inferno Blaster ×1

To fight the enemies, make sure to:
Level 3 (combat): Arm yourself with the most powerful weapon against the enemies.
 - To fight Restless Rain Phantom (WATER), use Fire Staff.
Level 6 (boss): Arm yourself with the most powerful weapon against the enemies.
 - To fight Eternal Frost Titan (ICE), use Inferno Blaster.

Observation: Welcome to RougelikeRPG (Easy Mode)!
Your starting inventory:
Coin(s): 0
Inventory (Weight: 4/12):
Materials:
  - Frost Particle
  - Weapon Prototype

You are now entering **Level 1: Growth** — a sun-dappled forest.  
Collectible Items: Fire Essence, Light Shard, Shadow Dust, Leaf Fragment, Frost Particle  
Containers: bird nest

Action: think[The strategy guide says I must leave this level with a *Fire Staff*. That requires 1 Fire Essence + my Weapon Prototype. Step 1: pick up Fire Essence.]
Observation: OK.

Action: collect Fire Essence
Observation: You collected the Fire Essence. Added Fire Essence to inventory.

Action: think[I need to collect a Magic Catalyst to pass the checkpoint. However, there is no Magic Catalyst, I will open the containers one by one to check if Magic Catalyst is inside. If other junks are inside I will just discard them.]
Observation: OK.

Action: open bird nest
Observation: You found **Magic Catalyst**! Added to inventory.

Action: think[Frost Particle is unnecessary weight. Discard it.]
Observation: OK.

Action: discard Frost Particle
Observation: Frost Particle removed.

Action: think[Now craft the Fire Staff.]
Observation: OK.

Action: craft Fire Staff
Observation: **Fire Staff** created!

Action: think[Checkpoint satisfied (one Fire Staff). Leave the level.]
Observation: OK.

Action: leave
Observation: You proceed to **Level 2: Growth** — a sunny shoreline.  
Collectible Items: Water Crystal, Magic Catalyst, Light Shard.
Containers: Tide Pools, Magic Box

Action: think[I must exit this level with one additional Fire Essence and one Water Crystal. I need to grab a Water Crystal.]
Observation: OK.

Action: collect Water Crystal
Observation: Water Crystal added to inventory.

Action: think[Let's also do the search on containers to find the Fire Essence.]
Observation: OK.

Action: open magic box
Observation: You found a **Earth Fragment**! Added to inventory.

Action: think[Earth Fragment is NOT in my plan of collected item now or future. My inventory has very limited capacity, I need to discard it.]
Observation: OK.

Action: discard Earth Fragment
Observation: You discarded Earth Fragment.

Action: think[Now let's check another container. Let's check the Tide pool.]
Observation: OK.

Action: open tide pool
Observation: You found **Fire Essence**! Added to inventory.

Action: think[Inventory checkpoint met. Leave.]
Observation: OK.

Action: leave
Observation: You enter **Level 3: Combat** beside a roaring river.  
Enemy: Restless Rain Phantom (WATER)

Action: think[I must equip weapon before fighting according to the guide.]
Observation: OK.

Action: equip Fire Staff
Observation: Fire Staff equipped.

Action: attack Restless Rain Phantom
Observation: You deal 7 damage (not very effective); take 5 damage. HP = 110.

Action: think[Repeat attacks until it falls.]
Observation: OK.

Action: attack Restless Rain Phantom
… (several repeats) …
Observation: Rain Phantom defeated! Loot: Enchanted Cloth, coin, Weapon Prototype, Light Shard.

Action: think[Keep Enchanted Cloth, discard junk, then leave.]
Observation: OK.

Action: discard Light Shard
Observation: Light Shard removed.

Action: discard Weapon Prototype
Observation: Weapon Prototype removed.

Action: leave
Observation: You step into **Level 4: Growth** — a damp cave.

Action: think[There is a Magic Catalyst, but I've already have a Magic Catalyst and I only need one. So I don't need to collect it.]
Observation: OK.

Action: leave
Observation: You arrive at **Level 5: Shop** (Thorne the Artificer).  
For sale: Fire Essence (cost = 1 Water Crystal), …

Action: think[I need two Fire Essences for Fire Enhancer. I can use the Water Crystal to get one.]
Observation: OK.

Action: buy Fire Essence
Observation: Purchased Fire Essence.

Action: craft Fire Enhancer
Observation: **Fire Enhancer** crafted!

Action: craft Inferno Blaster
Observation: **Inferno Blaster** crafted!

Action: think[Shop checkpoint met (one Inferno Blaster). Onward!]
Observation: OK.

Action: leave
Observation: **Level 6: Boss** — snow swirls around the Eternal Frost Titan (ICE).

Action: equip Inferno Blaster
Observation: Inferno Blaster equipped.

Action: think[Fire beats Ice. Attack until it's down.]
Observation: OK.

Action: attack Eternal Frost Titan
Observation: You deal 50 damage (super-effective); HP drops to 67.

… (two more attacks) …

Observation: **Eternal Frost Titan defeated! Task completed successfully.**
"""



game_react_type1 = """

Here is one example from ANOTHER task. it shows the command and strategy you interact with the enviroment. Note that the item you need in your task can be DIFFERENT:

The guide for THAT example:
You will face a ICE-element boss on the final floor.
To counter it effectively, we recommend using a FIRE-element weapon: Inferno Blaster.

To craft Inferno Blaster, follow these steps:
- Craft Fire Staff using 1 Fire Essence, 1 Weapon Prototype
- Craft Fire Enhancer using 2 Fire Essences, 1 Magic Catalyst
- Craft Inferno Blaster using 1 Fire Staff, 1 Fire Enhancer, 1 Enchanted Cloth

You will need to prepare the following materials:
- Fire Essence ×3
- Weapon Prototype ×1
- Magic Catalyst ×1
- Enchanted Cloth ×1
- Water Crystal ×1

Observation: Welcome to RougelikeRPG (Easy Mode)!
Your starting inventory:
Coin(s): 0
Inventory (Weight: 4/12):
Materials:
  - Frost Particle
  - Weapon Prototype

You are now entering **Level 1: Growth** — a sun-dappled forest.  
Collectible Items: Fire Essence, Light Shard, Shadow Dust, Leaf Fragment, Frost Particle  
Containers: bird nest

Action: think[The strategy guide says I must leave this level with a *Fire Staff*.  
That requires 1 Fire Essence + my Weapon Prototype. Step 1: pick up Fire Essence.]
Observation: OK.

Action: collect Fire Essence
Observation: You collected the Fire Essence. Added Fire Essence to inventory.

Action: think[I need to collect a Magic Catalyst to pass the checkpoint. However, there is no Magic Catalyst, I will open the containers one by one to check if Magic Catalyst is inside. If other junks are inside I will just discard them.]
Observation: OK.

Action: open bird nest
Observation: You found **Magic Catalyst**! Added to inventory.

Action: think[Frost Particle is unnecessary weight. Discard it.]
Observation: OK.

Action: discard Frost Particle
Observation: Frost Particle removed.

Action: think[Now I can craft the Fire Staff.]
Observation: OK.

Action: craft Fire Staff
Observation: **Fire Staff** created!

Action: leave
Observation: You proceed to **Level 2: Growth** — a sunny shoreline.  
Collectible Items: Water Crystal, Magic Catalyst, Light Shard.
Containers: Tide Pools, Magic Box

Action: think[I must exit this level with one Fire Essence and one Water Crystal.  
I already have Fire Essence; This just grab a Water Crystal.]
Observation: OK.

Action: collect Water Crystal
Observation: Water Crystal added to inventory.

Action: think[Let's also do the search on containers to see if they contain useful materials.]
Observation: OK.

Action: open magic box
Observation: You found a **Earth Fragment**! Added to inventory.

Action: think[Earth Fragment is NOT in my plan of collected item now or future. My inventory has very limited capacity, I need to discard it.]
Observation: OK.

Action: discard Earth Fragment
Observation: You discarded Earth Fragment.

Action: think[Now let's check another container. Let's check the Tide pool.]
Observation: OK.

Action: open tide pool
Observation: You found **Fire Essence**! Added to inventory.


Action: leave
Observation: You enter **Level 3: Combat** beside a roaring river.  
Enemy: Restless Rain Phantom (WATER)

Action: think[I must equip weapon before fighting.]
Observation: OK.

Action: equip Fire Staff
Observation: Fire Staff equipped.

Action: attack Restless Rain Phantom
Observation: You deal 7 damage (not very effective); take 5 damage. HP = 110.

Action: think[Repeat attacks until it falls.]
Observation: OK.

Action: attack Restless Rain Phantom
… (several repeats) …
Observation: Rain Phantom defeated! Loot: Enchanted Cloth, coin, Weapon Prototype, Light Shard.

Action: think[Keep Enchanted Cloth, discard junk, then leave.]
Observation: OK.

Action: discard Light Shard
Observation: Light Shard removed.

Action: discard Weapon Prototype
Observation: Weapon Prototype removed.

Action: leave
Observation: You step into **Level 4: Growth** — a damp cave.

Action: collect Magic Catalyst
Observation: Magic Catalyst added.

Action: leave
Observation: You arrive at **Level 5: Shop** (Thorne the Artificer).  
For sale: Fire Essence (cost = 1 Water Crystal), …

Action: think[I need two Fire Essences for Fire Enhancer. Trade Water Crystal.]
Observation: OK.

Action: buy Fire Essence
Observation: Purchased Fire Essence.

Action: craft Fire Enhancer
Observation: **Fire Enhancer** crafted!

Action: craft Inferno Blaster
Observation: **Inferno Blaster** crafted!


Action: leave
Observation: **Level 6: Boss** — snow swirls around the Eternal Frost Titan (ICE).

Action: equip Inferno Blaster
Observation: Inferno Blaster equipped.

Action: think[Fire beats Ice. Attack until it's down.]
Observation: OK.

Action: attack Eternal Frost Titan
Observation: You deal 50 damage (super-effective); HP drops to 67.

… (two more attacks) …

Observation: **Eternal Frost Titan defeated! Task completed successfully.**
"""



game_react_type2 = """

Here is one example from ANOTHER task. it shows the command and strategy you interact with the enviroment. Note that the item you need in your task can be DIFFERENT:
The guide for THAT example:
You will face a ICE-element boss on the final floor.
To counter it effectively, we recommend using a FIRE-element weapon: Inferno Blaster.

To craft Inferno Blaster, follow these steps:
- Craft Fire Staff using 1 Fire Essence, 1 Weapon Prototype
- Craft Fire Enhancer using 2 Fire Essences, 1 Magic Catalyst
- Craft Inferno Blaster using 1 Fire Staff, 1 Fire Enhancer, 1 Enchanted Cloth


You will need to collect items from the following levels:
Level 1 (growth):
 - Fire Essence ×1 
Level 2 (growth):
 - Fire Essence ×1 
Level 3 (combat):
 - Enchanted Cloth ×1 
Level 4 (growth):
 - Magic Catalyst ×1 
 - Fire Essence ×1 

Observation: Welcome to RougelikeRPG (Easy Mode)!
Your starting inventory:
Coin(s): 0
Inventory (Weight: 4/12):
Materials:
  - Frost Particle
  - Weapon Prototype

You are now entering **Level 1: Growth** — a sun-dappled forest.  
Collectible Items: Fire Essence, Light Shard, Shadow Dust, Leaf Fragment, Frost Particle  
Containers: bird nest

Action: think[The startegy guide asks me to collect three Fire Essences, there is one on the ground. So collect it.]
Observation: OK.

Action: collect Fire Essence
Observation: You collected the Fire Essence. Added Fire Essence to inventory.


Action: think[Frost Particle is unnecessary weight. Discard it.]
Observation: OK.

Action: discard Frost Particle
Observation: Frost Particle removed.

Action: think[I have Fire Essence and Weapon prototype. Now craft the Fire Staff.]
Observation: OK.

Action: craft Fire Staff
Observation: **Fire Staff** created!

Action: think[maybe I need to also check what is in the bird nest. If the thing is useful, I will keep it, otherwise I will just discard it.]
Observation: OK.

Action: open bird nest
Observation: You opened the bird nest. You found an Earth Element. Added to Inventory.

Action: think[Oh it seems that the Earth Element has nothing to do with my collection plan, I will discard it.]
Observation: OK.


Action: discard Earth Element
Observation: Earth Element removed.


Action: leave
Observation: You proceed to **Level 2: Growth** — a sunny shoreline.  
Collectible Items: Water Crystal, Magic Catalyst, Light Shard.
Containers: Tide Pools, Magic Box

Action: think[The guide asks me to collect Water Crystal and Fire Essence. According to the guide, The Water Crystal will be used in trading later. I have to collect it here and save until I trade it. I will collect Water Crystal first. ]
Observation: OK.

Action: collect Water Crystal
Observation: Water Crystal added to inventory.


Action: think[There is no Fire Essence on the ground, I need to open each container to check.]
Observation: OK.

Action: open tide pool
Observation: You found **Fire Essence**! Added to inventory.

Action: think[Great. Let me check other containers.]
Observation: OK.

...(several checks)...

Action: leave
Observation: You enter **Level 3: Combat** beside a roaring river.  
Enemy: Restless Rain Phantom (WATER)

Action: think[I must equip weapon before fighting.]
Observation: OK.

Action: equip Fire Staff
Observation: Fire Staff equipped.

Action: attack Restless Rain Phantom
Observation: You deal 7 damage (not very effective); take 5 damage. HP = 110.

Action: think[Repeat attacks until it falls.]
Observation: OK.

Action: attack Restless Rain Phantom
… (several repeats) …
Observation: Rain Phantom defeated! Loot: Enchanted Cloth, coin, Weapon Prototype, Light Shard.

Action: think[According to the guide, I will keep Enchanted Cloth, discard junk, then leave.]
Observation: OK.

Action: discard Light Shard
Observation: Light Shard removed.

Action: discard Weapon Prototype
Observation: Weapon Prototype removed.

Action: leave
Observation: You step into **Level 4: Growth** — a damp cave.

Action: think[According to the guide, I need to collect one Magic Catalyst, I know from the guide there is one on the ground. Just collect it.]
Observation: OK.

Action: collect Magic Catalyst
Observation: Magic Catalyst added.

Action: leave
Observation: You arrive at **Level 5: Shop** (Thorne the Artificer).  
For sale: Fire Essence (cost = 1 Water Crystal), …

Action: think[I need one Fire Essences for Fire Enhancer. Trade Water Crystal.]
Observation: OK.

Action: buy Fire Essence
Observation: Purchased Fire Essence.

Action: think[I need to craft the weapon before I start combating. According to the guide I will craft Fire Enhancer, then Inferno Blaster.]
Observation: OK.

Action: craft Fire Enhancer
Observation: **Fire Enhancer** crafted!

Action: craft Inferno Blaster
Observation: **Inferno Blaster** crafted!



Action: leave
Observation: **Level 6: Boss** — snow swirls around the Eternal Frost Titan (ICE).

Action: equip Inferno Blaster
Observation: Inferno Blaster equipped.

Action: think[Fire beats Ice. Attack until it's down.]
Observation: OK.

Action: attack Eternal Frost Titan
Observation: You deal 50 damage (super-effective); HP drops to 67.

… (two more attacks) …

Observation: **Eternal Frost Titan defeated! Task completed successfully.**
"""


game_react_type3 = """


Here is one example from ANOTHER task. it shows the command and strategy you interact with the enviroment. Note that the item you need in your task can be DIFFERENT:
The guide for THAT example:
You will face a ICE-element boss on the final floor.
To counter it effectively, we recommend using a FIRE-element weapon: Inferno Blaster.

To craft Inferno Blaster, follow these steps:
- Craft Fire Staff using 1 Fire Essence, 1 Weapon Prototype
- Craft Fire Enhancer using 2 Fire Essences, 1 Magic Catalyst
- Craft Inferno Blaster using 1 Fire Staff, 1 Fire Enhancer, 1 Enchanted Cloth

You will need to collect items from the following levels:
Level 1 (growth):
 - Fire Essence ×1 (one on the ground)
Level 2 (growth):
 - Fire Essence ×1 (one in the tide pool, one in the wooden crate. you only need to collect 1 of them.)
 - Water Crystal ×1 (one on the ground, we collect this for trading it in the shop later)
Level 3 (combat):
 - Enchanted Cloth ×1 (one from defeating Restless Blizzard Spirit)
Level 4 (growth):
 - Magic Catalyst ×1 (one on the ground, one in the stalagmite. you only need to collect 1 of them.)
Level 5 (shop):
 - Fire Essence ×1 (one in the shop, use Water Crystal to trade it; you can also buy one using a coin.)

Observation: Welcome to RougelikeRPG (Easy Mode)!
Your starting inventory:
Coin(s): 0
Inventory (Weight: 4/12):
Materials:
  - Frost Particle
  - Weapon Prototype

You are now entering **Level 1: Growth** — a sun-dappled forest.  
Collectible Items: Fire Essence, Light Shard, Shadow Dust, Leaf Fragment, Frost Particle  
Containers: bird nest

Action: think[The startegy guide asks me to collect one Fire Essence which is just on the ground. So collect it.]
Observation: OK.

Action: collect Fire Essence
Observation: You collected the Fire Essence. Added Fire Essence to inventory.


Action: think[Frost Particle is unnecessary weight. Discard it.]
Observation: OK.

Action: discard Frost Particle
Observation: Frost Particle removed.

Action: think[I have Fire Essence and Weapon prototype. Now craft the Fire Staff.]
Observation: OK.

Action: craft Fire Staff
Observation: **Fire Staff** created!

Action: think[Checkpoint satisfied. Leave the level.]
Observation: OK.

Action: leave
Observation: You proceed to **Level 2: Growth** — a sunny shoreline.  
Collectible Items: Water Crystal, Magic Catalyst, Light Shard.
Containers: Tide Pools, Magic Box

Action: think[The guide asks me to collect Water Crystal and Fire Essence in this level. According to the guide, The Water Crystal will be used in trading later. I have to collect it here and save until I trade it. I will collect Water Crystal first. ]
Observation: OK.

Action: collect Water Crystal
Observation: Water Crystal added to inventory.


Action: think[I know from the guide that Tide pools hide Fire Essence. I will collect it.]
Observation: OK.

Action: open tide pool
Observation: You found **Fire Essence**! Added to inventory.

Action: think[Inventory checkpoint met. Leave.]
Observation: OK.

Action: leave
Observation: You enter **Level 3: Combat** beside a roaring river.  
Enemy: Restless Rain Phantom (WATER)

Action: think[I must equip weapon before fighting.]
Observation: OK.

Action: equip Fire Staff
Observation: Fire Staff equipped.

Action: attack Restless Rain Phantom
Observation: You deal 7 damage (not very effective); take 5 damage. HP = 110.

Action: think[Repeat attacks until it falls.]
Observation: OK.

Action: attack Restless Rain Phantom
… (several repeats) …
Observation: Rain Phantom defeated! Loot: Enchanted Cloth, coin, Weapon Prototype, Light Shard.

Action: think[According to the guide, I will keep Enchanted Cloth, discard junk, then leave.]
Observation: OK.

Action: discard Light Shard
Observation: Light Shard removed.

Action: discard Weapon Prototype
Observation: Weapon Prototype removed.

Action: leave
Observation: You step into **Level 4: Growth** — a damp cave.

Action: think[According to the guide, I just need to collect one Magic Catalyst, I know from the guide there is one on the ground. Just collect it.]
Observation: OK.

Action: collect Magic Catalyst
Observation: Magic Catalyst added.

Action: leave
Observation: You arrive at **Level 5: Shop** (Thorne the Artificer).  
For sale: Fire Essence (cost = 1 Water Crystal), …

Action: think[I need one Fire Essences for Fire Enhancer. Trade Water Crystal.]
Observation: OK.

Action: buy Fire Essence
Observation: Purchased Fire Essence.

Action: think[I need to craft the weapon before I start combating. According to the guide I will craft Fire Enhancer, then Inferno Blaster.]
Observation: OK.

Action: craft Fire Enhancer
Observation: **Fire Enhancer** crafted!

Action: craft Inferno Blaster
Observation: **Inferno Blaster** crafted!

Action: think[Shop checkpoint met (one Inferno Blaster). Onward!]
Observation: OK.

Action: leave
Observation: **Level 6: Boss** — snow swirls around the Eternal Frost Titan (ICE).

Action: equip Inferno Blaster
Observation: Inferno Blaster equipped.

Action: think[Fire beats Ice. Attack until it's down.]
Observation: OK.

Action: attack Eternal Frost Titan
Observation: You deal 50 damage (super-effective); HP drops to 67.

… (two more attacks) …

Observation: **Eternal Frost Titan defeated! Task completed successfully.**
"""

