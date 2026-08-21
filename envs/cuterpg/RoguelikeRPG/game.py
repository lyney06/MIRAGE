"""
Main game manager for the RougelikeRPG game.
"""
import copy
import random
import numpy as np
from typing import List, Dict, Any, Optional
from common.utils import set_seed
from envs.cuterpg.RoguelikeRPG.constants import GameMode, Element, EASY_MODE_LAYERS, HARD_MODE_LAYERS, BASE_MATERIALS, RENAME_MAP
from envs.cuterpg.RoguelikeRPG.entities.player import Player
from envs.cuterpg.RoguelikeRPG.entities.item import create_material, Item
from envs.cuterpg.RoguelikeRPG.levels.level import Level
from envs.cuterpg.RoguelikeRPG.levels.growth_level import GrowthLevel
from envs.cuterpg.RoguelikeRPG.levels.combat_level import CombatLevel
from envs.cuterpg.RoguelikeRPG.levels.boss_level import BossLevel
from envs.cuterpg.RoguelikeRPG.levels.shop_level import ShopLevel
from envs.cuterpg.RoguelikeRPG.utils.solution_manager import SolutionManager
from envs.cuterpg.RoguelikeRPG.levels.utils import add_item
from envs.cuterpg.RoguelikeRPG.utils.utils import derangement
from pdb import set_trace as st

