# constant.py
from pdb import set_trace as st
# ------------------------
# 🥦 INGREDIENTS CLASSIFICATION
# ------------------------

# plantable ingredients
PLANTABLE_INGREDIENTS = [
    "tomato", 
    "carrot",
    "potato",
    "lettuce",
    "cucumber",
    "corn",
]

# fishable ingredients
FISHABLE_INGREDIENTS = [
    "salmon",
    "tuna",
    "shrimp",
    "crab",
    "trout",
    "lobster",
    "oyster",
    "clam",
    "squid",
    "scallop",
]

ADDITIONAL_SEAFOOD = [
    "mackerel",
    "octopus",
    "anchovy",
    "eel",
    # "sea bass",     # remove for now due to empty space in the middle 
    "sardine",
    "croaker",
    "smelt",
    "flounder",
    "rockfish",
    "perch",
    "herring",
    "whiting",
]

# ingredients that can only be purchased
MEATS = ["chicken",
         "beef",
         "lamb",
         "pork",
         "ham",
         ]

CABINET_INGREDIENTS = [
    "flour",
    "rice",
    "avocado",
    "croutons",
    "tofu",
    "pea",
    "bean"
]
FRIDGE_INGREDIENTS = [
    "milk",
    "cheese",
    "mushroom",
    "spinach"
]
PURCHASABLE_ONLY_INGREDIENTS = CABINET_INGREDIENTS + FRIDGE_INGREDIENTS
PURCHASABLE_ONLY_INGREDIENTS.extend(MEATS)

MEAT_SEAFOOD_DICT = {
    "meat": MEATS,
    "seafood": FISHABLE_INGREDIENTS,
    "plant_based": ["tofu"]
}

MEAT_SEAFOOD_DICT['meat_seafood'] = MEAT_SEAFOOD_DICT['meat']+MEAT_SEAFOOD_DICT['seafood']
MEAT_SEAFOOD_DICT['all'] = MEAT_SEAFOOD_DICT['meat']+MEAT_SEAFOOD_DICT['seafood']+MEAT_SEAFOOD_DICT['plant_based']

# ------------------------
# 🧂 SEASONINGS
# ------------------------

BASE_SEASONINGS = [
    "salt",
    "pepper",
    "sugar",
    "soy sauce",
    "white vinegar",
    "rice vinegar",
    "garlic",
    "ginger",
    "chili sauce",
    "olive oil",
    "sesame oil",
    "butter",
    "cream",
    "sour cream",
]

SPECIAL_SEASONINGS = [
    "lemon juice",
    "lime juice",
    "parmesan",
    "basil",
    "oregano",
    "cumin",
    "paprika",
    "wasabi",
    "honey",
    "dill",
    "balsamic vinegar",
    "parsley"
]

SEASONINGS = BASE_SEASONINGS + SPECIAL_SEASONINGS

# we can buy everything from store, unless they are out of stock
PURCHASABLE_INGREDIENTS = PURCHASABLE_ONLY_INGREDIENTS + PLANTABLE_INGREDIENTS + FISHABLE_INGREDIENTS + SEASONINGS

