import yaml
import numpy as np

import gym

from pdb import set_trace as st

from envs.cuterpg import *
    

def is_env_registered(env_id):
    """Check if an environment is already registered in Gym."""
    return env_id in gym.envs.registry.env_specs


def get_task_range(args, is_train=False):
    if getattr(args, "n_tasks", None) is not None:
        num_tasks = args.n_tasks
    elif is_train:
        num_tasks = getattr(args, "n_train_tasks", 50)
    else:
        num_tasks = getattr(args, "n_test_tasks", 50)

    return list(range(num_tasks))

def load_env(args, is_train=False):
    env = gym.make(args.env)
    return env

