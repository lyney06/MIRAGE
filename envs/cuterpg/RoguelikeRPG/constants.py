"""
Constants and configurations for the RougelikeRPG game.
"""
import random
from enum import Enum, auto

# Game modes
class GameMode(Enum):
    EASY = auto()  # 6 layers
    HARD = auto()  # 8 layers

class Element(Enum):
    FIRE = "FIRE"
    WATER = "WATER"
    NATURE = "NATURE"
    LIGHT = "LIGHT"
    DARK = "DARK"
    ELECTRIC = "ELECTRIC"
    ICE = "ICE"
    EARTH = "EARTH"
    
    @classmethod
    def random(cls):
        """Returns a random element"""
        return random.choice(list(cls))

# Element effectiveness chart (attacker → defender)
# 2.0: Super effective, 1.0: Normal, 0.5: Not very effective, 0.0: Immune
ELEMENT_EFFECTIVENESS = {
    Element.FIRE: {
        Element.FIRE: 0.5,
        Element.WATER: 0.5,
        Element.NATURE: 2.0,
        Element.ICE: 2.0,
        Element.EARTH: 0.5,
        Element.LIGHT: 1.0,
        Element.DARK: 1.0,
        Element.ELECTRIC: 1.0,
    },
    Element.WATER: {
        Element.FIRE: 2.0,
        Element.WATER: 0.5,
        Element.NATURE: 0.5,
        Element.ICE: 0.5,
        Element.EARTH: 2.0,
        Element.LIGHT: 1.0,
        Element.DARK: 1.0,
        Element.ELECTRIC: 0.5,
    },
    Element.NATURE: {
        Element.FIRE: 0.5,
        Element.WATER: 2.0,
        Element.NATURE: 0.5,
        Element.ICE: 0.5,
        Element.EARTH: 2.0,
        Element.LIGHT: 1.0,
        Element.DARK: 1.0,
        Element.ELECTRIC: 1.0,
    },
    Element.ICE: {
        Element.FIRE: 0.5,
        Element.WATER: 0.5,
        Element.NATURE: 2.0,
        Element.ICE: 0.5,
        Element.EARTH: 2.0,
        Element.LIGHT: 1.0,
        Element.DARK: 1.0,
        Element.ELECTRIC: 1.0,
    },
    Element.EARTH: {
        Element.FIRE: 2.0,
        Element.WATER: 0.5,
        Element.NATURE: 0.5,
        Element.ICE: 0.5,
        Element.EARTH: 1.0,
        Element.LIGHT: 1.0,
        Element.DARK: 1.0,
        Element.ELECTRIC: 2.0,
    },
    Element.LIGHT: {
        Element.FIRE: 1.0,
        Element.WATER: 1.0,
        Element.NATURE: 1.0,
        Element.ICE: 1.0,
        Element.EARTH: 1.0,
        Element.LIGHT: 0.5,
        Element.DARK: 2.0,
        Element.ELECTRIC: 1.0,
    },
    Element.DARK: {
        Element.FIRE: 1.0,
        Element.WATER: 1.0,
        Element.NATURE: 1.0,
        Element.ICE: 1.0,
        Element.EARTH: 1.0,
        Element.LIGHT: 2.0,
        Element.DARK: 0.5,
        Element.ELECTRIC: 1.0,
    },
    Element.ELECTRIC: {
        Element.FIRE: 1.0,
        Element.WATER: 2.0,
        Element.NATURE: 1.0,
        Element.ICE: 1.0,
        Element.EARTH: 0.0,
        Element.LIGHT: 1.0,
        Element.DARK: 1.0,
        Element.ELECTRIC: 0.5,
    },
}

# Item tiers and weights
class ItemTier(Enum):
    BASIC = 1     # Basic materials (weight 2)
    STANDARD = 2  # Standard weapons (weight 3)
    ADVANCED = 3  # Advanced weapons (weight 5)