FLAVOR_TO_SEASONINGS = {
    "Basic Savory": {
        "during_cooking": ["salt", "pepper"],
    },
    "Umami Sweet": {
        "during_cooking": ["soy sauce", "garlic", "sugar"],
    },
    "Sweet and Sour": {
        "during_cooking": ["white vinegar", "soy sauce", "sugar"],
    },
    "Aromatic Umami": {
        "during_cooking": ["soy sauce", "ginger", "garlic", "sesame oil"],
    },
    "Spicy Umami": {
        "during_cooking": ["soy sauce", "chili sauce", "garlic", "ginger"],
    },
    "Tangy Pepper": {
        "during_cooking": ["white vinegar", "salt", "pepper"],
    },
    "Sweet Spicy": {
        "during_cooking": ["chili sauce", "sugar"],
    },
    "Hot and Sour": {
        "during_cooking": ["rice vinegar", "chili sauce", "sugar"],
    },
    "Fiery Aromatic": {
        "during_cooking": ["sesame oil", "ginger", "garlic", "chili sauce"],
    },
    "Teriyaki": {
        "during_cooking": ["soy sauce", "rice vinegar", "garlic", "sugar"],
    },

    "Classic Fresh": {
        "after_cooking": ["olive oil", "lemon juice"]
    },
    "Sweet Balsamic": {
        "after_cooking": ["balsamic vinegar", "garlic", "honey"],
    },
    "Asian Sesame": {
        "after_cooking": ["soy sauce", "rice vinegar", "ginger", "sesame oil"],
    },
    "Tangy Spiced": {
        "during_cooking": ["cumin", "paprika", "lime juice", "olive oil"],
    },
    "Classic Sushi": {
        "after_cooking": ["soy sauce", "rice vinegar", "wasabi"],
    },
    "Sesame Ginger": {
        "during_cooking": ["soy sauce", "ginger", "sesame oil"],
    },
    "Spicy Citrus": {
        "during_cooking": ["chili sauce", "garlic", "lime juice", "honey"],
    },

    "Spicy Mediterranean": {
        "during_cooking": ["olive oil", "chili sauce", "paprika", "cumin"],
    },
    "Lemon Garlic": {
        "during_cooking": ["garlic", "lemon juice"],
    },
    "Smoky Lime": {
        "during_cooking": ["olive oil", "paprika", "cumin", "lime juice"],
    },
    "Savory Sweet": {
        "during_cooking": ["butter", "garlic", "soy sauce", "honey"],
    },
    "Zesty Lime": {
        "during_cooking": ["olive oil", "cumin", "garlic", "lime juice"],
    },
    "Sweet Spicy": {
        "during_cooking": ["soy sauce", "chili sauce", "garlic", "honey"],
    },
    "Zesty Herb": {
        "after_cooking": ["olive oil", "basil", "oregano", "parmesan"],
    },
    "Garlic Butter": {
        "during_cooking": ["butter", "garlic", "parsley"],
    },
}


SPECIAL_DISHES = {
    "sushi": {
        "Tokyo Classic Nigiri": {
            "after_cooking": ["soy sauce", "wasabi", "rice vinegar"]
        },
        "Spicy Dragon Roll": {
            "after_cooking": ["lime juice", "honey", "chili sauce", "garlic"]
        },
        "Sesame Ginger Maki": {
            "after_cooking": ["sesame oil", "soy sauce", "ginger"]
        },
    },

    "salad": {
        "Caesar Supreme Salad": {
            "after_cooking": ["lemon juice", "salt", "pepper", "olive oil"]
        },
        "Mediterranean Balsamic Greens": {
            "after_cooking": ["honey", "balsamic vinegar", "garlic", "olive oil"]
        },
        "Spicy Thai Peanut Salad": {
            "after_cooking": ["soy sauce", "rice vinegar", "ginger", "sesame oil"]
        },
        "Mexican Lime Fiesta Salad": {
            "after_cooking": ["cumin", "paprika", "lime juice", "olive oil"]
        },
        "Greek Dill Cucumber Salad": {
            "after_cooking": ["white vinegar", "dill","olive oil"]
        }
    },

    "baked_seafood": {
        "Garlic Butter Lobster Tail": {
            "during_cooking": ["butter", "garlic", "soy sauce", "honey"],
        },
        "Cajun Spiced Grilled Shrimp": {
            "during_cooking": ["chili sauce", "paprika", "cumin"],
        },
        "Lemon Herb Grilled Salmon": {
            "during_cooking": ["garlic", "lemon juice"],
        },
        "Smoky Paprika Octopus": {
            "during_cooking": ["paprika", "cumin", "lime juice"],
        },
        "Lemon Dill Salmon": {
            "during_cooking": ["garlic", "lemon juice", "dill"],
        }
    },

    "taco": {
        "Chipotle Taco": {
            "after_cooking": ["cumin", "paprika", "chili sauce"]
        },
        "Baja Taco": {
            "after_cooking": ["cumin", "garlic", "lime juice"]
        },
        "Caribbean Jerk Taco": {
            "after_cooking": ["paprika", "cumin", "lime juice"],
        }
    },

    "fried_rice": {
        "Golden Egg": {
            "during_cooking": ["butter", "salt", "pepper"],
        },
        "Shanghai Soy Glazed": {
            "during_cooking": ["soy sauce", "garlic", "sugar"],
        },
        "Thai Spicy Basil": {
            "during_cooking": ["chili sauce", "garlic", "sugar"],
        },
        "Szechuan Peppercorn": {
            "during_cooking": ["ginger", "garlic", "chili sauce"],
        }
    },

}

