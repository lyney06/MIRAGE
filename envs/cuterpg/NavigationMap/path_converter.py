import re
import random
from ..utils.config import TILE_SIZE
from .utils import change_tile_num, fix_another_usage
from .observation import encode_obs, get_first_person
from pdb import set_trace as st

def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

def determine_turn(old_direction, new_direction):
    direction_order = [(0, -TILE_SIZE), (TILE_SIZE, 0), (0, TILE_SIZE), (-TILE_SIZE, 0)]    # (up, right, down, left)

    if old_direction not in direction_order or new_direction not in direction_order:
        return None

    old_ind = direction_order.index(old_direction)
    new_ind = direction_order.index(new_direction)
    if (new_ind - old_ind) % 4 == 1:
        return "Turn right"
    elif (new_ind - old_ind) % 4 == 3:
        return "Turn left"
    elif (new_ind - old_ind) % 4 == 2:
        return "Turn around"

    return None

DIRECTION_DICT = {(TILE_SIZE, 0): "east", (0, TILE_SIZE): "south", 
                     (-TILE_SIZE, 0): "west", (0, -TILE_SIZE): "north"}

def convert_path_to_instructions(path,
                                 map_data,
                                 mode,
                                 direction,
                                 wrong_tiles=False,
                                 closet=None,
                                 ):
    # Start! You are currently facing east.
    # Turn right to face south.
    # Move forward 1 tile (south).
    # Move forward 1 tile (west) to approach the destination.
    
    instructions = []
    dir_inverse = {}
    for key, val in DIRECTION_DICT.items():
        dir_inverse[val] = key
    current_direction = dir_inverse[direction]
    tile_count = 0

    instruction_to_steps = []
    curr_steps = [direction, path[0]]
    for i in range(1, len(path)):
        x1, y1 = path[i - 1]
        x2, y2 = path[i]
        dx = x2 - x1
        dy = y2 - y1
        new_direction = (dx, dy)


        if new_direction == current_direction:
            tile_count += 1
        else:
            if tile_count > 0:
                tile = 'tiles' if tile_count != 1 else 'tile'
                instructions.append(f"Move forward {tile_count} {tile} ({DIRECTION_DICT[current_direction]}).")
                instruction_to_steps.append(curr_steps)

            turn_instruction = determine_turn(current_direction, new_direction)
            if turn_instruction:
                instructions.append(f"{turn_instruction} to face {DIRECTION_DICT[new_direction]}.")
                instruction_to_steps.append([])

            current_direction = new_direction
            tile_count = 1
            curr_steps = [DIRECTION_DICT[new_direction], path[i-1]]

        curr_steps.append(path[i])

    # Last movement, all guidance steps are correct up to this point 
    if current_direction and tile_count > 0:
        tile = 'tiles' if tile_count != 1 else 'tile'
        instructions.append(f"Move forward {tile_count} {tile} ({DIRECTION_DICT[current_direction]}) to approach the destination.")
        instruction_to_steps.append(curr_steps)

    imperfect_info = [[] for _ in range(len(instructions))]
    if wrong_tiles:
        dir_to_vec = {'north': (0, -TILE_SIZE), 'east': (TILE_SIZE, 0), 'south': (0, TILE_SIZE), 'west': (-TILE_SIZE, 0)}
        grid = next(iter(map_data.values())) if isinstance(map_data, dict) else map_data
        H, W = len(grid), len(grid[0])

        def get_valid_ranges(instruction_idx, selected_instruction):
            match = re.search(r"Move forward (\d+) tile", selected_instruction)
            if not match:
                return []
            num_tiles = int(match.group(1))
            curr_dir = instruction_to_steps[instruction_idx][0]
            step_end_pos = instruction_to_steps[instruction_idx][-1]
            dx, dy = dir_to_vec[curr_dir]
            next_x, next_y = step_end_pos[0] + dx, step_end_pos[1] + dy

            is_beyond_boundary = not (0 <= next_y < H and 0 <= next_x < W and grid[next_y][next_x] == 'road')

            if instruction_idx == len(instructions) - 1:
                if num_tiles > 1:
                    return [-1]
                elif not is_beyond_boundary:
                    return [1]
                else:
                    return []
            elif is_beyond_boundary:
                # beyond boundaries: can only -1
                return [-1] if num_tiles > 1 else []
            elif num_tiles == 1:
                # 1 step: can only +1
                return [1]
            else:
                return [-1, 1]

        move_step_indices = [idx for idx, instr in enumerate(instructions) if "Move forward" in instr]
        non_last_indices = move_step_indices[:-1] if len(move_step_indices) > 1 else move_step_indices
        valid_non_last = [idx for idx in non_last_indices if get_valid_ranges(idx, instructions[idx])]
        
        if valid_non_last:
            valid_step_indices = valid_non_last
        else:
            valid_step_indices = [idx for idx in move_step_indices if get_valid_ranges(idx, instructions[idx])]

        if valid_step_indices:
            n_wrong_tiles = 1 if mode == 'easy' else 3
            for _ in range(20):
                temp_instructions = list(instructions)
                temp_imperfect_info = [[] for _ in range(len(instructions))]
                selected_indices = random.sample(valid_step_indices, min(n_wrong_tiles, len(valid_step_indices)))
                selected_instructions = [instructions[i] for i in selected_indices]

                for instruction_idx, selected_instruction in zip(selected_indices, selected_instructions):
                    modified_instruction = selected_instruction
                    match = re.search(r"Move forward (\d+) tile", selected_instruction)
                    num_tiles = int(match.group(1))
                    ranges = get_valid_ranges(instruction_idx, selected_instruction)
                    if not ranges:
                        ranges = [-1] if num_tiles > 1 else [1]
                    delta_count, tile_count = change_tile_num(num_tiles, True, ranges=ranges)

                    curr_dir = instruction_to_steps[instruction_idx][0]
                    step_end_pos = instruction_to_steps[instruction_idx][-1]
                    temp_imperfect_info[instruction_idx] = [delta_count, step_end_pos, curr_dir]
                    
                    old_tile_str = f"{num_tiles} {'tile' if num_tiles == 1 else 'tiles'}"
                    new_tile_str = f"{tile_count} {'tile' if tile_count == 1 else 'tiles'}"
                    temp_instructions[instruction_idx] = modified_instruction.replace(old_tile_str, new_tile_str, 1)

                if not simulate_blind_tile_execution(path, map_data, direction, temp_instructions, closet=closet):
                    instructions = temp_instructions
                    imperfect_info = temp_imperfect_info
                    break
            else:
                return None, None
        else:
            return None, None

    for i in range(len(instructions)):
        instructions[i] = f'Step {i+1}. {instructions[i]}'

    return instructions, imperfect_info

