import os
import json
from pdb import set_trace as st

# saving to json files for potential future use
def trajs_to_json(  task_range,
                    memories,
                    best_rewards,
                    best_trials,
                    last_rewards,
                    is_train,
                    instruction,
                    in_context,
                    logger,
                    args):
    folder_name = "./logs/data/"
    file_name = f"{folder_name}{args.log_name}::training_{is_train}.json"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    all_data = {}
    all_data['instruction'] = instruction
    all_data['in_context'] = in_context
    all_data['success'] = {}
    all_data['failure'] = {}
    for idx, task_name in enumerate(task_range):
        data = {'memory': memories[idx],
                'best_trial': best_trials[idx],
                'rewards': last_rewards[idx]}
        if best_rewards[idx] == 1: #successful task
            all_data['success'][task_name] = data
        elif best_rewards[idx] != -1:
            all_data['failure'][task_name] = data
    with open(file_name, "w") as outfile:
        json.dump(all_data, outfile)

    logger.log(f'[green]Saved data to[/] {file_name}', option='console')
