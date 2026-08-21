import argparse
import yaml
import wandb
from common.utils import set_seed
from common.logger import Logger
from llmagentbase import meta_test


def main(args, logger):
    # set seed
    set_seed(args.seed)
    if not args.debug:
        wandb.init(
            project="mirage", 
            name=args.log_name,
            config={k: str(v) if v is None else v for k, v in vars(args).items()}
        )
    meta_test(args, logger)


if __name__ == "__main__":
    # initialize argparse
    parser = argparse.ArgumentParser(description="llmagentbase")
    parser.add_argument(
        "--seed", type=int, default=0,
        help="random seed"
    )
    parser.add_argument(
        '--env', type=str, default='VillageNav-v0',
        help="Environment ID or name (e.g. VillageNav-v0, Cooking-easy-v0, Roguelike-easy-v0)"
    )
    parser.add_argument(
        '--agent_model', type=str, default='gpt-4o-mini'
    )
    parser.add_argument(
        "--test_temperature", "--temperature", type=float, default=0,
        dest="test_temperature",
        help="Temperature for LLM generation"
    )
    parser.add_argument(
        "--manual_type", type=int, default=None,
    )
    parser.add_argument(
        "--exploration_model", type=str, default=None, 
    )
    parser.add_argument(
        "--note", type=str, default='',
    )
    parser.add_argument(
        "--n_tasks", type=int, default=None,
        help="Number of tasks to evaluate per run"
    )
    parser.add_argument(
        "--n_test_tasks", type=int, default=None,
        help="Number of test tasks to evaluate per run"
    )
    parser.add_argument(
        "--debug", action="store_true",
    )
    parser.add_argument(
        "--log_dir", "--log_folder", type=str, default="./logs",
        dest="log_dir",
        help="Directory to save logs"
    )

    args = parser.parse_args()

    # Environment specific type resolution
    env_lower = args.env.lower()
    if 'nav' in env_lower:
        args.env_type = 'navigation'
    elif 'cook' in env_lower:
        args.env_type = 'cooking'
    elif 'rogue' in env_lower:
        args.env_type = 'roguelike'
    else:
        raise ValueError(
            f"Unsupported environment '{args.env}'. Expected name containing 'nav', 'cooking', or 'roguelike'."
        )
        
    # Load environment config defaults
    with open(f'envs/env_configs/{args.env_type}.yaml', 'r') as file:
        yaml_args = yaml.safe_load(file) or {}

    for key, value in yaml_args.items():
        if getattr(args, key, None) is None:
            setattr(args, key, value)

    if args.n_tasks is not None:
        args.n_test_tasks = args.n_tasks

    # Sanitize model names for clean filesystem & wandb logging
    agent_model_tag = args.agent_model.replace('/', '_') if args.agent_model else 'None'
    exp_model_tag = args.exploration_model.replace('/', '_') if args.exploration_model else 'None'
    str_debug = 'debug_' if args.debug else ''
    args.log_name = (
        f"{str_debug}{args.env}/Manual_{args.manual_type}_{exp_model_tag}_{agent_model_tag}"
    )

    # Initialize logger after all args and configs are set
    logger = Logger(args, log_folder=args.log_dir)

    # Run main
    main(args=args, logger=logger)