FLAVOR_TO_DISHES = {
    "Basic Savory": ["fried_rice", "baked_seafood"],
    "Umami Sweet": ["fried_rice"],
    "Sweet and Sour": ["fried_rice"],
    "Aromatic Umami": ["fried_rice", "baked_seafood"],
    "Spicy Umami": ["fried_rice", "taco"],
    "Tangy Pepper": ["baked_seafood"],
    "Sweet Spicy": ["fried_rice", "taco"],
    "Hot and Sour": ["sushi", "taco"],
    "Fiery Aromatic": ["fried_rice", "taco"],
    "Teriyaki": ["baked_seafood"],
    "Spicy Mediterranean": ["baked_seafood"],

    "Classic Fresh": ["salad", "baked_seafood"],
    "Sweet Balsamic": ["salad"],
    "Asian Sesame": ["salad", "sushi"],
    "Tangy Spiced": ["taco"],

    "Classic Sushi": ["sushi"],
    "Sesame Ginger": ["sushi"],
    "Spicy Citrus": ["sushi", "taco"],

    "Lemon Garlic": ["baked_seafood"],
    "Smoky Lime": ["baked_seafood", "taco"],
    "Savory Sweet": ["baked_seafood"],

    "Zesty Lime": ["taco"],
    "Garlic Butter": ["baked_seafood"],
    "Zesty Herb": ["salad"],
}


# ------------------------
# 🍳 COOKING METHODS
# ------------------------
COOKING_TOOLS = {
    "oven": "bake",
    "deep_fryer": "deep-fry",
    "pot": "boil",
    "steamer": "steam",
    "pan": "pan-fry",
    "grill": "grill",
    "cutting_board": "chop",
    "dish": "serve",
}

COOKING_METHOD_TO_STATE = {
    "boil": "boiled",
    "deep-fry": "deep-fried",
    "bake": "baked",
    "grill": "grilled",
    "steam": "steamed",
    "pan-fry": "pan-fried",
    "chop": "chopped",
    "serve": "assembled",
}

TOOL_MAX_CAP = {
    "oven": 4,
    "pan": 4,
    "pot": 1,
    "steamer": 1,
    "deep_fryer": 1,
    "knife": 1,
    "grill": 1,
}

STATE_TO_METHOD = {v: k for k, v in COOKING_METHOD_TO_STATE.items()}
METHOD_TO_TOOL = {v: k for k, v in COOKING_TOOLS.items()}



