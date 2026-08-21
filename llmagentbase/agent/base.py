import re
from common.llms import llm, token_num, TOKEN_LIMITS
from pdb import set_trace as st


class Agent:
    def __init__(   self, 
                    env,
                    instruction,
                    in_context,
                    logger,
                    model_name,
                    temperature,
                    thinking=False,
                    ):
        self.env = env
        self.instruction = instruction
        self.in_context = in_context
        self.logger = logger
        self.model_name = model_name
        self.temperature = temperature
        self.thinking = thinking
        self.available_actions = []
        self.mode_recs = []
        
    def remove_think(self, content):
        splitted_text = content.split('</think>')
        if getattr(self, 'thinking', False) and len(splitted_text) == 1:
            print("\033[31mERROR: Did not finish thinking\033[0m")
        return splitted_text[-1]
    
    def format_action(self,
                      action):
        action = action.replace('\n', ' ').strip()
        # self.logger.colored_log("Action Before:", action, color="blue")

        action = self.remove_think(action)
        
        triple_match = re.search(r'```([^`]+)```', action)
        if triple_match:
            action = triple_match.group(1).strip()
        else:
            single_match = re.search(r'`([^`]+)`', action)
            if single_match:
                action = single_match.group(1).strip()
            else:
                patterns = [
                    r'[Tt]herefore\s*,?\s*the\s+action\s+I\s+will\s+take\s+is\s+([^\.]+)',
                    r'[Tt]herefore\s*,?\s*I\s+will\s+take\s+([^\.]+)',
                    r'[Tt]herefore\s*,?\s*action\s*:\s*([^\.]+)',
                ]
                matched = False
                for pattern in patterns:
                    match = re.search(pattern, action)
                    if match:
                        action = match.group(1).strip()
                        matched = True
                        break
                if not matched:
                    if 'Action:' in action:
                        action = action.split('Action:')[1]
                    elif 'action:' in action:
                        action = action.split('action:')[1]
                    elif '**Action**:' in action:
                        action = action.split('**Action**:')[1]

        action = action.replace('Observation:', '') #for thinking models only
        action = action.strip()

        if action.startswith('['):
            action = f"think{action}"

        for formats in self.available_actions:
            if action.endswith(formats):
                action = formats
        return action

    def get_action(self, prompt, max_tokens, stop, reset_context=False):
        print(token_num(prompt))
        action = llm(prompt,
                     model_name=self.model_name,
                     temperature=self.temperature,
                     max_tokens=max_tokens,
                     stop=stop,
                     reset_context=reset_context,
                     thinking=getattr(self, 'thinking', False))
        if action is None: 
            action = ''
        action = self.format_action(action)
        # print(prompt)
        # breakpoint()
        return action
    
    def skip_env(self):
        return
    
    def close_env(self):
        return

    def log_frame(self, action, step, add_to_history=True):
        return

    def construct_prompt(self,
                         traj,
                        ):
        raise NotImplementedError("You need to implement a prompt constructor. ")
    
    def reset_env(self):
        raise NotImplementedError("You need to implement reset_env. ")
    
    def step(self, 
             action,
             reward=0,
             done=False,
             info=None):
        if info is None:
            info = {}
        if action.startswith('think'):
            observation = 'OK.'
        else:
            try:
                observation, reward, done, info = self.env.step(action)
            except AssertionError as e:
                self.logger.colored_log("Error:", str(e), color="red")
                observation = 'Invalid action! '
        return observation, reward, done, info
    
    def process_input(self,
                      epi_history,
                      info,
                      i):
        limit = int(TOKEN_LIMITS.get(self.model_name, 128000) * 0.9)
        reversed_history = epi_history[::-1]

        selected = []
        total_tokens = 0
        truncated = False
        for item in reversed_history:
            item_tokens = token_num(item)
            if total_tokens + item_tokens > limit:
                truncated = True
                break
            selected.append(item)
            total_tokens += item_tokens

        # reverse back to original order
        selected.reverse()
        prefix = '...omitting previous steps...\n' if truncated else ''
        traj = prefix + ''.join(selected)
        return traj
            
    def run(self,
            task_name,
            args=None):
        # reset task
        observation, reward, done, info, epi_history = self.reset_env()
        self.logger.colored_log("Observation:", observation, color="blue")
        self.logger.log()
        self.consecutive_think = 0
        self.repeated_think = 0
        self.last_think = ''
        self.action_lst = []
        i = 0
        action = None
        while True:
            if i > 0:
                curr_step = f'\nAction: {action}\nObservation: {observation}\n'
            else:
                curr_step = f'Observation: {observation}\n'

            epi_history.append(curr_step)

            if self.check_early_stop(done):
                break

            if self.model_name == 'human':
                if i < len(self.action_lst):
                    action = self.action_lst[i]
                else:
                    action = input("Enter your action: ")
            else:
                full_prompt = self.construct_prompt(traj = self.process_input(epi_history,
                                                                              info, 
                                                                              i))
                action = self.get_action(full_prompt, 
                                         max_tokens=512, 
                                         stop=['\nObservation:', '\nAction:'],
                                         reset_context=(i==0))
            action = action.strip()
            self.log_frame(action, i)
            
            if (action == 'complete') or (action == 'finish') or ('task is complete' in action.lower()):
                self.logger.colored_log("break due to early stopping", color="red")
                break

            if action.startswith('think') or action.startswith('<think>'):
                self.consecutive_think += 1
                if action == self.last_think:
                    self.repeated_think += 1
                self.last_think = action

                observation = 'OK.'
            else:
                self.consecutive_think = 0
                self.repeated_think = 0
                try:
                    observation, reward, done, info = self.env.step(action)
                except AssertionError as e:
                    self.logger.colored_log("Error:", str(e), color="red")
                    observation = 'Invalid action! '

            if info and 'warning' in info and observation != 'OK.':
                observation = f"{observation}\n{info['warning']}"

            self.logger.colored_log(f"Action {i}:", action, color="blue")
            self.logger.colored_log(f"Observation {i+1}:", observation, color="blue")
            self.logger.log() 
            i += 1
            
        traj_str = ''.join(epi_history)
        if not done:
            traj_str += '\nObservation: Maximum Step Exceeded, task failed. '
        if reward == 1:
            traj_str += '\nObservation: Task completed successfully.'

        return reward, traj_str, i
    
    def check_early_stop(self, done):
        if self.consecutive_think >= 5 or self.repeated_think >= 3:
            self.logger.colored_log("break due to consecutive think", f"{self.consecutive_think}, {self.repeated_think}", color="red")
            return True
        if done:
            self.logger.colored_log("break due to done", color="red")
            return True
        return False