# Item weights by tier
ITEM_WEIGHTS = {
    ItemTier.BASIC: 2,
    ItemTier.STANDARD: 3,
    ItemTier.ADVANCED: 5,
}

# Base materials (Tier 1)
BASE_MATERIALS = {
    "Fire Essence": Element.FIRE,
    "Water Crystal": Element.WATER,
    "Leaf Fragment": Element.NATURE,
    "Light Shard": Element.LIGHT,
    "Shadow Dust": Element.DARK,
    "Lightning Spark": Element.ELECTRIC,
    "Frost Particle": Element.ICE,
    "Earth Stone": Element.EARTH,
    "Weapon Prototype": None,  # Universal crafting material
    "Magic Catalyst": None,    # Universal crafting material
    "Enchanted Cloth": None,   # Universal crafting material
}

    
RENAME_MAP = {
    "Fire Essence": [
        "Essence of Fire",  
        "Fire Fragment",    
        "Flame Core",      
        "Compound-109",
        "Agent-F45",
        "Ignis-7",
        "Cinnabar Powder",
        "Phoenix Tear",
        "Searing Cinder"
    ],
    "Water Crystal": [
        "Ocean Tear",      
        "Aqua Crystal",   
        "Water Gem",        
        "Mat-W12",
        "Liquid-H2O",
        "Hydro-Beta",
        "Cobalt Tear",
        "Tears of the Lake",
        "Mist Pearl"
    ],
    "Leaf Fragment": [
        "Leaf Shard",        
        "Verdant Fragment",   
        "Nature Chip",     
        "Batch-G9",
        "Sector-7",
        "Flora-33",
        "Emerald Scale",
        "Forest Sliver",
        "Jungle Seed"
    ],
    "Light Shard": [
        "Sunbeam Fragment", 
        "Lightcore", 
        "Radiant Chip",
        "Photon-77",
        "Unit-101",
        "Lux-Alpha",
        "Dawn Pebble",
        "Daybreak Core",
        "Sunlight Pearl"
    ],
    "Shadow Dust": [
        "Dark Residue", 
        "Shadow Powder",
        "Umbra Particle",
        "Void-X9",
        "Index-4",
        "Nox-0",
        "Midnight Powder",
        "Onyx Flake",
        "Eclipse Ash"
    ],
    "Lightning Spark": [
        "Storm Seed", 
        "Lightning Core", 
        "Spark Fragment",
        "Volt-220",
        "Amp-8",
        "Node-Beta",
        "Galvanic Seed",
        "Static Filament",
        "Flickering Amber"
    ],
    "Frost Particle": [
        "Ice Fragment", 
        "Frostbite Chip",
        "Glacial Flake",
        "Zero-Kelvin",
        "Sample-Z",
        "F-32",
        "Winter Seed",
        "Shivering Powder",
        "Sleet Sliver"
    ],
    "Earth Stone": [
        "Earthen Shard", 
        "Dusty Rock",
        "Earth Core",
        "Geo-5",
        "Code-503",
        "Tellus-IX",
        "Basalt Chunk",
        "Loam Pebble",
        "Terran Fragment"
    ],
    "Weapon Prototype": [
        "Blank Weapon Core",
        "Weapon Template",
        "Prototype Frame",
        "Model-T",
        "Template-X",
        "W-Proto",
        "Steel Ingot",
        "Forging Blank",
        "Iron Template"
    ],
    "Magic Catalyst": [
        "Arcanite Core", 
        "Spell Focus", 
        "Magic Vial",
        "Reagent-4",
        "Flask-C",
        "Ether-9",
        "Runic Essence",
        "Mercury Vial",
        "Astral Dust"
    ],
    "Enchanted Cloth": [
        "Mystic Wrap", 
        "Enchanted Fabric",
        "Cloth of Runes",
        "Fabric-B",
        "F-88",
        "Loom-0",
        "Silk Ribbon",
        "Velvet Scrap",
        "Gilded Band"
    ],
    # Standard weapons (Tier 2)
    "Fire Staff": [
        "Blazing Rod",
        "Infernal Baton",
        "Pyre Cane",
        "Ignis Wand",
        "Flame Scepter",
        "W-Fire-2"
    ],
    "Water Wand": [
        "Aqua Rod",
        "Tidal Staff",
        "Ocean Scepter",
        "Hydro Baton",
        "Stream Wand",
        "W-Water-2"
    ],
    "Nature Bow": [
        "Verdant Greatbow",
        "Sylvan Arch",
        "Forest Longbow",
        "Flora Bow",
        "Vine Crossbow",
        "W-Nature-2"
    ],
    "Light Mace": [
        "Radiant Hammer",
        "Solar Club",
        "Luminous Cudgel",
        "Dawn Star",
        "Sun Maul",
        "W-Light-2"
    ],
    "Dark Dagger": [
        "Shadow Blade",
        "Umbral Knife",
        "Void Stiletto",
        "Nox Dirk",
        "Eclipse Cutter",
        "W-Dark-2"
    ],
    "Lightning Rod": [
        "Volt Staff",
        "Storm Pole",
        "Thunder Stick",
        "Spark Rod",
        "Galvanic Wand",
        "W-Electric-2"
    ],
    "Ice Sword": [
        "Frost Blade",
        "Glacial Saber",
        "Winter Edge",
        "Cryo Rapier",
        "Zero Claymore",
        "W-Ice-2"
    ],
    "Earth Hammer": [
        "Terran Maul",
        "Seismic Mace",
        "Boulder Smasher",
        "Geo Sledge",
        "Stone Breaker",
        "W-Earth-2"
    ],
    # Enhancers
    "Fire Enhancer": ["Pyro Catalyst", "Flame Booster", "Ignition Core", "E-Fire-1"],
    "Water Enhancer": ["Aqua Amplifier", "Tide Focus", "Hydro Booster", "E-Water-1"],
    "Nature Enhancer": ["Verdant Growth", "Flora Focus", "Sylvan Catalyst", "E-Nature-1"],
    "Light Enhancer": ["Radiant Prism", "Sun Focus", "Luminous Core", "E-Light-1"],
    "Dark Enhancer": ["Void Catalyst", "Shadow Focus", "Nox Resonator", "E-Dark-1"],
    "Lightning Enhancer": ["Volt Capacitor", "Storm Resonator", "Spark Amplifier", "E-Electric-1"],
    "Ice Enhancer": ["Cryo Core", "Frost Focus", "Glacial Catalyst", "E-Ice-1"],
    "Earth Enhancer": ["Geo Resonator", "Stone Focus", "Seismic Core", "E-Earth-1"],
    # Advanced weapons (Tier 3)
    "Inferno Blaster": ["Pyros Cannon", "Hellfire Launcher", "Solar Buster", "W-Fire-3"],
    "Tsunami Trident": ["Abyssal Lance", "Ocean Cleaver", "Hydro Harpoon", "W-Water-3"],
    "Gaia's Vengeance": ["Sylvan Wrath", "Verdant Judgement", "Nature Sentinel", "W-Nature-3"],
    "Divine Scepter": ["Angel Star", "Heavenly Beacon", "Solar Dominion", "W-Light-3"],
    "Void Reaper": ["Eternity Scythe", "Nox Destroyer", "Shadow Cleaver", "W-Dark-3"],
    "Storm Caller": ["Tempest Spear", "Thunderbringer", "Mjolnir Frame", "W-Electric-3"],
    "Glacier Blade": ["Absolute Zero", "Rime Slicer", "Permafrost Greatsword", "W-Ice-3"],
    "Mountain Breaker": ["Tectonic Shatterer", "Earthsplitter", "Titan Hammer", "W-Earth-3"]
}

