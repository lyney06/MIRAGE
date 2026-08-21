from .constant import COOKING_TOOLS
from pdb import set_trace as st

def parse_take_action(action_str):
    """
    Parses actions like:
        - 'take raw beef out of fridge'
        - 'take tomato out of cabinet'
        - 'take steamed rice out of pot_0'

    Returns:
        (ingredient_name, source_location) or raises ValueError on invalid format.
    """
    action_str = action_str.strip().lower()

    if not action_str.startswith("take ") or " out of " not in action_str:
        raise ValueError("Invalid action format. Use 'take <ingredient> out of <fridge/cabinet/tool>'.")

    try:
        main_part, location = action_str.split(" out of ")
        _, ingredient = main_part.split("take ", 1)
        ingredient = ingredient.strip()
        location = location.strip()

        if not ingredient:
            raise ValueError("Missing ingredient name.")

        # Validate location
        if location in {"fridge", "cabinet"}:
            return ingredient, location

        # Check if it's a valid cooking tool instance like 'pot_0'
        tool_types = sorted(set(COOKING_TOOLS.keys()))

        tool_base = location.split("_")[0]
        if tool_base in tool_types:
            return ingredient, location

        raise ValueError(f"Invalid location '{location}'. Use 'fridge', 'cabinet', or valid tool name like 'pan_0'.")

    except Exception:
        raise ValueError("Invalid action format. Use 'take <ingredient> out of <fridge/cabinet/tool>'.")

def parse_put_action(action_str):
    """
    Parse an action like 'put raw chicken into pan_0' -> ('raw chicken', 'pan_0')
    """
    tokens = action_str.strip().split()

    if len(tokens) < 4 or tokens[0] != 'put' or 'into' not in tokens:
        raise ValueError("Invalid put action format. Use: 'put <ingredient> into <tool>'.")

    into_idx = tokens.index('into')
    ingredient = ' '.join(tokens[1:into_idx])
    tool = ' '.join(tokens[into_idx + 1:])

    if not ingredient or not tool:
        raise ValueError("Missing ingredient or tool in put action.")

    return ingredient, tool



def parse_plate_action(action_str):
    """
    Support the following two modes:
    - plate <ingredient_phrase> into <plate_id>
    - plate from <tool> into <plate_id>
    
    Returns:
        mode (str): "from_hand" or "from_tool"
        arg1 (str): ingredient or tool
        plate_id (str)
    """
    action_str = action_str.strip().lower()

    if not action_str.startswith("plate "):
        raise ValueError("Invalid plate format. Use: plate <ingredient> into <plate_id> or plate from <tool> into <plate_id>.")

    try:
        # plate from pot_0 into plate_1
        if "plate from " in action_str:
            _, rest = action_str.split("plate from ", 1)
            tool, plate = rest.split(" into ")
            return "from_tool", tool.strip(), plate.strip()

        # plate boiled rice into plate_0
        else:
            main_part = action_str[len("plate "):]
            if " into " not in main_part:
                raise ValueError
            ing, plate = main_part.split(" into ")
            return "from_hand", ing.strip(), plate.strip()

    except Exception:
        raise ValueError("Invalid action format. Use: plate <ingredient> into <plate_id> or plate from <tool> into <plate_id>.")