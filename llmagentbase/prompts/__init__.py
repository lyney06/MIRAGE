from .navigation import nav_react, nav_react_tiles, nav_react_obs, nav_tiles_obs, nav_react_turns, nav_turns_obs, nav_instruction_summer, nav_instruction_winter
from .cooking import cook_instruction, cook_react, cook_react_perfect, cook_react_descriptive, cook_react_multiserve, cook_react_none
from .roguelike import game_instruction, game_react, game_react_type3, game_react_type2, game_react_type1, game_instruction_back, game_react_type0

PROMPTS = {'navigation':{},
           'cooking': {},
           'roguelike': {},
           }

PROMPTS['navigation']['instruction'] = {'summer': nav_instruction_summer,
                                        'winter': nav_instruction_winter}
PROMPTS['navigation']['react'] = {'encoded': nav_react}
PROMPTS['navigation']['react_perfect'] = {  'encoded_turns': nav_react_turns,
                                            'encoded_tiles': nav_react_tiles,
                                            'encoded_descriptive': nav_react_obs,
                                            'encoded_turns_obs': nav_turns_obs,
                                            'encoded_tiles_obs': nav_tiles_obs,
                                          }

PROMPTS['cooking']['instruction'] = {'encoded': cook_instruction}
PROMPTS['cooking']['react'] = {'encoded': cook_react}
PROMPTS['cooking']['react_none'] = {'encoded': cook_react_none}
PROMPTS['cooking']['react_perfect'] = {'encoded': cook_react_perfect}
PROMPTS['cooking']['react_descriptive'] = {'encoded': cook_react_descriptive,
                                           'multiserve': cook_react_multiserve,
                                           }

PROMPTS['roguelike']['instruction'] = {'base': game_instruction,
                                       'reversible': game_instruction_back}
PROMPTS['roguelike']['react'] = {'encoded': game_react}
PROMPTS['roguelike']['react_detailed'] = {'encoded':game_react_type3}
PROMPTS['roguelike']['react_list'] = {'encoded':game_react_type2}
PROMPTS['roguelike']['react_vague'] = {'encoded':game_react_type1}
PROMPTS['roguelike']['react_checkpoint'] = {'encoded':game_react_type0}

def get_prompt(type, env, args):
    if args.env_type == 'navigation':
        if type == 'instruction':
            if 'Seasonal' in args.env:
                return PROMPTS[args.env_type][type]['winter']
            else:
                return PROMPTS[args.env_type][type]['summer']

        if args.manual_type is None:
            few_shot_type = 'react'
            prompt_type = 'encoded'
        elif args.manual_type == 0:
            few_shot_type = 'react_perfect'
            prompt_type = 'encoded_turns'
        elif args.manual_type == 1: 
            few_shot_type = 'react_perfect'
            prompt_type = 'encoded_tiles'
        elif args.manual_type == 2:
            few_shot_type = 'react_perfect'
            prompt_type = 'encoded_descriptive'
        elif args.manual_type == 3:
            few_shot_type = 'react_perfect'
            prompt_type = 'encoded_turns_obs'
        elif args.manual_type == 4:
            few_shot_type = 'react_perfect'
            prompt_type = 'encoded_tiles_obs'

    elif args.env_type == 'cooking':
        if type == 'instruction':
            return PROMPTS[args.env_type][type]['encoded']
        
        if 'crop-gone' in args.env:
            few_shot_type = 'react_descriptive'
            prompt_type = 'encoded'
        elif 'storage-loss' in args.env:
            few_shot_type = 'react_descriptive'
            prompt_type = 'encoded'
        elif 'rookie-chef' in args.env:
            few_shot_type = 'react_descriptive'
            prompt_type = 'encoded'
        elif 'multiserve' in args.env:
            few_shot_type = 'react_descriptive'
            prompt_type = 'encoded'
        else:
            if args.manual_type is None:
                few_shot_type = 'react_none'
                prompt_type = 'encoded'
            elif args.manual_type == 0:
                few_shot_type = 'react'
                prompt_type = 'encoded'
            elif args.manual_type == 1:
                few_shot_type = 'react_perfect'
                prompt_type = 'encoded'
            elif args.manual_type == 2:
                few_shot_type = 'react_descriptive'
                prompt_type = 'encoded'
            elif args.manual_type == 4:
                few_shot_type = 'react_descriptive'
                prompt_type = 'encoded'

    elif args.env_type == 'roguelike':
        if type == 'instruction':
            is_reversible = getattr(env.unwrapped, 'reversible', getattr(args, 'back', False)) if env is not None else getattr(args, 'back', False)
            if is_reversible:
                return PROMPTS[args.env_type]['instruction']['reversible']
            else:
                return PROMPTS[args.env_type]['instruction']['base']
        else:
            if args.manual_type is None:
                few_shot_type = 'react'
                prompt_type = 'encoded'
            elif args.manual_type == 0:
                few_shot_type = 'react_checkpoint'
                prompt_type = 'encoded'
            elif args.manual_type == 1:
                few_shot_type = 'react_vague'
                prompt_type = 'encoded'
            elif args.manual_type == 2:
                few_shot_type = 'react_list'
                prompt_type = 'encoded'
            elif args.manual_type >= 3:
                few_shot_type = 'react_detailed'
                prompt_type = 'encoded'
      

    return PROMPTS[args.env_type][few_shot_type][prompt_type]