# Standard weapons (Tier 2)
STANDARD_WEAPONS = {
    "Fire Staff": Element.FIRE,
    "Water Wand": Element.WATER,
    "Nature Bow": Element.NATURE,
    "Light Mace": Element.LIGHT,
    "Dark Dagger": Element.DARK,
    "Lightning Rod": Element.ELECTRIC,
    "Ice Sword": Element.ICE,
    "Earth Hammer": Element.EARTH,
}

# Advanced weapons (Tier 3)
ADVANCED_WEAPONS = {
    "Inferno Blaster": Element.FIRE,
    "Tsunami Trident": Element.WATER,
    "Gaia's Vengeance": Element.NATURE,
    "Divine Scepter": Element.LIGHT,
    "Void Reaper": Element.DARK,
    "Storm Caller": Element.ELECTRIC,
    "Glacier Blade": Element.ICE,
    "Mountain Breaker": Element.EARTH,
}

# Resulting mapping: item name -> weight
ITEM_WEIGHT_MAP = {}

# Add base materials (tier: BASIC)
for name in BASE_MATERIALS:
    ITEM_WEIGHT_MAP[name] = ITEM_WEIGHTS[ItemTier.BASIC]

# Add standard weapons (tier: STANDARD)
for name in STANDARD_WEAPONS:
    ITEM_WEIGHT_MAP[name] = ITEM_WEIGHTS[ItemTier.STANDARD]