def generate_hint_text(original, renamed):
    """Generate an implicit, flavor-style hint line for a renamed item (without explicitly leaking original canonical name)."""
    from envs.cuterpg.RoguelikeRPG.constants import (
        STANDARD_WEAPONS, ADVANCED_WEAPONS, BASE_MATERIALS
    )

    elem = None
    item_type = "item"

    if original in ADVANCED_WEAPONS:
        elem = ADVANCED_WEAPONS[original]
        item_type = "weapon"
    elif original in STANDARD_WEAPONS:
        elem = STANDARD_WEAPONS[original]
        item_type = "weapon"
    elif original in BASE_MATERIALS:
        elem = BASE_MATERIALS[original]
        item_type = "material"

    elem_name = elem.value if (elem and hasattr(elem, "value")) else None

    templates = []

    if item_type == "weapon":
        if elem_name == "electric":
            templates.extend([
                f"Legend tells that '{renamed}' channels fierce high-voltage energy, ideal against ocean beasts.",
                f"Scrolls describe '{renamed}' as a formidable electric weapon forged for heavy elemental battle.",
                f"Merchant rumors say '{renamed}' crackles with lightning strikes that easily douse water foes.",
                f"I've heard that '{renamed}' is a specialized electric weapon crafted with thunder-infused materials.",
            ])
        elif elem_name == "fire":
            templates.extend([
                f"They say '{renamed}' burns with intense thermal energy, capable of melting icy titans.",
                f"Travelers speak of '{renamed}', a flame-imbued weapon revered for scorching frost-aligned enemies.",
                f"Old blacksmiths describe '{renamed}' as a searing weapon of blazing heat.",
                f"A veteran warrior told me '{renamed}' ignites fiercely against cold-hearted foes.",
            ])
        elif elem_name == "water":
            templates.extend([
                f"Scrolls note that '{renamed}' flows with torrential liquid power, extinguishing fiery threats.",
                f"Local legends describe '{renamed}' as an aquatic weapon forged to submerge blazing monsters.",
                f"I've heard that '{renamed}' channels the force of crashing tides in battle.",
                f"Merchants whisper that '{renamed}' is a water-attuned weapon feared by fire entities.",
            ])
        elif elem_name == "nature":
            templates.extend([
                f"Ancient lore says '{renamed}' bristles with wild verdant growth to shatter earth and stone.",
                f"I've heard that '{renamed}' harnesses forest power, lethal against earthen beasts.",
                f"Wanderers claim '{renamed}' channels natural flora to crush heavy ground obstacles.",
            ])
        elif elem_name == "ice":
            templates.extend([
                f"Scrolls depict '{renamed}' as radiating zero-kelvin frost, freezing flora and nature beasts.",
                f"They say '{renamed}' is an icy blade of absolute cold, devastating to wild overgrown foes.",
                f"A solitary traveler mentioned '{renamed}' freezes nature spirits in their tracks.",
            ])
        elif elem_name == "earth":
            templates.extend([
                f"Blacksmiths claim '{renamed}' carries heavy tectonic force to ground electric foes.",
                f"Legend speaks of '{renamed}' as a massive stone weapon capable of absorbing high-voltage shocks.",
                f"Local rumors say '{renamed}' possesses immense earthen mass against lightning threats.",
            ])
        elif elem_name == "light":
            templates.extend([
                f"Travelers whisper that '{renamed}' shines with solar luminescence to banish shadow fiends.",
                f"Scrolls record '{renamed}' as a radiant weapon of pure light, blinding to dark entities.",
            ])
        elif elem_name == "dark":
            templates.extend([
                f"In ancient lore, '{renamed}' pulsates with void shadow energy to consume radiant beings.",
                f"Dark merchants speak of '{renamed}', an umbral weapon that swallows light in combat.",
            ])
        else:
            templates.extend([
                f"Legends speak of '{renamed}', a weapon of great elemental power.",
                f"A skilled blacksmith told me '{renamed}' holds unique martial potential.",
            ])
    
    elif item_type == "material":
        if elem_name == "electric":
            templates.extend([
                f"They say '{renamed}' crackles with tiny sparks of high-voltage energy.",
                f"Crafters use '{renamed}' to infuse weaponry with lightning power.",
            ])
        elif elem_name == "fire":
            templates.extend([
                f"'{renamed}' feels warm to the touch, containing raw thermal energy.",
                f"Forgemasters value '{renamed}' for binding fire elements into weapons.",
            ])
        elif elem_name == "water":
            templates.extend([
                f"'{renamed}' glistens like pure condensed liquid essence.",
                f"Alchemists say '{renamed}' carries the fluid properties of water.",
            ])
        elif elem_name == "nature":
            templates.extend([
                f"'{renamed}' smells of fresh forest growth and flora essence.",
                f"Craftsmen blend '{renamed}' when fashioning nature-attuned gear.",
            ])
        elif elem_name == "ice":
            templates.extend([
                f"'{renamed}' remains perpetually cold as frost and never melts.",
                f"Artisans use '{renamed}' to chill materials during elemental forging.",
            ])
        elif elem_name == "earth":
            templates.extend([
                f"'{renamed}' is heavy and dense, composed of solid telluric stone.",
                f"Forges utilize '{renamed}' to add tectonic durability to weapons.",
            ])
        elif elem_name == "light":
            templates.extend([
                f"'{renamed}' glows faintly with pure solar light.",
                f"Priests describe '{renamed}' as a luminous shard of energy.",
            ])
        elif elem_name == "dark":
            templates.extend([
                f"'{renamed}' absorbs surrounding light like shadow dust.",
                f"Umbral crafters seek '{renamed}' for void elemental recipes.",
            ])
        elif original == "Weapon Prototype":
            templates.extend([
                f"'{renamed}' is a blank metal frame, essential for forging weapons.",
                f"Smiths use '{renamed}' as the core foundation for weapon crafting.",
            ])
        elif original == "Magic Catalyst":
            templates.extend([
                f"'{renamed}' acts as a potent magic catalyst, vital for advanced recipes.",
                f"Alchemists require '{renamed}' to stabilize high-tier elemental crafting.",
            ])
        elif original == "Enchanted Cloth":
            templates.extend([
                f"'{renamed}' is woven with mystic runes, used to bind elemental armaments.",
                f"Tailors describe '{renamed}' as a runic fabric for magical weapons.",
            ])

    if not templates:
        templates = [
            f"Local merchants rebrand items like '{renamed}' to attract traveling adventurers.",
            f"If you ever find '{renamed}', remember its unique elemental properties.",
            f"Legends mention '{renamed}' as an item of ancient origins.",
        ]

    return random.choice(templates)