def simulate_blind_tile_execution(path, map_data, start_direction, instructions, closet=None):
    dir_to_vec = {'north': (0, -TILE_SIZE), 'east': (TILE_SIZE, 0), 'south': (0, TILE_SIZE), 'west': (-TILE_SIZE, 0)}
    cur_pos = path[0]
    cur_dir = start_direction
    target_pos = path[-1]
    grid = next(iter(map_data.values())) if isinstance(map_data, dict) else map_data
    H, W = len(grid), len(grid[0])

    for line in instructions:
        match_turn = re.search(r"Turn (?:left|right|around)? ?(?:until you are facing|to face) (north|south|east|west)", line)
        if match_turn:
            cur_dir = match_turn.group(1)
        elif "Move forward" in line or "Walk forward" in line:
            match = re.search(r" (\d+) tile", line)
            if match:
                count = int(match.group(1))
                for _ in range(count):
                    dx, dy = dir_to_vec[cur_dir]
                    next_x, next_y = cur_pos[0] + dx, cur_pos[1] + dy
                    if 0 <= next_y < H and 0 <= next_x < W and grid[next_y][next_x] == 'road':
                        cur_pos = (next_x, next_y)
                    else:
                        break

    if closet and cur_pos in closet:
        return True
    return cur_pos == target_pos

def get_side_dirs(direction):
    if direction in [(TILE_SIZE, 0), (-TILE_SIZE, 0)]:
        return [(0, TILE_SIZE), (0, -TILE_SIZE)]  # south, north
    else:
        return [(TILE_SIZE, 0), (-TILE_SIZE, 0)]  # east, west