# Add advanced weapons (tier: ADVANCED)
for name in ADVANCED_WEAPONS:
    ITEM_WEIGHT_MAP[name] = ITEM_WEIGHTS[ItemTier.ADVANCED]
    
# Final mapping: item name -> type, tier, element
ITEM_INFO_MAP = {}

# Base materials (tier: BASIC)
for name, element in BASE_MATERIALS.items():
    ITEM_INFO_MAP[name] = {
        "type": "material",
        "tier": ItemTier.BASIC,
        "element": element
    }

# Standard weapons (tier: STANDARD)
for name, element in STANDARD_WEAPONS.items():
    ITEM_INFO_MAP[name] = {
        "type": "weapon",
        "tier": ItemTier.STANDARD,
        "element": element
    }

# Advanced weapons (tier: ADVANCED)
for name, element in ADVANCED_WEAPONS.items():
    ITEM_INFO_MAP[name] = {
        "type": "weapon",
        "tier": ItemTier.ADVANCED,
        "element": element
    }
    
# Crafting recipes
CRAFTING_RECIPES = {
    # Tier 2 weapons (Element + Prototype)
    "Fire Staff": [("Fire Essence", 1), ("Weapon Prototype", 1)],
    "Water Wand": [("Water Crystal", 1), ("Weapon Prototype", 1)],
    "Nature Bow": [("Leaf Fragment", 1), ("Weapon Prototype", 1)],
    "Light Mace": [("Light Shard", 1), ("Weapon Prototype", 1)],
    "Dark Dagger": [("Shadow Dust", 1), ("Weapon Prototype", 1)],
    "Lightning Rod": [("Lightning Spark", 1), ("Weapon Prototype", 1)],
    "Ice Sword": [("Frost Particle", 1), ("Weapon Prototype", 1)],
    "Earth Hammer": [("Earth Stone", 1), ("Weapon Prototype", 1)],
    
    # Element enhancers
    "Fire Enhancer": [("Fire Essence", 2), ("Magic Catalyst", 1)],
    "Water Enhancer": [("Water Crystal", 2), ("Magic Catalyst", 1)],
    "Nature Enhancer": [("Leaf Fragment", 2), ("Magic Catalyst", 1)],
    "Light Enhancer": [("Light Shard", 2), ("Magic Catalyst", 1)],
    "Dark Enhancer": [("Shadow Dust", 2), ("Magic Catalyst", 1)],
    "Lightning Enhancer": [("Lightning Spark", 2), ("Magic Catalyst", 1)],
    "Ice Enhancer": [("Frost Particle", 2), ("Magic Catalyst", 1)],
    "Earth Enhancer": [("Earth Stone", 2), ("Magic Catalyst", 1)],
    
    # Tier 3 weapons (Tier 2 weapon + Element enhancer)
    "Inferno Blaster": [("Fire Staff", 1), ("Fire Enhancer", 1), ("Enchanted Cloth", 1)],
    "Tsunami Trident": [("Water Wand", 1), ("Water Enhancer", 1), ("Enchanted Cloth", 1)],
    "Gaia's Vengeance": [("Nature Bow", 1), ("Nature Enhancer", 1), ("Enchanted Cloth", 1)],
    "Divine Scepter": [("Light Mace", 1), ("Light Enhancer", 1), ("Enchanted Cloth", 1)],
    "Void Reaper": [("Dark Dagger", 1), ("Dark Enhancer", 1), ("Enchanted Cloth", 1)],
    "Storm Caller": [("Lightning Rod", 1), ("Lightning Enhancer", 1), ("Enchanted Cloth", 1)],
    "Glacier Blade": [("Ice Sword", 1), ("Ice Enhancer", 1), ("Enchanted Cloth", 1)],
    "Mountain Breaker": [("Earth Hammer", 1), ("Earth Enhancer", 1), ("Enchanted Cloth", 1)],
}

