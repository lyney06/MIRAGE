import os
import openai
from joblib import Memory
from pdb import set_trace as st

memory = Memory('cachedir', verbose=0)

def is_openrouter_model(model_name):
    if not model_name:
        return False
    return model_name.startswith("openrouter:") or model_name.startswith("OR:")

@memory.cache
def openai_llm(prompt, 
               model_name, 
               temperature=0.08, max_tokens=128, stop=None, thinking=False):
    if model_name in ['o3-mini', 'o1']:
        messages = [{'role': 'user', 'content': prompt}] if isinstance(prompt, str) else prompt
        response = openai.ChatCompletion.create(
            model=model_name,
            messages = messages,
            max_completion_tokens=20000, 
            stop=stop,
        )
        response_content = response["choices"][0]['message']['content']
    else:
        messages = [{'role': 'user', 'content': prompt}] if isinstance(prompt, str) else prompt
        response = openai.ChatCompletion.create(
            model=model_name,
            messages = messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
        )
        response_content = response["choices"][0]['message']['content']
    return response_content

