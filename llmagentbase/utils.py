def log_task(task_idx, task_name, logger):
    logger.log()
    logger.colored_log("----------------------------------", color="red")
    logger.colored_log(f"Task {task_idx+1}: {task_name}", color="red")
    logger.colored_log("----------------------------------", color="red")


def plan_to_str(plans):
    res = ''
    for i, plan in enumerate(plans):
        res += f'{i+1}. {plan}\n'
    if not res:
        res = "There is no existing plan yet. You are starting from scratch."
    return res