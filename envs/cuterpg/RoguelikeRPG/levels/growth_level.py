"""
Growth (resource gathering) level for the RougelikeRPG game.
"""
import random
from typing import List, Dict, Any, Tuple, Optional, Set
# from envs.cuterpg.RoguelikeRPG.levels.level import Level
from envs.cuterpg.RoguelikeRPG.levels.crafting_level import CraftingLevel
from envs.cuterpg.RoguelikeRPG.entities.player import Player
from envs.cuterpg.RoguelikeRPG.entities.item import Item, Material, create_material
from envs.cuterpg.RoguelikeRPG.constants import Element, BASE_MATERIALS
from envs.cuterpg.RoguelikeRPG.systems.crafting import CraftingSystem
from .utils import add_item
from pdb import set_trace as st

class GrowthLevel(CraftingLevel):
    """
    A level focused on gathering resources and information.
    
    Players can explore, find items, and gather intelligence about
    upcoming enemies.
    """
    
    def __init__(self, 
                 level_number: int, 
                 next_enemy_hint: Optional[str] = None,
                 reversible=False,
                 item_rename=False):
        self.item_rename = item_rename
        super().__init__(level_number, "growth", next_enemy_hint, reversible=reversible)
        self.available_actions = [
            "open",     # Open a container
            "talk",     # Talk to an NPC
            # "discard",  # Discard an item
            "read",     # Read an item or sign
        ] + self._get_common_actions()
        
        self.next_enemy_hint = next_enemy_hint
        self.collectibles = {}    # Items that can be collected
        self.containers = {}      # Objects that can be opened
        self.npcs = {}            # NPCs that can be talked to
        self.readables = {}       # Things that can be read

        # Generate the level content
        self._generate_level_content()
    
    def _generate_level_content(self):
        """Generate the random content for this level."""
        # Generate a random environment theme
        environment_themes = [
            "forest", "cave", "ruins", "village", "mountain",
            "beach", "swamp", "temple", "meadow", "castle"
        ]
        self.theme = random.choice(environment_themes)
        
        # Create the level description based on the theme
        self.description = self._generate_description()
        
        # Generate collectible items (2-4 items)
        self._generate_collectibles(random.randint(2, 4))
        
        # Generate containers (1-2 containers)
        self._generate_containers(random.randint(2, 3), item_rename=self.item_rename)
        
        # Generate NPCs (0-2 NPCs)
        self._generate_npcs(random.randint(1, 2))
        
        # Generate readable objects (1-3 readables)
        self._generate_readables(random.randint(1, 3))
        
        # Add everything to the interactions dict
        self.interactions = {
            **self.collectibles,
            **self.containers,
            **self.npcs,
            **self.readables
        }
    
    def _generate_description(self) -> str:
        """Generate a description for the level based on its theme."""
        descriptions = {
            "forest": "You find yourself in a lush forest with tall trees.",
            "cave": "You enter a dark, damp cave. ",
            "ruins": "Ancient stone ruins surround you, their once-grand architecture now crumbling with age. ",
            "village": "You arrive at a small village with thatched-roof cottages.",
            "mountain": "The mountain path is steep and rocky.",
            "beach": "Warm sand squishes between your toes as you walk along the shoreline.",
            "swamp": "The swamp is humid and foggy.",
            "temple": "Ornate columns line the interior of this ancient temple.",
            "meadow": "A vast meadow stretches before you.",
            "castle": "The massive stone castle looms above you."
        }
        
        base_description = descriptions.get(self.theme, "You find yourself in a mysterious location filled with possibilities.")
        
        hint = ""
        if self.next_enemy_hint:
            hints = [
                f"You notice signs that a {self.next_enemy_hint} has passed through recently.",
                f"A local warns you about a {self.next_enemy_hint} in the area.",
                f"You find tracks that seem to belong to a {self.next_enemy_hint}.",
                f"There are rumors circulating about a {self.next_enemy_hint} nearby.",
                f"You spot damage that could only have been caused by a {self.next_enemy_hint}."
            ]
            hint = f" {random.choice(hints)}"
            
        return f"{base_description}{hint} What would you like to do?"
    
    def _generate_collectibles(self, count: int):
        """Generate collectible items."""
        # Possible collectible items by theme
        collectibles_by_theme = {
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
        
        # Get theme-appropriate collectibles
        theme_collectibles = collectibles_by_theme.get(self.theme, ["strange object", "curious item", "mysterious artifact"])
        
        # Add random element-based materials
        element_materials = list(BASE_MATERIALS.keys())
        potential_collectibles = theme_collectibles + element_materials
        
        # Generate the specified number of unique collectibles
        selected_collectibles = random.sample(potential_collectibles, min(count, len(potential_collectibles)))
        
        for item_name in selected_collectibles:
            # Check if it's an element material
            add_item(item_name, self.collectibles, self.theme)
            
    
    def _placed_item_names(self):
        """Item names already placed in collectibles or containers on this level."""
        names = set()
        for info in self.collectibles.values():
            item = info.get("item")
            if item is not None:
                names.add(item.name)
        for info in self.containers.values():
            item = info.get("item")
            if item is not None:
                names.add(item.name)
        return names

    def _generate_containers(self, count: int, item_rename: bool = False):
        """Generate containers that can be opened."""
        # Possible containers by theme
        containers_by_theme = {
            "forest": ["hollow tree", "bird nest", "animal burrow", "rotting log"],
            "cave": ["rock pile", "crystal formation", "stalagmite", "bat nest"],
            "ruins": ["stone chest", "sarcophagus", "collapsed pillar", "hidden compartment"],
            "village": ["abandoned cart", "barrel", "crate", "storage chest"],
            "mountain": ["eagle nest", "crevice", "small cave", "snow drift"],
            "beach": ["tide pool", "washed up chest", "abandoned boat", "sand mound"],
            "swamp": ["hollow stump", "submerged chest", "giant flower", "mud mound"],
            "temple": ["offering box", "sacred chest", "hidden compartment", "ancient urn"],
            "meadow": ["fallen log", "rabbit hole", "dense thicket", "old stump"],
            "castle": ["treasure chest", "weapon rack", "wooden barrel", "supply crate"]
        }
        
        # Get theme-appropriate containers
        theme_containers = containers_by_theme.get(self.theme, ["mysterious container", "strange box", "unusual chest"])
        
        # Generate the specified number of unique containers
        selected_containers = random.sample(theme_containers, min(count, len(theme_containers)))
        
        used_item_names = self._placed_item_names()
        for container_name in selected_containers:
            # Each container has a 60% chance to contain a valuable item
            if random.random() < 0.6:
                # Determine what's inside (avoid duplicating items already on this level)
                possible_contents = [
                    name for name in list(BASE_MATERIALS.keys()) + [
                        "Weapon Prototype", "Magic Catalyst", "Enchanted Cloth"
                    ]
                    if name not in used_item_names
                ]
                if not possible_contents:
                    self.containers[container_name] = {
                        "description": f"There's a {container_name} that might contain something useful.",
                        "opened": False,
                        "content_description": "It's empty. Nothing useful inside.",
                        "item": None
                    }
                    continue
                content_name = random.choice(possible_contents)
                used_item_names.add(content_name)
                
                if content_name in BASE_MATERIALS:
                    element = BASE_MATERIALS[content_name]
                    description = f"A basic crafting material with {element.value if element else 'no'} elemental properties."
                    item = create_material(content_name, description, element)
                else:
                    # Generic crafting material
                    description = f"A universal crafting material used in many recipes."
                    item = create_material(content_name, description)
                
                self.containers[container_name] = {
                    "description": f"There's a {container_name} that might contain something useful.",
                    "opened": False,
                    "content_description": f"You found a {content_name} inside!",
                    "item": item
                }
            else:
                # Empty container
                self.containers[container_name] = {
                    "description": f"There's a {container_name} that might contain something useful.",
                    "opened": False,
                    "content_description": "It's empty. Nothing useful inside.",
                    "item": None
                }

        if item_rename:
            # We want to add exactly 2 empty containers.
            # Get theme-appropriate containers that aren't already in self.containers
            available = [c for c in theme_containers if c not in self.containers]
            # If not enough, draw from generic container names
            generic_containers = ["old crate", "dusty barrel", "cracked urn", "iron chest", "wooden box", "ancient vase", "moldy box"]
            for gc in generic_containers:
                if len(available) >= 2:
                    break
                if gc not in self.containers:
                    available.append(gc)
            
            # Select exactly 2 empty containers to add
            empty_containers_to_add = random.sample(available, min(2, len(available)))
            for container_name in empty_containers_to_add:
                self.containers[container_name] = {
                    "description": f"There's a {container_name} that might contain something useful.",
                    "opened": False,
                    "content_description": "It's empty. Nothing useful inside.",
                    "item": None
                }
    
    def _generate_npcs(self, count: int):
        """Generate NPCs that can be talked to."""
        # Possible NPCs by theme
        npcs_by_theme = {
            "forest": ["forest ranger", "hermit", "lost traveler", "woodcutter"],
            "cave": ["miner", "explorer", "cave dweller", "geologist"],
            "ruins": ["archaeologist", "treasure hunter", "historian", "ghost"],
            "village": ["shopkeeper", "blacksmith", "farmer", "village elder"],
            "mountain": ["climber", "shepherd", "mountain guide", "hermit"],
            "beach": ["fisherman", "sailor", "beachcomber", "lifeguard"],
            "swamp": ["witch", "frog hunter", "herbalist", "lost traveler"],
            "temple": ["priest", "acolyte", "pilgrim", "temple guardian"],
            "meadow": ["beekeeper", "shepherd", "botanist", "wanderer"],
            "castle": ["guard", "servant", "noble", "visiting dignitary"]
        }
        
        # Get theme-appropriate NPCs
        theme_npcs = npcs_by_theme.get(self.theme, ["mysterious stranger", "traveler", "wanderer"])
        
        # Generate the specified number of unique NPCs
        selected_npcs = random.sample(theme_npcs, min(count, len(theme_npcs)))
        
        for npc_name in selected_npcs:
            # Create dialog for the NPC
            # Each NPC has a chance to provide a hint about the next enemy
            if self.next_enemy_hint and random.random() < 0.7:  # 70% chance for a helpful NPC
                dialog = f"\"Be careful out there! I've heard there's a {self.next_enemy_hint} ahead. They're weak against certain elements, but I can't remember which ones...\""
            else:
                # Generic dialog based on theme
                dialog_options = {
                    "forest": [
                        "\"The forest is beautiful this time of year, isn't it?\"",
                        "\"Watch out for wild animals around here.\"",
                        "\"I've been collecting herbs for medicine.\"",
                    ],
                    "cave": [
                        "\"It's dark in these caves. Be careful where you step.\"",
                        "\"I'm looking for rare minerals. Have you seen any?\"",
                        "\"I've been mapping these tunnels for months.\"",
                    ],
                    # Add more dialog options for other themes...
                }
                
                theme_dialogs = dialog_options.get(
                    self.theme, 
                    ["\"Interesting to meet someone like you here.\"", 
                     "\"Safe travels on your journey.\"", 
                     "\"What brings you to these parts?\""]
                )
                dialog = random.choice(theme_dialogs)
            
            self.npcs[npc_name] = {
                "description": f"There's a {npc_name} here who might have useful information.",
                "dialog": dialog
            }
    
    def _generate_readables(self, count: int):
        """Generate objects that can be read."""
        # Possible readable objects by theme
        readables_by_theme = {
            "forest": ["carved tree", "moss-covered stone", "ranger's note", "old map"],
            "cave": ["wall carvings", "mineral guide", "explorer's journal", "warning sign"],
            "ruins": ["stone tablet", "ancient scroll", "wall inscription", "tattered book"],
            "village": ["notice board", "shopkeeper's ledger", "village records", "storybook"],
            "mountain": ["trail marker", "old journal", "summit log", "warning sign"],
            "beach": ["message in a bottle", "shipwreck log", "tidal chart", "weather warning"],
            "swamp": ["warning sign", "researcher's notes", "moldy book", "herb guide"],
            "temple": ["holy scripture", "prayer book", "wall inscription", "ritual guide"],
            "meadow": ["botanist's guide", "farmer's almanac", "weather stone", "trail marker"],
            "castle": ["royal decree", "family history", "knight's code", "tactical map"]
        }
        
        # Get theme-appropriate readable objects
        theme_readables = readables_by_theme.get(self.theme, ["mysterious inscription", "faded document", "strange symbols"])
        
        # Generate the specified number of unique readable objects
        selected_readables = random.sample(theme_readables, min(count, len(theme_readables)))
        
        for readable_name in selected_readables:
            # Create content for the readable object
            # Each readable has a chance to provide a hint about the next enemy
            if self.next_enemy_hint and random.random() < 0.6:  # 60% chance for useful info
                # Determine what element the enemy might be
                element_names = [e.name.lower() for e in Element]
                enemy_element = random.choice(element_names)
                
                content = f"\"...beware the {self.next_enemy_hint} that lurks ahead. Its {enemy_element} attacks are powerful, but it has weaknesses that can be exploited with the right weapons...\""
            else:
                # Generic content based on theme
                content_options = {
                    "forest": [
                        "\"The ancient trees of this forest have stood for centuries, watching over travelers.\"",
                        "\"Beware the dangers that lurk in the shadows between the trees.\"",
                        "\"Many have sought the treasures hidden in these woods. Few have found them.\"",
                    ],
                    "cave": [
                        "\"The deeper you go, the more wonders—and dangers—you'll find.\"",
                        "\"These caves were once home to a civilization long forgotten.\"",
                        "\"Mind your step and your head. The cave claims many careless adventurers.\"",
                    ],
                    # Add more content options for other themes...
                }
                
                theme_contents = content_options.get(
                    self.theme, 
                    ["\"An ancient power dwells in these lands...\"", 
                     "\"Many adventurers have passed this way before.\"", 
                     "\"The path ahead is fraught with danger, but also opportunity.\""]
                )
                content = random.choice(theme_contents)
            
            self.readables[readable_name] = {
                "description": f"There's a {readable_name} here with some writing on it.",
                "content": content
            }
    
    def enter(self, player: Player) -> str:
        """
        Called when the player enters this level.
        
        Args:
            player: The player entering the level
            
        Returns:
            str: A description of the level
        """
        # Get a description of available items in this level
        available_items = self.get_available_items_description()
        
        # Combine the level description with the available items
        full_description = f"{self.description}{available_items}"
        
        return full_description
    
    def get_curr_obs(self):
        available_items = self.get_available_items_description()
        
        # Combine the level description with the available items
        full_description = f"{self.description}{available_items}"
        
        return full_description
    
    def process_action(self, player: Player, action: str, *args) -> Dict[str, Any]:
        """
        Process a player action in this level.
        
        Args:
            player: The player
            action: The action being taken
            args: Additional arguments for the action
            
        Returns:
            Dict[str, Any]: The result of the action
        """
        action = action.lower()
        
        # Handle common actions
        if action in self._get_common_actions():
            return self.process_general_action(player, action, *args)
        
        if action == "collect":
            if len(args) == 0:
                return {"success": False, "message": "Collect what? Try 'collect [item name]'"}
            
            item_name = args[0]
            return self._collect_item(player, item_name)
        
        elif action == "open":
            if len(args) == 0:
                return {"success": False, "message": "Open what? Try 'open [container name]'"}
            
            container_name = args[0]
            return self._open_container(player, container_name)
        
        elif action == "talk":
            if len(args) == 0:
                return {"success": False, "message": "Talk to whom? Try 'talk [NPC name]'"}
            
            npc_name = args[0]
            return self._talk_to_npc(npc_name)
        
        elif action == "read":
            if len(args) == 0:
                return {"success": False, "message": "Read what? Try 'read [object name]'"}
            
            readable_name = args[0]
            return self._read_object(readable_name)
        
        else:
            return {"success": False, "message": f"Invalid action: {action}."}

    def get_available_actions(self, player: Player) -> List[str]:
        actions = []
        for key, info in self.containers.items():
            if not info.get('opened', False):
                actions.append(f"open {key}")
        for key in self.npcs:
            actions.append(f"talk {key}")
        for key in self.readables:
            actions.append(f"read {key}")
        return list(dict.fromkeys(actions + super().get_available_actions(player)))


    def _open_container(self, player: Player, container_name: str) -> Dict[str, Any]:
        """Open a container in the level."""
        # Check if the container exists
        if container_name not in self.containers:
            return {"success": False, "message": f"There is no {container_name} to open here."}
        
        container = self.containers[container_name]
        
        # Check if already opened
        if container["opened"]:
            return {"success": False, "message": f"You've already opened the {container_name}."}
        
        # Mark as opened
        container["opened"] = True
        
        # Get the contents
        item = container["item"]
        content_description = container["content_description"]
        
        # If there's an item, add it to inventory
        if item:
            success, message = player.add_to_inventory(item)
            
            if success:
                return {"success": True, "message": f"You opened the {container_name}. {content_description} {message}"}
            else:
                # drop the items to the ground
                display_name = self.renamed_items[item.name] if item.name in self.renamed_items else item.name
                add_item(item.name, self.collectibles, self.theme, display_name)
                # self.interactions.update(self.collectibles)
                return {"success": True, "message": f"You opened the {container_name}. {content_description} However, {message}, so it drops on the ground."}
        else:
            return {"success": True, "message": f"You opened the {container_name}. {content_description}"}
    
    def _talk_to_npc(self, npc_name: str) -> Dict[str, Any]:
        """Talk to an NPC in the level."""
        # Check if the NPC exists
        if npc_name not in self.npcs:
            return {"success": False, "message": f"There is no {npc_name} to talk to here."}
        
        npc = self.npcs[npc_name]
        dialog = npc["dialog"]
        
        return {"success": True, "message": f"You talk to the {npc_name}. They say: {dialog}"}
    
    
    def _read_object(self, readable_name: str) -> Dict[str, Any]:
        """Read a readable object in the level."""
        # Check if the readable exists
        if readable_name not in self.readables:
            return {"success": False, "message": f"There is no {readable_name} to read here."}
        
        readable = self.readables[readable_name]
        content = readable["content"]
        
        return {"success": True, "message": f"You read the {readable_name}. It says: {content}"}
    
    def can_exit(self, player: Player) -> Tuple[bool, str]:
        """
        Check if the player can exit this level.
        
        Args:
            player: The player
            
        Returns:
            Tuple[bool, str]: Whether the player can exit and a message
        """
        # Players can always exit a growth level
        return True, "You can leave this area and move on."
    

    def print_level(self):
        """Print important information about the growth level in a colorful and readable format using ANSI codes."""
        
        print_info = False
        if not print_info:
            return
        
        # Define basic colors
        RESET = "\033[0m"
        BOLD = "\033[1m"
        CYAN = "\033[96m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        BLUE = "\033[94m"
        MAGENTA = "\033[95m"
        WHITE = "\033[97m"
        LIGHT_GREEN = "\033[92m"
        LIGHT_CYAN = "\033[96m"
        LIGHT_MAGENTA = "\033[95m"
        LIGHT_YELLOW = "\033[93m"

        print(f"{CYAN}{BOLD}--- Growth Level {self.level_number} ---{RESET}")
        print(f"{GREEN}Environment Theme: {YELLOW}{self.theme.capitalize()}{RESET}")
        print(f"{GREEN}Description:{RESET}\n{self.description}\n")
        
        if self.next_enemy_hint:
            print(f"{RED}⚔️ Next Enemy Hint: {MAGENTA}{self.next_enemy_hint}{RESET}\n")
        
        print(f"{BLUE}Available Actions: {WHITE}{', '.join(self.available_actions)}{RESET}\n")
        
        if self.collectibles:
            print(f"{LIGHT_GREEN}Collectibles:{RESET}")
            for name, info in self.collectibles.items():
                print(f"  - {YELLOW}{name}{RESET}: {info['description']}")
            print()
            
        if self.containers:
            print(f"{LIGHT_CYAN}Containers:{RESET}")
            for name, info in self.containers.items():
                opened_status = "Opened" if info['opened'] else "Closed"
                print(f"  - {YELLOW}{name} ({opened_status}){RESET}: {info['description']}")
            print()
            
        if self.npcs:
            print(f"{LIGHT_MAGENTA}NPCs:{RESET}")
            for name, info in self.npcs.items():
                print(f"  - {YELLOW}{name}{RESET}: {info['description']}")
            print()
            
        if self.readables:
            print(f"{LIGHT_YELLOW}Readables:{RESET}")
            for name, info in self.readables.items():
                print(f"  - {YELLOW}{name}{RESET}: {info['description']}")
            print()
            
        print(f"{CYAN}{BOLD}--- End of Level Info ---{RESET}\n")