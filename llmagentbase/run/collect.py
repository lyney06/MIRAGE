import pygame
from common.utils import set_seed, rew_logging, initialize_logs, compute_accuracies
from envs.utils import load_env
from llmagentbase.run.run_episode import run_one_episode
from llmagentbase.prompts import get_prompt
from llmagentbase.agent import build_agent
from llmagentbase.utils import log_task
from pdb import set_trace as st

def collect_trajs(  task_range,
                    logger,
                    args,
                    is_train,
                    ):
    # set_seed(args.seed)
    env = load_env(args, is_train)
    # get prompts
    instruction = get_prompt('instruction', env, args)
    in_context = get_prompt('react', env, args)
            
    rewards = initialize_logs()
    # init agent
    agent = build_agent(None,
                        instruction,
                        in_context,
                        logger,
                        args.train_temperature if is_train else args.test_temperature,
                        args)
    if args.env_type == 'roguelike':
        success_fn = lambda r: r != 0
    else:
        success_fn = lambda r: r == 1
    
    for task_idx, task_name in enumerate(task_range):
        log_task(task_idx, task_name, logger)
        # load env for agent
        agent.env = env
        # really run one task
        traj, reward, step_count = run_one_episode(  agent,
                                                    task_name=task_name,
                                                    logger=logger,
                                                    args=args,
                                                    )
        compute_accuracies(agent.mode_recs, logger)
        success = success_fn(reward)
        logger.log_experiment(step_count, success)

        rewards = rew_logging(rewards,
                              reward,
                              task_idx,
                              logger=logger,
                              success_fn=success_fn,
                              debug=args.debug)

        logger.save_gif(task_name, reward)
        agent.close_env()

    logger.save_summary()
    return