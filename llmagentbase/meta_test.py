from envs.utils import get_task_range
from llmagentbase.run.collect import collect_trajs
from pdb import set_trace as st

def meta_test(args, logger):
    task_range = get_task_range(args, is_train=False)
    collect_trajs(  task_range,
                    logger,
                    args,
                    is_train=False,
                    )