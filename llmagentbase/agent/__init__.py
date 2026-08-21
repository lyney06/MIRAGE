from .navigator import Navigator
from .chef import Chef
from .adventurer import Adventurer
from pdb import set_trace as st


def build_agent(env,
                instruction,
                in_context,
                logger,
                train_temperature,
                args = None):
    if args.env_type == 'navigation':
        manual = args.manual_type
        agent = Navigator(  env,
                            instruction,
                            in_context,
                            logger,
                            args.agent_model,
                            train_temperature,
                            manual)
            
    elif args.env_type == 'cooking':
        manual = args.manual_type
        agent = Chef(  env,
                            instruction,
                            in_context,
                            logger,
                            args.agent_model,
                            train_temperature,
                            manual)
    elif args.env_type == 'roguelike':
        manual = args.manual_type
        agent = Adventurer(  env,
                                instruction,
                                in_context,
                                logger,
                                args.agent_model,
                                train_temperature,
                                manual)
        
        
    return agent