def determine_turn_path(from_dir, to_dir):
    mapping = {
        ((TILE_SIZE, 0), (0, -TILE_SIZE)): "left",
        ((TILE_SIZE, 0), (0, TILE_SIZE)): "right",
        ((-TILE_SIZE, 0), (0, TILE_SIZE)): "left",
        ((-TILE_SIZE, 0), (0, -TILE_SIZE)): "right",
        ((0, TILE_SIZE), (TILE_SIZE, 0)): "left",
        ((0, TILE_SIZE), (-TILE_SIZE, 0)): "right",
        ((0, -TILE_SIZE), (-TILE_SIZE, 0)): "left",
        ((0, -TILE_SIZE), (TILE_SIZE, 0)): "right",
    }
    return mapping.get((from_dir, to_dir), 'unknown')

def count_branches(map_data, path_segment, direction, turn_side, season='summer'):
    dx, dy = direction
    if turn_side == "left":
        side = (dy, -dx)
    else:
        side = (-dy, dx)
    count = 0
    for idx, (x, y) in enumerate(path_segment):
        if idx == 0:
            continue
        sx, sy = x + side[0], y + side[1]
        try:
            if 0 <= sy < len(map_data[season]) and 0 <= sx < len(map_data[season][0]):
                if map_data[season][sy][sx] == 'road':
                    count += 1
        except (IndexError, KeyError):
            continue
    return count

def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])

def generate_instruction(turn, count, current_dir):
    dir_str = DIRECTION_DICT[current_dir]
    dir_phrase_templates = [
        f"Walk towards {dir_str}",
        f"Head {dir_str}",
        f"Continue going {dir_str}",
    ]
    direction_intro = random.choice(dir_phrase_templates)
    
    main_instruction_templates = [
        f"{direction_intro}, then take the {ordinal(count)} {turn}.",
        f"{direction_intro} and take the {ordinal(count)} {turn}.",
        f"{direction_intro}; turn {turn} at the {ordinal(count)} opportunity.",
    ]
    return random.choice(main_instruction_templates)

def generate_face_instruction(from_dir, to_dir):
    turn = determine_turn_path(from_dir, to_dir)
    if turn == "unknown":
        return f"Turn until you are facing {DIRECTION_DICT[to_dir]}."
    return f"Turn {turn} until you are facing {DIRECTION_DICT[to_dir]}."


def count_intersections_on_final_segment(map_data, path_segment, direction, season='summer'):
    dx, dy = direction
    side_dirs = [(dy, -dx), (-dy, dx)]
    count = 0
    for idx, (x, y) in enumerate(path_segment):
        if idx == 0:
            continue
        has_left = False
        has_right = False
        for i, side in enumerate(side_dirs):
            sx, sy = x + side[0], y + side[1]
            try:
                if 0 <= sy < len(map_data[season]) and 0 <= sx < len(map_data[season][0]):
                    if map_data[season][sy][sx] == 'road':
                        if i == 0:
                            has_left = True
                        else:
                            has_right = True
            except (IndexError, KeyError):
                continue
        if has_left or has_right:
            count += 1
    return count

def generate_final_instruction(map_data, segment, direction, season='summer'):
    num_intersections = count_intersections_on_final_segment(map_data, segment, direction, season=season)

    if num_intersections == 0:
        return "Go straight — your destination is just ahead, before any intersections."
    
    templates = [
        f"Walk straight and pass {num_intersections} intersection{'s' if num_intersections > 1 else ''}, then your destination will be on that stretch.",
        f"Keep walking — after passing {num_intersections} intersection{'s' if num_intersections > 1 else ''}, you'll arrive.",
        f"Continue forward — your goal is right after the {ordinal(num_intersections)} intersection.",
        f"Head straight — the destination is just past the {ordinal(num_intersections)} intersection.",
        f"After you pass {num_intersections} intersection{'s' if num_intersections > 1 else ''}, your destination will be ahead.",
    ]
    return random.choice(templates)


def parse_turn_instruction(selected_instruction):
    # "turn left at the 1st opportunity"
    match = re.search(r"turn (left|right) at the (\d+)(st|nd|rd|th) opportunity", selected_instruction, re.IGNORECASE)
    if match:
        return int(match.group(2))

    # "then take the 1st left"
    match = re.search(r"then take the (\d+)(st|nd|rd|th) (left|right)", selected_instruction, re.IGNORECASE)
    if match:
        return int(match.group(1))

    # "and take the 1st left"
    match = re.search(r"and take the (\d+)(st|nd|rd|th) (left|right)", selected_instruction, re.IGNORECASE)
    if match:
        return int(match.group(1))

    # "pass N intersections" or "after passing N intersections"
    match = re.search(r"(pass|passing) (\d+) intersection", selected_instruction, re.IGNORECASE)
    if match:
        return int(match.group(2))

    # "after the 1st intersection" / "past the 2nd intersection"
    match = re.search(r"(after|past) the (\d+)(st|nd|rd|th) intersection", selected_instruction, re.IGNORECASE)
    if match:
        return int(match.group(2))

    raise ValueError(f"Cannot parse instruction: {selected_instruction}")

