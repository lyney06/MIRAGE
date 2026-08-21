import random
try:
    import wandb
except Exception:
    wandb = None
import numpy as np
from collections import Counter
from pdb import set_trace as st

def set_seed(seed) -> None:
    """Sets random seed for reproducibility
    Args:
        seed (int): Target seed to set
    """
    random.seed(seed)
    np.random.seed(seed)
    # import torch
    # torch.manual_seed(seed)
    # if torch.cuda.is_available():
    #     torch.cuda.manual_seed_all(seed)

def error_handle(signum, frame):
    """Time limit error handle"""
    raise Exception("Oops time is up")


def initialize_logs(task_range=None):
    rewards = []
    return rewards


def get_rew_and_sr(rewards, total_task=None, success_fn=lambda r: r == 1):
    """
    Compute average reward and success rate, with flexible success criteria.

    Args:
        rewards (List[float]): List of reward values.
        total_task (int, optional): Total number of tasks. If None, use len(rewards).
        success_fn (Callable): Function to determine whether a reward counts as success.

    Returns:
        Tuple[float, float]: (average reward, success rate)
    """
    total = total_task if total_task is not None else len(rewards)
    avg_reward = np.sum(rewards) / total
    success_rate = np.sum([1 for r in rewards if success_fn(r)]) / total
    return avg_reward, success_rate


def rew_logging(rewards, 
                reward,
                task_idx,
                logger,
                success_fn=lambda r: r == 1,
                debug=False,
                ):
    rewards.append(reward)
    logger.log('print', "*************************")

    (avg_r, sr) = get_rew_and_sr(rewards, success_fn=success_fn)

    logger.colored_log(
        f"Task {task_idx + 1}:",
        f"Average reward: {avg_r:.3f}, average success rate: {sr:.3f}",
        color="green"
    )
    if not debug and wandb is not None:
        wandb.log({'reward': avg_r, 
                   'success_rate': sr})

    return rewards


def compute_accuracies(mode_recs, logger):
    if not mode_recs:
        return
    
    counter = Counter()

    for gt_mode, mode in mode_recs:
        if gt_mode == "N/A":
            continue
        counter['total'] += 1
        if gt_mode == mode:
            counter['correct'] += 1
            counter[f'{gt_mode}_correct'] += 1
        counter[f'{gt_mode}_total'] += 1

    overall_acc = counter['correct'] / counter['total'] if counter['total'] else 0
    explore_acc = counter['Explore_correct'] / counter['Explore_total'] if counter['Explore_total'] else 0
    follow_acc = counter['Follow_correct'] / counter['Follow_total'] if counter['Follow_total'] else 0

    accuracies = {
        'overall_accuracy': overall_acc,
        'explore_accuracy': explore_acc,
        'follow_accuracy': follow_acc
    }
    
    logger.log(f"\033[33mOverall Accuracy: \033[0m\033[32m{accuracies['overall_accuracy']:.2%}\033[0m")
    logger.log(f"\033[33mExplore Accuracy: \033[0m\033[32m{accuracies['explore_accuracy']:.2%}\033[0m")
    logger.log(f"\033[33mFollow Accuracy: \033[0m\033[32m{accuracies['follow_accuracy']:.2%}\033[0m")

    return 