# Enemy configurations
ENEMY_PREFIXES = [
    "Fierce", "Menacing", "Corrupted", "Ancient", "Mystic",
    "Furious", "Vigilant", "Restless", "Tranquil", "Rampaging"
]

ENEMY_TYPES = {
    Element.FIRE: ["Fire Imp", "Magma Golem", "Flame Sprite"],
    Element.WATER: ["Water Elemental", "Tide Lurker", "Rain Phantom"],
    Element.NATURE: ["Forest Guardian", "Vine Strangler", "Leaf Sprite"],
    Element.LIGHT: ["Radiant Angel", "Dawn Spirit", "Light Wisp"],
    Element.DARK: ["Shadow Walker", "Void Fiend", "Night Stalker"],
    Element.ELECTRIC: ["Thunder Beast", "Spark Phantom", "Lightning Elemental"],
    Element.ICE: ["Frost Giant", "Ice Golem", "Blizzard Spirit"],
    Element.EARTH: ["Stone Sentinel", "Rock Beast", "Crystal Giant"],
}

# Boss configurations
BOSS_NAMES = {
    Element.FIRE: "Inferno Overlord",
    Element.WATER: "Abyssal Hydra",
    Element.NATURE: "Ancient World Tree",
    Element.LIGHT: "Radiance Seraph",
    Element.DARK: "Void Emperor",
    Element.ELECTRIC: "Thunderstorm Archon",
    Element.ICE: "Eternal Frost Titan",
    Element.EARTH: "Mountain Colossus",
}

# Game level configurations
EASY_MODE_LAYERS = ["growth", "growth", "combat", "growth", "shop", "boss"]
HARD_MODE_LAYERS = ["growth", "combat", "growth", "growth", "miniboss", "growth", "shop", "boss"]

# Inventory configurations
INITIAL_INVENTORY_CAPACITY = 12
CAPACITY_INCREASE_COMBAT = 2
CAPACITY_INCREASE_MINIBOSS = 3

# Combat configurations
ENEMY_BASE_HP_RANGE = (40, 60)
MINIBOSS_HP_RANGE = (80, 120)
BOSS_HP_RANGE = (150, 200)

ENEMY_DAMAGE_LOW = 6
ENEMY_DAMAGE_HIGH = 8


for defender in Element:

    counters = []

    for attacker, table in ELEMENT_EFFECTIVENESS.items():

        if table.get(defender, 1.0) > 1.0:

            counters.append(attacker.name)

    print(defender.name, "<-", counters)