def simulate_blind_execution(path, map_data, season, start_direction, instructions, closet=None):
    dir_to_vec = {'north': (0, -TILE_SIZE), 'east': (TILE_SIZE, 0), 'south': (0, TILE_SIZE), 'west': (-TILE_SIZE, 0)}
    cur_pos = path[0]
    cur_dir = start_direction
    target_pos = path[-1]

    for line in instructions:
        if "Turn " in line and "facing " in line:
            match = re.search(r"Turn (left|right|around)? ?(?:until you are facing|to face) (north|south|east|west)", line)
            if match:
                cur_dir = match.group(2)
        elif any(k in line for k in ["take the ", "turn left at ", "turn right at"]):
            match_turn = re.search(r"take the (\d+)(st|nd|rd|th) (left|right)", line, re.IGNORECASE)
            if not match_turn:
                match_turn = re.search(r"turn (left|right) at the (\d+)(st|nd|rd|th)", line, re.IGNORECASE)
                if match_turn:
                    turn_side = match_turn.group(1).lower()
                    target_branch = int(match_turn.group(2))
                else:
                    continue
            else:
                target_branch = int(match_turn.group(1))
                turn_side = match_turn.group(3).lower()

            current_branch_count = 0
            steps_taken = 0
            while current_branch_count < target_branch and steps_taken < 30:
                dx, dy = dir_to_vec[cur_dir]
                next_x, next_y = cur_pos[0] + dx, cur_pos[1] + dy
                if not (0 <= next_y < len(map_data[season]) and 0 <= next_x < len(map_data[season][0])):
                    break
                if map_data[season][next_y][next_x] != 'road':
                    break
                cur_pos = (next_x, next_y)
                steps_taken += 1

                side = (dy, -dx) if turn_side == "left" else (-dy, dx)
                sx, sy = cur_pos[0] + side[0], cur_pos[1] + side[1]
                if 0 <= sy < len(map_data[season]) and 0 <= sx < len(map_data[season][0]):
                    if map_data[season][sy][sx] == 'road':
                        current_branch_count += 1

            if current_branch_count == target_branch:
                dir_order = ['north', 'east', 'south', 'west']
                cur_idx = dir_order.index(cur_dir)
                if turn_side == 'left':
                    cur_dir = dir_order[(cur_idx - 1) % 4]
                else:
                    cur_dir = dir_order[(cur_idx + 1) % 4]
            else:
                return False

        elif any(k in line.lower() for k in ["destination", "arrive", "intersection", "stretch", "ahead", "straight"]):
            steps_taken = 0
            while steps_taken < 30:
                if closet and cur_pos in closet:
                    return True
                if cur_pos == target_pos:
                    return True
                dx, dy = dir_to_vec[cur_dir]
                next_x, next_y = cur_pos[0] + dx, cur_pos[1] + dy
                if not (0 <= next_y < len(map_data[season]) and 0 <= next_x < len(map_data[season][0])):
                    break
                if map_data[season][next_y][next_x] != 'road':
                    break
                cur_pos = (next_x, next_y)
                steps_taken += 1

    if closet and cur_pos in closet:
        return True
    return cur_pos == target_pos