class Game:
    """
    Main game manager that handles game state, level progression,
    and player interactions.
    """
    
    def __init__(self, 
                 mode: GameMode = GameMode.EASY,
                 seed: Optional[int] = None,
                 shuffle_container=False,
                 single_level_enemy=1,
                 shuffle_enemy=False,
                 reversible=True,
                 item_rename=False,
                 neat=False):
        """
        Initialize a new game.
        
        Args:
            mode: Game mode (EASY or HARD)
            seed: Random seed for reproducibility (optional)
        """
        if seed is not None:
            set_seed(seed)
        self.seed = seed
        self.mode = mode
        self.player = Player()
        self.current_level_index = 0
        self.levels: List[Level] = []
        self.game_completed = False
        self.game_over = False

        self.shuffle_container = shuffle_container
        self.single_level_enemy = single_level_enemy
        self.shuffle_enemy = shuffle_enemy
        self.reversible = reversible
        self.item_name = item_rename
        self.renamed_items = {}
        self.neat = neat

        # Initialize starting inventory with random items
        self._initialize_player_inventory()
        
        # Generate the game levels
        self._generate_levels()
        self.reset_player_hp()
        return
    
    def apply_dynamics(self):
        self.shuffle_items()
        self.apply_renames()

    def apply_renames(self):
        if not self.item_name:
            return

        # -----------------------------
        # Step 1: Sample renamed subset and assign aliases
        # -----------------------------
        # Define item categories in RENAME_MAP
        from envs.cuterpg.RoguelikeRPG.constants import STANDARD_WEAPONS, ADVANCED_WEAPONS
        
        all_weapon_keys = list(STANDARD_WEAPONS.keys()) + list(ADVANCED_WEAPONS.keys())
        all_basic_keys = [k for k in RENAME_MAP.keys() if k not in all_weapon_keys and "Enhancer" not in k]

        # -----------------------------
        # Part A: Select 3 Basic Materials
        # -----------------------------
        required_basic = [k for k in self.solution_manager.required_items.keys() if k in all_basic_keys and k in RENAME_MAP]
        random.shuffle(required_basic)

        # Prioritize collectible items (starting inv has fewer than required)
        collectible_basic = []
        for k in required_basic:
            needed_qty = self.solution_manager.required_items[k]
            item = self.player.inventory.get_item_by_name(k)
            have_qty = item.count if item else 0
            if have_qty < needed_qty:
                collectible_basic.append(k)

        selected_basic = collectible_basic[:3]
        for k in required_basic:
            if len(selected_basic) >= 3:
                break
            if k not in selected_basic:
                selected_basic.append(k)

        # Supplement with noise basic materials if fewer than 3
        if len(selected_basic) < 3:
            basic_pool = [k for k in all_basic_keys if k in RENAME_MAP and k not in selected_basic]
            needed = 3 - len(selected_basic)
            selected_basic.extend(random.sample(basic_pool, min(needed, len(basic_pool))))

        # -----------------------------
        # Part B: Select 1 Medium/Advanced Weapon
        # -----------------------------
        solution_elem = getattr(self.solution_manager, "solution_element", None)
        solution_weapon_candidates = []
        if solution_elem:
            for w_name, elem in STANDARD_WEAPONS.items():
                if elem == solution_elem and w_name in RENAME_MAP:
                    solution_weapon_candidates.append(w_name)
            for w_name, elem in ADVANCED_WEAPONS.items():
                if elem == solution_elem and w_name in RENAME_MAP:
                    solution_weapon_candidates.append(w_name)

        if solution_weapon_candidates:
            selected_weapon = [random.choice(solution_weapon_candidates)]
        else:
            weapon_pool = [k for k in all_weapon_keys if k in RENAME_MAP]
            selected_weapon = [random.choice(weapon_pool)]

        # Combine: Exactly 3 basic materials + 1 medium/advanced weapon (Total 4 items)
        selected_keys = selected_basic + selected_weapon

        # Final renamed_items dict
        self.renamed_items = {
            k: random.choice(RENAME_MAP[k]) for k in selected_keys
        }

        for key, val in self.renamed_items.items():
            print(f"{key} -> {val}")

        # Rename starting inventory items
        for item in self.player.inventory.items:
            if item.name in self.renamed_items:
                item.display_name = self.renamed_items[item.name]

        # -----------------------------
        # Step 2: Apply display_name to all relevant items
        # -----------------------------
        for level in self.levels:
            level.renamed_items = self.renamed_items
            # Containers
            if hasattr(level, "containers"):
                for container, container_info in level.containers.items():
                    item = container_info.get("item")
                    if item and item.name in self.renamed_items:
                        level.containers[container]['content_description'] = level.containers[container]['content_description'].replace(item.name, self.renamed_items[item.name])
                        item.display_name = self.renamed_items[item.name]

            # Collectibles
            if hasattr(level, "collectibles"):
                for collect_info in level.collectibles.values():
                    item = collect_info.get("item")
                    if item and item.name in self.renamed_items:
                        item.display_name = self.renamed_items[item.name]

            # Shops
            if hasattr(level, "for_sale"):
                for item_info in level.for_sale.values():
                    item = item_info["item"]
                    if item.name in self.renamed_items:
                        item.display_name = self.renamed_items[item.name]

            # Enemies
            if hasattr(level, "enemies") and level.enemies:
                for enemy in level.enemies:
                    for drop in enemy.drops:
                        if isinstance(drop, Item) and drop.name in self.renamed_items:
                            drop.display_name = self.renamed_items[drop.name]
            if hasattr(level, "enemy") and level.enemy:
                for drop in level.enemy.drops:
                    if isinstance(drop, Item) and drop.name in self.renamed_items:
                        drop.display_name = self.renamed_items[drop.name]

        # -----------------------------
        # Step 3: Add hint lines to NPCs or Readables
        # Each renamed item hint appears exactly once, scattered across distinct slots (NPC/readable/shopkeeper).
        # -----------------------------
        def gen_hint_text(k, v):
            return generate_hint_text(k, v)

        def append_hint_text(original_text: str, hint_text: str) -> str:
            if not original_text:
                return f'"{hint_text}"'
            original_text = original_text.strip()
            if original_text.endswith('"'):
                return f'{original_text[:-1]} {hint_text}"'
            else:
                return f'{original_text} {hint_text}'

        # Collect all available text slots across all levels
        all_slots = []
        for level in self.levels:
            if level.level_type == "shop":
                all_slots.append(("shopkeeper", level, None))
            if hasattr(level, 'npcs'):
                for npc in level.npcs:
                    all_slots.append(("npc", level, npc))
            if hasattr(level, 'readables'):
                for r in level.readables:
                    all_slots.append(("readable", level, r))

        random.shuffle(all_slots)

        # Distribute each renamed item's hint to a unique slot
        items_to_hint = list(self.renamed_items.items())
        random.shuffle(items_to_hint)

        for k, v in items_to_hint:
            if not all_slots:
                break
            typ, level, key = all_slots.pop()
            text = gen_hint_text(k, v)
            if typ == "npc":
                level.npcs[key]['dialog'] = append_hint_text(level.npcs[key]['dialog'], text)
            elif typ == "shopkeeper":
                shop_dialog = getattr(level, 'shopkeeper_dialog', '"Welcome to my shop! Feel free to browse my wares."')
                level.shopkeeper_dialog = append_hint_text(shop_dialog, text)
            elif typ == "readable":
                level.readables[key]['content'] = append_hint_text(level.readables[key]['content'], text)

        return
 

    def shuffle_items(self):
        """
        Shuffle container contents in a random growth level or enemy drops if enabled.
        """
        # -----------------------------
        # 1. Shuffle one growth level's containers
        # -----------------------------
        if self.shuffle_container:
            # Find all growth levels with collectibles or containers
            growth_levels = [lvl for lvl in self.levels if lvl.level_type == "growth"]
            if len(growth_levels) >= 2:
                chosen_levels = random.sample(growth_levels, k=2)
                for chosen_level in chosen_levels:
                    # 1. Gather all item names currently in level
                    all_item_values = []
                    for name, info in chosen_level.collectibles.items():
                        if info.get("item") is not None:
                            all_item_values.append(info["item"].name)
                        else:
                            all_item_values.append(None)
                    for name, info in chosen_level.containers.items():
                        if info.get("item") is not None:
                            all_item_values.append(info["item"].name)
                        else:
                            all_item_values.append(None)

                    # 2. Check if a value-based derangement is mathematically possible
                    n_total = len(all_item_values)
                    if n_total > 1:
                        from collections import Counter
                        counts = Counter(all_item_values)
                        max_val = max(counts.values())
                        if max_val > n_total / 2:
                            # Calculate how many additional unique collectibles we need
                            d_needed = 2 * max_val - n_total
                            existing_names = {x for x in all_item_values if x is not None}
                            
                            themed_pool = {
                                "forest": ["fallen branch", "colorful mushroom", "strange berry", "shiny rock"],
                                "cave": ["glowing crystal", "strange fungus", "ancient coin", "bat droppings"],
                                "ruins": ["stone fragment", "rusty key", "worn statue", "faded scroll"],
                                "village": ["discarded tool", "woven basket", "clay pot", "wooden toy"],
                                "mountain": ["eagle feather", "sharp stone", "hardy plant", "snow crystal"],
                                "beach": ["seashell", "smooth pebble", "driftwood", "crab shell"],
                                "swamp": ["twisted root", "glowing moss", "murky water sample", "strange flower"],
                                "temple": ["prayer bead", "incense stick", "ceremonial knife", "offering bowl"],
                                "meadow": ["wildflower", "honeycomb", "bird feather", "rabbit fur"],
                                "castle": ["iron nail", "tapestry scrap", "coat of arms", "candle stub"]
                            }
                            generic_pool = ["strange object", "curious item", "mysterious artifact", "old boot", "rusty nail", "dusty book"]
                            pool = themed_pool.get(chosen_level.theme, generic_pool)
                            available_junk = [item_name for item_name in pool if item_name not in existing_names]
                            
                            # Top up with base materials if needed
                            for mat in list(BASE_MATERIALS.keys()):
                                if len(available_junk) >= d_needed:
                                    break
                                if mat not in existing_names and mat not in available_junk:
                                    available_junk.append(mat)
                                    
                            # Add generic items if we still need more
                            idx = 1
                            while len(available_junk) < d_needed:
                                candidate = f"curious item {idx}"
                                if candidate not in existing_names and candidate not in available_junk:
                                    available_junk.append(candidate)
                                idx += 1
                                
                            for item_name in available_junk[:d_needed]:
                                add_item(item_name, chosen_level.collectibles, chosen_level.theme)

                    # Gather all available items (collectibles + unopened container items)
                    all_items = []
                    for name, info in chosen_level.collectibles.items():
                        all_items.append(info["item"])

                    # Container items
                    for name, info in chosen_level.containers.items():
                        all_items.append(info["item"])

                    if len(all_items) <= 1:
                        continue  # nothing to shuffle

                    # Shuffle all items
                    all_items = derangement(all_items)

                    idx = 0
                    collectibles_size = len(chosen_level.collectibles)
                    chosen_level.collectibles = {}
                    for _ in range(collectibles_size):
                        item = all_items[idx]
                        if item is not None:
                            key_name = item.name
                            k_idx = 1
                            while key_name in chosen_level.collectibles:
                                key_name = f"{item.name}_{k_idx}"
                                k_idx += 1
                            display_name = getattr(item, 'display_name', '') or item.name
                            locations = [
                                "on the ground",
                                "partially hidden under some debris",
                                "glowing faintly in a corner",
                                "tucked away in a crevice",
                                "just lying there in plain sight"
                            ]
                            chosen_level.collectibles[key_name] = {
                                "description": f"You see a {display_name} {random.choice(locations)}.",
                                "item": item
                            }
                        idx += 1

                    for container in chosen_level.containers:
                        item = all_items[idx]
                        if item is not None:
                            display_name = getattr(item, 'display_name', '') or item.name
                            chosen_level.containers[container] = {
                                "description": f"There's a {container} that might contain something useful.",
                                "opened": False,
                                "content_description": f"You found a {display_name} inside!",
                                "item": item
                            }
                        else:
                            chosen_level.containers[container] = {
                                "description": f"There's a {container} that might contain something useful.",
                                "opened": False,
                                "content_description": "It's empty. Nothing useful inside.",
                                "item": None
                            }
                        idx += 1

                    chosen_level.interactions = {
                        **chosen_level.collectibles,
                        **chosen_level.containers,
                        **chosen_level.npcs,
                        **chosen_level.readables,
                    }
        # -----------------------------
        # 2. Shuffle enemy drops
        # -----------------------------
        if self.shuffle_enemy:
            combat_levels = [lvl for lvl in self.levels if lvl.level_type == "combat"]
            if combat_levels:
                chosen_level = random.choice(combat_levels)
                if chosen_level.enemies:
                    enemy_drop_lists = [list(enemy.drops) for enemy in chosen_level.enemies]
                    flat_drops = [drop for drops in enemy_drop_lists for drop in drops]
                    if len(flat_drops) > 1:
                        shuffled_drops = derangement(flat_drops)
                        idx = 0
                        for enemy, drops in zip(chosen_level.enemies, enemy_drop_lists):
                            enemy.drops = shuffled_drops[idx: idx + len(drops)]
                            idx += len(drops)

    
    def _initialize_player_inventory(self):
        """Initialize the player's inventory with some starting items."""
        # Add a random elemental material
        
        possible_materials = list(BASE_MATERIALS.keys())
        
        # Pick a random elemental material
        material_name = random.choice(possible_materials)
        element = BASE_MATERIALS[material_name]
        description = f"A basic crafting material with {element.value if element else 'no'} elemental properties."
        material = create_material(material_name, description, element)
        self.player.add_to_inventory(material)
        
        # Add a Weapon Prototype
        prototype = create_material("Weapon Prototype", "A universal crafting material used for creating weapons.")
        self.player.add_to_inventory(prototype)
        
        # 50% chance to add a second material
        if random.random() < 0.5:
            # Make sure it's different from the first one
            remaining_materials = [m for m in possible_materials if m != material_name]
            second_material_name = random.choice(remaining_materials)
            element = BASE_MATERIALS[second_material_name]
            description = f"A basic crafting material with {element.value if element else 'no'} elemental properties."
            second_material = create_material(second_material_name, description, element)
            self.player.add_to_inventory(second_material)
            
        # print(f"[INIT] Inventory after initialization:\n{self.player.inventory}")
        return 
    
    def _generate_levels(self):
        """Generate all levels for the game based on the selected mode."""
        # Determine the level sequence based on game mode

        if self.mode == GameMode.EASY:
            level_types = EASY_MODE_LAYERS
        else:
            level_types = HARD_MODE_LAYERS
        
        # Plan enemy elements to ensure variety and progression
        all_elements = list(Element)
        boss_element = random.choice(all_elements)
        
        # For hard mode, also plan a mini-boss element different from the final boss
        if self.mode == GameMode.HARD:
            miniboss_element_options = [e for e in all_elements if e != boss_element]
            miniboss_element = random.choice(miniboss_element_options)
        else:
            miniboss_element = None
        
        # Create levels based on the sequence
        self.levels = []
        next_enemy_type = None  # Track the next enemy type for hints
        
        for i, level_type in enumerate(level_types):
            level_number = i + 1
            # print("Random check:", random.random(), np.random.rand())
            
            # Determine next enemy type for hints
            if i < len(level_types) - 1:
                next_type = level_types[i + 1]
                if next_type == "combat":
                    # Generate a random enemy type for hint
                    element = random.choice(all_elements)
                    #element = boss_element
                    print(f"current element:{element}")
                    from envs.cuterpg.RoguelikeRPG.constants import ENEMY_TYPES
                    enemy_types = ENEMY_TYPES.get(element, ["Monster"])
                    next_enemy_type = random.choice(enemy_types)
                elif next_type == "miniboss":
                    next_enemy_type = f"{miniboss_element.value} Champion"
                elif next_type == "boss":
                    from envs.cuterpg.RoguelikeRPG.constants import BOSS_NAMES
                    next_enemy_type = BOSS_NAMES.get(boss_element, f"Ancient {boss_element.value} Destroyer")
                else:
                    next_enemy_type = None
            
            # Create the appropriate level type
            if level_type == "growth":
                level = GrowthLevel(level_number, 
                                    next_enemy_hint=next_enemy_type,
                                    reversible=self.reversible,
                                    item_rename=self.item_name)
            elif level_type == "combat":
                # Choose a random element for the enemy
                other_elems = [e for e in all_elements if e != boss_element]
                # enemy_elements = random.choice(other_elems, self.single_level_enemy)
                enemy_elements = random.choices(other_elems, k=self.single_level_enemy)
                level = CombatLevel(level_number, 
                                    difficulty=1, 
                                    enemy_elements=enemy_elements,
                                    enemy_num = self.single_level_enemy,
                                    reversible=self.reversible)
            elif level_type == "miniboss":
                level = BossLevel(level_number, 
                                  is_final_boss=False, 
                                  boss_element=miniboss_element,
                                  reversible=self.reversible)
            elif level_type == "shop":
                level = ShopLevel(level_number, 
                                  next_enemy_hint=next_enemy_type,
                                  reversible=self.reversible)
            # elif level_type == "crafting":
            #     level = CraftingLevel(level_number, next_enemy_hint=next_enemy_type)
            elif level_type == "boss":
                level = BossLevel(level_number, 
                                  is_final_boss=True, 
                                  boss_element=boss_element,
                                  reversible=self.reversible)
            else:
                # Default to a growth level if the type is unknown
                level = GrowthLevel(level_number,
                                    reversible=self.reversible,
                                    item_rename=self.item_name)
            
            self.levels.append(level)
        
        # Now that all levels are created, use the solution manager to ensure the game is solvable
        # print(self.levels)
        solution_manager = SolutionManager(self.levels, boss_element, self.player.inventory)
        self.solution_element = solution_manager.distribute_required_items()
        
        # Add hints about the boss's weaknesses
        solution_manager.add_hints_about_boss(len(self.levels) - 1)
        self.solution_manager = solution_manager
        # print("Random check:", random.random(), np.random.rand())
        for level in self.levels:
            level.neat = self.neat
        return
    
    def start(self) -> str:
        """
        Start the game and enter the first level.
        
        Returns:
            str: Initial game state description
        """
        # Make sure we're at the beginning
        self.current_level_index = 0
        self.game_completed = False
        self.game_over = False
        
        # Get the first level
        current_level = self.get_current_level()
        
        # Enter the first level
        level_description = current_level.enter(self.player)
        self.level_descripion = level_description
        
        # Create the opening message
        mode_name = "Easy Mode" if self.mode == GameMode.EASY else "Hard Mode"
        opening = f"Welcome to RougelikeRPG ({mode_name})!\n\n"
        inventory = f"Your starting inventory:\n{self.player.inventory}\n\n"
        self.opening = opening
        
        return f"{opening}{inventory}You are now entering Level 1: {current_level.level_type.capitalize()}\n\n{level_description}"

    
    def get_current_level(self) -> Level:
        """
        Get the current level object.
        
        Returns:
            Level: The current level
        """
        return self.levels[self.current_level_index]
    
    def process_action(self, action: str, *args) -> Dict[str, Any]:
        """
        Process a player action.
        
        Args:
            action: The action to take
            args: Additional arguments for the action
            
        Returns:
            Dict[str, Any]: Result of the action
        """
        # Check if the game is over
        if self.game_over:
            return {"success": False, "message": "Game over! You have been defeated."}
        
        if self.game_completed:
            return {"success": False, "message": "Congratulations! You have completed the game."}
        
        # Get the current level
        current_level = self.get_current_level()
        
        # Process the action in the current level
        result = current_level.process_action(self.player, action, *args)
        
        # Check if the player is still alive
        if not self.player.is_alive:
            self.game_over = True
            result["game_over"] = True
            result["message"] += "\n\nYou have been defeated! Game over."
            return result
        
        # Check if the level has been completed
        if current_level.back:
            self.get_current_level().completed = False
            self.get_current_level().back = False
            self.current_level_index -= 1
            next_level = self.get_current_level()
            next_level.completed = False
            next_level.back = False
            next_level_description = next_level.enter(self.player)
            self.level_descripion = next_level_description

            # result["next_level"] = True 
            result["next_level_number"] = next_level.level_number
            result["next_level_type"] = next_level.level_type
            result["next_level_description"] = next_level_description
            result["message"] += f"\n\nYou are now back to Level {next_level.level_number}: {next_level.level_type.capitalize()}.\n\n{next_level_description}"

        elif current_level.completed:
            # Move to the next level if available
            if self.current_level_index < len(self.levels) - 1:
                self.current_level_index += 1
                next_level = self.get_current_level()
                
                # Enter the next level
                next_level_description = next_level.enter(self.player)
                self.level_descripion = next_level_description
                
                result["next_level"] = True
                result["next_level_number"] = next_level.level_number
                result["next_level_type"] = next_level.level_type
                result["next_level_description"] = next_level_description
                result["message"] += f"\n\nYou proceed to Level {next_level.level_number}: {next_level.level_type.capitalize()}.\n\n{next_level_description}"
            else:
                # Game completed!
                self.game_completed = True
                result["game_completed"] = True
                result["message"] += "\n\nCongratulations! You have completed the game and proven yourself a worthy adventurer!"
        
        return result
    
    def get_game_state(self) -> Dict[str, Any]:
        """
        Get the current state of the game.
        
        Returns:
            Dict[str, Any]: Current game state
        """
        current_level = self.get_current_level()
        
        state = {
            "game_mode": self.mode.name,
            "current_level_number": current_level.level_number,
            "current_level_type": current_level.level_type,
            "levels_completed": self.current_level_index,
            "total_levels": len(self.levels),
            "player_hp": f"{self.player.current_hp}/{self.player.max_hp}",
            "player_inventory": str(self.player.inventory),
            "equipped_weapon": str(self.player.equipped_weapon) if self.player.equipped_weapon else "None",
            "game_completed": self.game_completed,
            "game_over": self.game_over,
            "available_actions": current_level.get_available_actions(self.player)
        }
        
        return state
    
    def verify_solvability(self) -> Dict[str, Any]:
        """
        Verify that this game is solvable.
        
        Returns:
            Dict[str, Any]: Verification results
        """
        from envs.cuterpg.RoguelikeRPG.utils.game_verification import EnhancedGameVerification
        return EnhancedGameVerification.verify_game_solvability(self)
    

    def reset_player_hp(self):
        weapons = self.solution_manager.expected_weapons
        # print(weapons)
        total_hp = 0
        for idx, level in enumerate(self.levels):
            if level.level_type == 'combat':
                hp_drops = []
                for enemy in level.enemies:
                   turns, total_damage_taken = enemy.simulate_battle(weapons[idx])
                   hp_drops.append(total_damage_taken)
                total_hp += sum(hp_drops)
            elif level.level_type == 'boss':
                turns, total_damage_taken = level.enemy.simulate_battle(weapons[idx])
                total_hp += total_damage_taken

        self.player.max_hp = total_hp + 1
        self.player.current_hp = self.player.max_hp
        return
    
    def run_interactive(self):
        """
        Run the game in interactive mode, accepting commands from stdin.
        """
        # print(self.start())
        
        while not self.game_completed and not self.game_over:
            # Display the current level and available actions
            current_level = self.get_current_level()
            print(f"\nCurrent Level: {current_level.level_number} ({current_level.level_type.capitalize()})")
            print(f"Available actions: {', '.join(current_level.available_actions)}")
            print(f"HP: {self.player.current_hp}/{self.player.max_hp} | Equipped: {self.player.equipped_weapon if self.player.equipped_weapon else 'Nothing'}")
            
            # Show available interaction objects in the current level
            if hasattr(current_level, 'interactions') and current_level.interactions:
                print("\nThings you can interact with:")
                for obj_name, obj_info in current_level.interactions.items():
                    if "description" in obj_info:
                        print(f"- {obj_name}: {obj_info['description']}")
                    else:
                        print(f"- {obj_name}")
            
            # In combat levels, show enemy information
            if current_level.level_type in ["combat", "boss"] and hasattr(current_level, 'enemy') and current_level.enemy:
                print(f"\nEnemy: {current_level.enemy}")
            
            # Get player input
            try:
                command = input("\nWhat would you like to do? ").strip()
                
                # Exit the game if requested
                if command.lower() in ["exit", "quit"]:
                    print("Thanks for playing RougelikeRPG!")
                    break
                
                # Special handling for common command patterns
                # First try to split by space to get action
                parts = command.split(' ', 1)
                action = parts[0].lower()
                
                # Handle the argument part - we need to be flexible with how people input item names
                args = []
                if len(parts) > 1:
                    arg_text = parts[1].strip()
                    
                    # Remove brackets if they're present
                    if (arg_text.startswith('[') and arg_text.endswith(']')):
                        arg_text = arg_text[1:-1].strip()
                    
                    args = [arg_text]
                
                # Process the action
                result = self.process_action(action, *args)
                
                # Display the result
                print(f"\n{result['message']}")
                
                # Display additional content if available
                if "content" in result:
                    print(f"\n{result['content']}")
                
                # Check if the game has ended
                if self.game_completed or self.game_over:
                    break
                
            except EOFError:
                print("\nGame terminated by user.")
                break
            except KeyboardInterrupt:
                print("\nGame terminated by user.")
                break
            except Exception as e:
                print(f"\nAn error occurred: {e}")
        
        # Game end message
        if self.game_completed:
            print("\nCongratulations! You have completed the game!")
        elif self.game_over:
            print("\nGame over! You have been defeated.")