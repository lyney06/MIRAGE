import os
import sys
import imageio
import numpy as np
from pdb import set_trace as st

COLOR_CODES = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}


class Logger(object):
    def __init__(self, args, log_folder="./logs"):
        # make log folder
        self.args = args
        # make log_file
        self.log_file = f"{log_folder}/{args.log_name}/log.txt"
        log_folder = '/'.join(self.log_file.split('/')[:-1])
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        # self.log_folder = log_folder
        # st()
        self.log_folder = self.log_file.split('/log.txt')[0]
        self.gif_folder = f"{self.log_folder}/gifs"
        if not os.path.exists(self.gif_folder):
            os.makedirs(self.gif_folder)
        print(f'\033[34mSaving experiment logs to\033[0m:{self.log_file}')
        open(self.log_file, 'w')

        # experiment data
        self.steps_all = [] # all experiment steps
        self.steps_success = [] # steps for successful experiments
        self.manual_steps = []  # manual steps
        self.frames = []    # frames for gif
        # self.gif_path = os.path.join(gif_folder, f"{args.log_name}.gif")
        # self.gif_path = gif_folder

    def _print(self, text, option='print'):
        if option == "print":
            print(text)
        else:
            raise ValueError("Invalid option")

    def log(self, *args, option="print"):
        text = ' '.join([str(arg) for arg in args])
        default_stdout = sys.stdout  # assign console output to a variable
        self._print(text, option=option)
        f = open(self.log_file, 'a')
        sys.stdout = f
        self._print(text, option=option)
        sys.stdout = default_stdout  # set stdout back to console output

    def log_experiment(self, steps, success):
        """Log experiment steps and success"""
        self.steps_all.append(steps)
        if success:
            self.steps_success.append(steps)

    def log_frame(self, frame):
        """Store a frame for gif generation"""
        self.frames.append(frame)

    def clear_frame(self):
        self.frames = []

    def save_summary(self):
        """Save summary statistics"""
        avg_steps_all = np.mean(self.steps_all) if self.steps_all else 0
        avg_steps_success = np.mean(self.steps_success) if self.steps_success else 0

        summary_text = (f"Average Steps (All): {avg_steps_all:.2f}\n"
                        f"Average Steps (Successful): {avg_steps_success:.2f}\n")
        self.log(summary_text)

    def save_gif(self, task_name, reward):
        """Saves the collected frames as a gif"""
        if self.frames:
            success = 'success' if reward == 1 else 'failure'
            imageio.mimsave(f"{self.gif_folder}/{task_name}_{success}.gif", self.frames, fps=0.8)
            self.clear_frame()
            self.log(f"Saved visualization GIF at {self.gif_folder}")
        else:
            self.log("No frames recorded, skipping GIF generation.")
            
    def colored_log(self, prefix, message="", color="yellow", option="print"):
        """
        Print a colored prefix + normal message using ANSI codes.

        Args:
            prefix (str): The part to color
            message (str): The normal message (default empty)
            color (str): Color name ("yellow", "red", etc.)
            option (str): 'print' (default). (You used to have 'console', but now only 'print')
        """
        color_code = COLOR_CODES.get(color.lower(), "")
        reset_code = COLOR_CODES["reset"]

        # Check if prefix needs a colon
        if prefix and not prefix.endswith(":") and message != "":
            prefix = prefix + ":"

        text = f"{color_code}{prefix}{reset_code} {message}"
        self.log(text, option=option)