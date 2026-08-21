import cv2
import pygame
import numpy as np
import textwrap
from llmagentbase.agent.base import Agent


class Navigator(Agent):
    def __init__(   self, 
                    env,
                    instruction,
                    in_context,
                    logger,
                    model_name,
                    temperature,
                    manual_type
                    ):
        super().__init__(env,
                        instruction,
                        in_context,
                        logger,
                        model_name,
                        temperature)
        self.manual_type = manual_type
        self.mode_recs = []

    def construct_prompt(self,
                         traj
                        ):
        if ('qwen3' in self.model_name.lower() or 'deepseek' in self.model_name.lower()) and "Warning: Do not put" not in self.instruction:
            self.instruction += "\nWarning: Do not put 'Observation:' in your answer. Otherwise it will be truncated!"
        if self.manual_type is None:
            prompt = f"{self.instruction}\n{self.in_context}\nNow it's your turn:\n"
        else:
            prompt = f"{self.instruction}\n{self.in_context}\nNow it's your turn:\nStep-by-Step Guide to Complete the Task:\n{self.manual}\n\nTry your best to navigate to the destination:\n"
        prompt += f"{traj}\nAction: "
        return prompt
    
    def reset_env(self):
        reward, done, info = 0, False, {}
        epi_history = []
        observation = self.env.reset()
        self.manual, self.imperfect_info = self.env.get_manual(self.manual_type)
        if self.manual_type in [3, 4]:
            observation = self.env.unwrapped.env.take_action('void')[0]

        if self.manual_type is not None:
            self.logger.colored_log("Loaded Manual:", self.manual, color="yellow")
            self.logger.colored_log("Imperfect Info:", self.imperfect_info, color="yellow")

        self.logger.colored_log("Horizon:", self.env.get_horizon(), color="green")
        return observation, reward, done, info, epi_history

    def log_frame(self, action, step, add_to_history=True):
        frame = pygame.surfarray.array3d(pygame.display.get_surface())
        frame = np.rot90(frame, k=-1)
        frame = np.fliplr(frame)
        action = f'Action {step+1}: {action}'
        frame = self.add_text_to_frame(frame, action)

        if add_to_history:
            self.logger.log_frame(frame)

    def add_text_to_frame(self, frame, action_text, font_scale=1, text_color=(255, 255, 255), bg_color=(0, 0, 0)):
        # Get original frame dimensions
        height, width, channels = frame.shape
        extra_space_right = width  # Add the same width as the original frame for self.manual
        text_height = 150  # Fixed extra space below

        # Create a new blank image with extra space on the right and below
        new_frame = np.full((height + text_height, width + extra_space_right, channels), bg_color, dtype=np.uint8)

        # Copy the original frame into the new image
        new_frame[:height, :width] = frame

        # Handle action text
        font_scale_rec = font_scale
        if "think[" in action_text:
            font_scale = font_scale * 0.5  # Reduce font size
            wrapped_text = textwrap.fill(action_text, width=65)
        else:
            wrapped_text = action_text

        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness = 2

        # Add action text below the original frame
        for i, line in enumerate(wrapped_text.split('\n')):
            text_size = cv2.getTextSize(line, font, font_scale, thickness)[0]
            text_x = (width - text_size[0]) // 2  # Centered below the image
            text_y = height + int((i + 1) * 30 * font_scale)
            cv2.putText(new_frame, line, (text_x, text_y), font, font_scale, text_color, thickness, cv2.LINE_AA)

        # Add self.manual text in the right extra space
        if hasattr(self, "manual") and self.manual:
            manual_x_start = width + 10  # Start manual text slightly inside the right space
            manual_y_start = 30  # Start text near the top of the right space

            # Process each original line separately
            count = 0
            for i, original_line in enumerate(self.manual.splitlines()):  # Preserve existing new lines
                wrapped_lines = textwrap.wrap(original_line, width=70)  # Wrap only if a line is too long

                for j, line in enumerate(wrapped_lines):
                    text_size = cv2.getTextSize(line, font, font_scale_rec * 0.5, thickness)[0]
                    text_x = manual_x_start  # Aligned to the right section
                    text_y = manual_y_start + int(count * 30 * font_scale_rec)  # Adjust for wrapped lines

                    cv2.putText(new_frame, line, (text_x, text_y), font, font_scale_rec * 0.5, text_color, thickness, cv2.LINE_AA)
                    count += 1
        return new_frame