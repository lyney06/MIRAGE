import numpy as np
from pdb import set_trace as st

def run_one_episode(agent,
                    task_name,
                    logger,
                    args,
                    ):
    reward, traj, step_count = agent.run(task_name, 
                                         args=args
                                         )

    logger.colored_log(f"Task {task_name}:", f"ends with reward: {reward:.3f}", color="cyan")
    # logger.save_gif(task_name, reward)
    # st()
    return traj, reward, step_count