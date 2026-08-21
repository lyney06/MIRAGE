import gym
import numpy as np
from gym.envs.registration import register

from pdb import set_trace as st


# ======================================= Navigation ======================================= #

for obs_type in ['encoded', 'raw']:
    env_id = f"VillageNav-v0" if obs_type == 'encoded' else f"VillageNav-{obs_type}-v0"
    register(
        id=env_id,  # Unique ID for the environment
        entry_point="envs.cuterpg.navigation:NavigationEnv",  # Path to your environment class
        kwargs={  # Pass all custom parameters inside kwargs
            "obs_type": obs_type,
            "seasons": ["summer"],
            "dynamic": False,
            "npc": False,
            "max_land_size": 4,
            "min_land_size": 2,
        },
    )
    
    env_id = f"VillageNav-Large-v0" if obs_type == 'encoded' else f"VillageNav-Large-{obs_type}-v0"
    register(
        id=env_id,  # Unique ID for the environment
        entry_point="envs.cuterpg.navigation:NavigationEnv",  # Path to your environment class
        kwargs={  # Pass all custom parameters inside kwargs
            "obs_type": obs_type,
            "seasons": ["summer"],
            "dynamic": False,
            "npc": False,
            "max_land_size": 4,
            "min_land_size": 2,
            "window_width": 1200,
            "window_height": 1200,
            "map_rows": 24,
            "map_cols": 24,
        },
    )

# get manual in summer, and test in winter
register(
    id=f"VillageNav-Seasonal-v0",  # Unique ID for the environment
    entry_point="envs.cuterpg.navigation:NavigationEnv",  # Path to your environment class
    kwargs={  # Pass all custom parameters inside kwargs
        "obs_type": "encoded",
        "seasons": ["summer", "winter"],
        "dynamic": False,
        "npc": False,
        "max_land_size": 4,
        "min_land_size": 2,
    },
)

register(
    id=f"VillageNav-Dynamic-v0",  # Unique ID for the environment
    entry_point="envs.cuterpg.navigation:NavigationEnv",  # Path to your environment class
    kwargs={  # Pass all custom parameters inside kwargs
        "obs_type": "encoded",
        "seasons": ["summer"],
        "dynamic": True,
        "npc": False,
        "max_land_size": 4,
        "min_land_size": 2,
    },
)

# NOTE: VillageNav-NPC_* environments are currently work-in-progress.
# Static NPCs are spawned on the map, but the full interaction loop (exposing 'inquire_npc' in
# available actions, adjacent distance checks, observation formatting, and prompt integration) is not fully wired up.
for manual_type in ['perfect', 'imperfect', 'mixed']:
    if manual_type == 'perfect':
        manual_lst = [1, 2]
    elif manual_type == 'imperfect':
        manual_lst = [3]
    elif manual_type == 'mixed':
        manual_lst = [1, 2, 3]
    register(
        id=f"VillageNav-NPC_{manual_type}-v0",  # Unique ID for the environment
        entry_point="envs.cuterpg.navigation:NavigationEnv",  # Path to your environment class
        kwargs={  # Pass all custom parameters inside kwargs
            "obs_type": "encoded",
            "seasons": ["summer"],
            "dynamic": False,
            "npc": 5, # number of random npc on the map
            "max_land_size": 4,
            "min_land_size": 2,
            "npc_manual_lst": manual_lst,
        },
    )

for obs_type in ['encoded', 'raw']:
    env_id = f"UrbanNav-Construction-v0" if obs_type == 'encoded' else f"UrbanNav-Construction-{obs_type}-v0"
    register(
        id=env_id,  # Unique ID for the environment
        entry_point="envs.cuterpg.navigation:NavigationEnv",  # Path to your environment class
        kwargs={  # Pass all custom parameters inside kwargs
            "obs_type": obs_type,
            "seasons": ["summer"],
            "dynamic": False,
            "npc": False,
            "max_land_size": 2,
            "min_land_size": 2,
            "construction": True,
            # "window_width": 900,
            # "window_height": 900,
            # "map_rows": 18,
            # "map_cols": 18,
        },
    )


# ======================================= Cooking ======================================= #

for mode in ['hard', 'easy']:
    env_id = f"Cooking-{mode}-v0"
    register(
        id=env_id,  # Unique ID for the environment
        entry_point="envs.cuterpg.cooking:CookingEnv",  # Path to your environment class
        kwargs={  # Pass all custom parameters inside kwargs
            "mode": mode,
        },
    )


    env_id = f"Cooking-{mode}-crop-gone-v0"
    register(
        id=env_id,  # Unique ID for the environment
        entry_point="envs.cuterpg.cooking:CookingEnv",  # Path to your environment class
        kwargs={  # Pass all custom parameters inside kwargs
            "mode": mode,
            "crop_gone": True
        },
    )

    env_id = f"Cooking-{mode}-rookie-chef-v0"
    register(
        id=env_id,  # Unique ID for the environment
        entry_point="envs.cuterpg.cooking:CookingEnv",  # Path to your environment class
        kwargs={  # Pass all custom parameters inside kwargs
            "mode": mode,
            "novice_mistake": True
        },
    )
    
    env_id = f"Cooking-{mode}-storage-loss-v0"
    register(
        id=env_id,  # Unique ID for the environment
        entry_point="envs.cuterpg.cooking:CookingEnv",  # Path to your environment class
        kwargs={  # Pass all custom parameters inside kwargs
            "mode": mode,
            "storage_loss": True
        },
    )


env_id = f"Cooking-multiserve-v0"
register(
    id=env_id,  # Unique ID for the environment
    entry_point="envs.cuterpg.cooking:CookingEnv",  # Path to your environment class
    kwargs={  # Pass all custom parameters inside kwargs
        "mode": 'easy',
        "storage_loss": False,
        "n_servings": 5,
    },
)


# ======================================= Gaming ======================================= #
# ======================================= RoguelikeRPG ======================================= #

for mode in ['easy']:
    env_id = f"Roguelike-{mode}-v0"
    register(
        id=env_id,  # Unique ID for the environment
        entry_point="envs.cuterpg.game:GameEnv",  # Path to your environment class
        kwargs={  # Pass all custom parameters inside kwargs
            "mode": mode,
        },
    )


    env_id = f"Roguelike-shuffle-{mode}-v0"
    register(
        id=env_id,  # Unique ID for the environment
        entry_point="envs.cuterpg.game:GameEnv",  # Path to your environment class
        kwargs={  # Pass all custom parameters inside kwargs
            "mode": mode,
            "shuffle_container": True,
            "shuffle_enemy": True,
            "single_level_enemy": 2,
            "reversible": True,
        },
    )

    env_id = f"Roguelike-reversible-{mode}-v0"
    register(
        id=env_id,  # Unique ID for the environment
        entry_point="envs.cuterpg.game:GameEnv",  # Path to your environment class
        kwargs={  # Pass all custom parameters inside kwargs
            "mode": mode,
            "reversible": True
        },
    )

    env_id = f"Roguelike-rename-{mode}-v0"
    register(
        id=env_id,  # Unique ID for the environment
        entry_point="envs.cuterpg.game:GameEnv",  # Path to your environment class
        kwargs={  # Pass all custom parameters inside kwargs
            "mode": mode,
            "item_rename": True,
            "reversible": True,
        },
    )