# ------------------------
# 🍱 RECIPES
# ------------------------
RECIPES = {
    "sushi": {
        "main_ingredients": {
            "rice": [("steamed", "100 g")],
        },
        "required_ingredients": {
            "crab": [("boiled", "30 g")],
            "shrimp": [("boiled", "25 g")],
            "tuna": [("raw", "40 g")],
            "salmon": [("raw", "40 g")],
            "chicken": [("pan-fried", "50 g")],
            "beef": [("pan-fried", "50 g")],
        },
        "optional_ingredients": {
            "avocado": [("raw", "chopped", "0.5 count")],
            "cucumber": [("raw", "chopped", "0.5 count")],
            "mushroom": [("raw", "chopped", "10 g"), ("boiled", "chopped", "10 g")],
        },
        "cooking_steps": [
            [("rice", "steamed"), ("ingredient", "chopped")],
            [("ingredient", "boiled"), ("ingredient", "pan-fried"), ("seasonings", "during_cooking", "pan")],
            [("ingredient", "assembled")], # do we specify ingredients?
            [("seasonings", "after_cooking", "plate")],
        ],
        "step_dependencies": [
            (("rice", "steamed"), ("ingredient", "assembled"))
        ],
        "rules": {
            "optional": (0, 3),
            "required": (1, 2),
        }
    },

    "fried_rice": {
        "main_ingredients": {
            "rice": [("steamed", "pan-fried", "150 g")],
            "egg": [("pan-fried", "1 count")]
            },
        "required_ingredients": {
        },
        "optional_ingredients": {
            "carrot": [("pan-fried", "chopped", "1 count")],
            "pea": [("boiled", "pan-fried", "15 g")],
            "onion": [("pan-fried", "chopped", "15 g")],
            "chicken": [("pan-fried", "chopped", "50 g")],
            "beef": [("pan-fried", "chopped", "50 g")],
            "tofu": [("pan-fried", "chopped", "50 g")],
            "ham": [("pan-fried", "chopped", "50 g")],
            "shrimp": [("pan-fried", "40 g")],
        },
        "cooking_steps": [
            [("rice", "steamed"), ("ingredient", "chopped"), ("ingredient", "boiled")],  
            [("ingredient", "pan-fried"), ("seasonings", "during_cooking", "pan")],  
            [("ingredient", "assembled")],
            [("seasonings", "after_cooking", "plate")],
        ],
        "step_dependencies": [
            (("rice", "steamed"), ("rice", "pan-fried")),
        ],
        "rules": {
            "optional": (1, 5),
            "required": (0, 0)
        }
    },

    "salad": {
        "main_ingredients": {
        "lettuce": [("raw", "50 g")],
        "cucumber": [("raw", "chopped", "30 g")]
        },
        "required_ingredients": {
        },
        "optional_ingredients": {
            "tomato": [("raw", "chopped", "0.5 count"), ("grilled", "chopped", "0.5 count")],
            "croutons": [("raw", "10 g")],
            "corn": [("boiled", "20 g")],
            "spinach": [("raw", "20 g")],
            "avocado": [("raw", "chopped", "0.5 count")],
            "mushroom": [("raw", "chopped", "20 g"), ("grilled", "chopped", "20 g")]
        },
        "cooking_steps": [
            [("ingredient", "boiled"), ("ingredient", "grilled"), ("ingredient", "chopped")],  
            [("ingredient", "assembled")],
            [("seasonings", "after_cooking", "plate")], 
        ],
        "step_dependencies": [
        ],
        "rules": {
            "optional": (2, 4),
            "required": (0, 0)
        }
    },
    
    "baked_seafood": {
        "main_ingredients": {
        },
        "required_ingredients": {
            "shrimp": [("baked", "100 g")],
            "crab": [("baked", "100 g")],
            "lobster": [("baked", "100 g")],
            "scallop": [("baked", "100 g")],
            "oyster": [("baked", "100 g")],
            "clam": [("baked", "100 g")],
            "squid": [("baked", "100 g")],
        },
        "optional_ingredients": {
            "corn": [("baked", "30 g")],
            "potato": [("chopped", "baked", "2 count"), ("baked", "2 count")],
            "ham": [("baked", "50 g")]
        },
        "cooking_steps": [
            [("ingredient", "chopped")],
            [("ingredient", "baked")],
            [("seasonings", "during_cooking", "oven")],  
            [("ingredient", "assembled")],
            [("seasonings", "after_cooking", "plate")],
        ],
        "step_dependencies": [
        ],
        "rules": {
            "required": (1, 6),
            "optional": (0, 3)
        }
    },

    "taco": {
        "main_ingredients": {
            "tortilla": [("grilled", '1 count')],
        },
        "required_ingredients": {
            "shrimp": [("pan-fried", "50 g")],
            "lobster": [("pan-fried", "50 g")],
            "scallop": [("pan-fried", "50 g")],
            "chicken": [("pan-fried", "50 g")],
            "beef": [("pan-fried", "50 g")],
        },
        "optional_ingredients": {
            "lettuce": [("raw", "chopped", "0.5 count")],
            "tomato": [("raw", "chopped", "0.5 count"), ("pan-fried", "chopped", "0.5 count")],
            "avocado": [("raw", "chopped", "0.5 count")],
            "mushroom": [("pan-fried", "chopped", "10 g")],
            "corn": [("boiled", "10 g")],
            "bean": [("boiled", "30 g")]
        },
        "cooking_steps": [
            [("tortilla", "grilled"), ("ingredient", "chopped")],  
            [("ingredient", "pan-fried"), ("ingredient", "boiled")],  
            [("seasonings", "during_cooking", "pan")],
            [("ingredient", "assembled")],
            [("seasonings", "after_cooking", "plate")]
        ],
        "step_dependencies": [
        ],
        "rules": {
            "required": (1, 2), #lower and upper bound
            "optional": (0, 3)
        }
    },
}


DISHES_TO_FLAVORS = {}
for dish in RECIPES:
    for flavor, dishes in FLAVOR_TO_DISHES.items():
        if dish in dishes:
            if dish not in DISHES_TO_FLAVORS:
                DISHES_TO_FLAVORS[dish] = [flavor]
            elif flavor not in DISHES_TO_FLAVORS[dish]:
                DISHES_TO_FLAVORS[dish].append(flavor)

for dish in SPECIAL_DISHES:
    for flavor in SPECIAL_DISHES[dish]:
        if dish not in DISHES_TO_FLAVORS:
            DISHES_TO_FLAVORS[dish] = [flavor]
        elif flavor not in DISHES_TO_FLAVORS[dish]:
            DISHES_TO_FLAVORS[dish].append(flavor)