def path_to_turn(path, 
                 map_data, 
                 mode,
                 MAP_ROWS,
                 MAP_COLS,
                 season,
                 start_direction,
                 wrong_turns=False,
                 closet=None):
    
    if wrong_turns:
        include_obs = True
    else:
        include_obs = False
        
    dir_inverse = {v: k for k, v in DIRECTION_DICT.items()}

    current_dir = dir_inverse[start_direction]
    instructions = []
    segment = []

    # --- Initial check: need a turn? ---
    start_idx = 0
    if len(path) >= 2:
        x1, y1 = path[0]
        x2, y2 = path[1]
        first_move = (x2 - x1, y2 - y1)
        if first_move != current_dir:
            instructions.append(generate_face_instruction(current_dir, first_move))
            current_dir = first_move

    # --- Main path ---
    segment = [path[start_idx]]
    for i in range(start_idx+1, len(path)):
        x1, y1 = path[i - 1]
        x2, y2 = path[i]
        move = (x2 - x1, y2 - y1)

        if move == current_dir:
            segment.append((x2, y2))
        else:
            turn = determine_turn_path(current_dir, move)
            if turn in ['left', 'right']:
                branches = count_branches(map_data, segment, current_dir, turn, season=season)
                branches = max(1, branches)
                curr_instruction = generate_instruction(turn, branches, current_dir)
                if include_obs:
                    obs = get_first_person( (x1, y1),
                                            DIRECTION_DICT[current_dir], 
                                            map_data, 
                                            season, 
                                            MAP_ROWS, 
                                            MAP_COLS, 
                                            TILE_SIZE)
                    encoded_obs = encode_obs(obs,
                                            season)
                    candidates = encoded_obs[1:]
                    distinct_obs = [
                        item for item in candidates
                        if "road that you can step on" not in item
                        and "roads that you can step on" not in item
                        and "out of the map boundary" not in item
                    ]
                    if len(distinct_obs) >= 2:
                        sampled_obs = random.sample(distinct_obs, 2)
                    elif len(distinct_obs) == 1:
                        remaining = [item for item in candidates if item not in distinct_obs]
                        if remaining:
                            sampled_obs = distinct_obs + random.sample(remaining, 1)
                        else:
                            sampled_obs = distinct_obs
                    else:
                        sampled_obs = random.sample(candidates, min(2, len(candidates))) if candidates else []

                    encoded_obs = fix_another_usage(sampled_obs)
                    if len(encoded_obs) == 2:
                        encoded_obs = f"{encoded_obs[0][:-1]} and {encoded_obs[1][:-1]}."
                    elif len(encoded_obs) == 1:
                        encoded_obs = ' '.join(encoded_obs)
                        encoded_obs = encoded_obs[:-1] + '.'
                    else:
                        encoded_obs = ""
                    curr_instruction = curr_instruction+ f" At the intersection you will see {encoded_obs}"
                instructions.append(curr_instruction)
            else:
                instructions.append(f"Make a turn to face {DIRECTION_DICT[move]}.")
            current_dir = move
            segment = [path[i-1], path[i]]

    if len(segment) >= 1:
        instructions.append(generate_final_instruction(map_data, segment, current_dir, season=season))
        
    imperfect_info = []
    if wrong_turns:
        turn_indices = [idx for idx, instr in enumerate(instructions[:-1])
                        if any(phrase in instr for phrase in ["take the ", "turn left at ", "turn right at"])]
        if turn_indices:
            n_wrong_tiles = 1 if mode == 'easy' else 2
            max_attempts = 20
            for _ in range(max_attempts):
                temp_instructions = list(instructions)
                temp_imperfect_info = []
                selected_indices = random.sample(turn_indices, min(n_wrong_tiles, len(turn_indices)))
                selected_instructions = [instructions[i] for i in selected_indices]

                for instruction_idx, selected_instruction in zip(selected_indices, selected_instructions):
                    modified_instruction = selected_instruction
                    num_turns = parse_turn_instruction(selected_instruction)
                    if num_turns == 1:
                        delta_count, turn_count = change_tile_num(num_turns, True, ranges=[1, 2])
                    else:
                        delta_count, turn_count = change_tile_num(num_turns, True, ranges=[-1, 1, 2])
                        
                    temp_imperfect_info.append(f"At step {instruction_idx+1}, the number of turns is changed by {delta_count}.")
                    temp_instructions[instruction_idx] = modified_instruction.replace(ordinal(num_turns), ordinal(turn_count), 1)

                if not simulate_blind_execution(path, map_data, season, start_direction, temp_instructions, closet):
                    instructions = temp_instructions
                    imperfect_info = temp_imperfect_info
                    break
            else:
                return None, None
        else:
            return None, None

    for i in range(len(instructions)):
        if i == 0 and instructions[i].startswith('Continue going'):
            instructions[i] = instructions[i].replace('Continue going', 'Going')
        instructions[i] = f'Step {i+1}. {instructions[i]}'

    return instructions, imperfect_info