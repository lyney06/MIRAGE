import re
import tiktoken
import ollama
from joblib import Memory
# from transformers import LlamaTokenizer  # type: ignore
# from transformers import AutoTokenizer
from pdb import set_trace as st
memory = Memory('cachedir', verbose=0)
import time

def remove_think(content):
    return content.split('</think>')[-1]

def ollama_llm(prompt, model_name, temperature=0.08, max_tokens=128, stop=None):
    if 'qwen3' in model_name.lower():
        stop = ['\nObservation']
    # Prepare messages
    if isinstance(prompt, str):
        user_content = prompt.strip()
        if 'qwen3' in model_name.lower():
            user_content = '/nothink ' + user_content  # only for qwen3
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': user_content}
        ]
    elif isinstance(prompt, list):
        messages = []
        for m in prompt:
            msg = m.copy()
            if msg['role'] == 'user' and 'qwen3' in model_name.lower():
                msg['content'] = '/nothink ' + msg['content']
            messages.append(msg)
    else:
        raise ValueError("Prompt must be a string or a list of messages.")
    
    start_time = time.time()
    response = ollama.chat(
        model=model_name,
        messages=messages,
        options={
            'num_predict': max_tokens,
            'temperature': temperature,
            'num_ctx': 32768
        },
        stream=True
    )

    # Deal with streamed output in case it can be truncated early
    message = ''
    num_chunks = 0
    for i, chunk in enumerate(response):
        if chunk:
            num_chunks += 1
            message += chunk['message']['content']
            if stop:
                stop_pos = len(message)
                for token in stop:
                    pos = message.find(token)
                    if pos != -1:
                        stop_pos = min(stop_pos, pos)
                if stop_pos < len(message):
                    print(f'Truncating for stop tokens: {message[stop_pos:]}')
                    message = message[:stop_pos]
                    break

    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f'Total time for decoding = {elapsed_time:.3f}')
    print(f'Number of tokens decoded = {num_chunks}')
    print(f'Tokens per second = {num_chunks/elapsed_time:.3f}')

    if 'qwen3' in model_name.lower(): message = message.replace('Action: ', '')
    print('Ran prompt', flush=True)

    if message is None or message == '':
        print('Message was None or empty!')
        print(response)

    # Clean <think> only for qwen3
    if 'qwen3' in model_name:
        message = remove_think(message)

    return message.strip()
