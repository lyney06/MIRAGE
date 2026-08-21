#!/usr/bin/env python3

import re
import tiktoken
import time
from concurrent.futures import ThreadPoolExecutor
from joblib import Memory
import requests
from openai import OpenAI
from pdb import set_trace as st

memory = Memory("cachedir", verbose=0)


import os

DEFAULT_VLLM_BASE_URL = os.environ.get("VLLM_BASE_URL", "http://127.0.0.1:8000/v1")
DEFAULT_API_KEY = "EMPTY"


def _is_qwen_model(model_name):
    return "qwen" in model_name.lower()

def _is_deepseek_model(model_name):
    return "deepseek" in model_name.lower()


def _build_messages(prompt, model_name, thinking):
    """
    Build OpenAI-compatible chat messages.

    For newer Qwen/vLLM, do NOT inject '/nothink' into the prompt.
    Thinking should be controlled via extra_body.chat_template_kwargs.enable_thinking.
    """
    if isinstance(prompt, str):
        user_content = prompt.strip()
        return [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_content},
        ]

    if isinstance(prompt, list):
        messages = []
        for m in prompt:
            msg = m.copy()
            messages.append(msg)
        return messages

    raise ValueError("Prompt must be a string or a list of messages.")


def _build_extra_body(model_name, thinking):
    """
    Build vLLM/OpenAI extra_body.

    For Qwen thinking models, enable_thinking controls whether the model emits
    thinking content. This replaces the old '/nothink' prompt prefix.
    """
    if _is_qwen_model(model_name):
        return {
            "chat_template_kwargs": {
                "enable_thinking": bool(thinking)
            }
        }

    return None


def _single_vllm_call(
    client,
    messages,
    model_name,
    temperature,
    max_tokens,
    stop,
    thinking=False,
):
    kwargs = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stop": stop,
    }

    extra_body = _build_extra_body(model_name, thinking)
    if extra_body is not None:
        kwargs["extra_body"] = extra_body

    response = client.chat.completions.create(**kwargs)
    message = response.choices[0].message.content
    return message, response


def remove_think_if_present(content):
    """
    Safely remove Qwen-style thinking text if it appears.

    Unlike the old remove_think(), this does not print an error when </think>
    is absent, because absence of thinking is expected when enable_thinking=False.
    """
    if not content:
        return content

    if "</think>" in content:
        return content.split("</think>")[-1].strip()

    return content.strip()


def _postprocess_message(message, model_name):
    if message is None:
        return ""

    if _is_qwen_model(model_name):
        message = remove_think_if_present(message)
        message = message.replace("Action: ", "")

    return message.strip()


def _print_timing_and_usage(response, message, elapsed_time):
    if hasattr(response, "usage") and response.usage is not None:
        completion_tokens = response.usage.completion_tokens
        # print(f"Number of tokens decoded = {completion_tokens}")
        # print(f"Tokens per second = {completion_tokens / max(elapsed_time, 1e-6):.3f}")
    else:
        num_tokens = len((message or "").split())
        # print(f"Approximate number of tokens decoded = {num_tokens}")
        # print(f"Approximate tokens per second = {num_tokens / max(elapsed_time, 1e-6):.3f}")

    # print(f"Total time for decoding = {elapsed_time:.3f}")


def vllm_llm(
    prompt,
    model_name,
    temperature=0.08,
    max_tokens=128,
    stop=None,
    thinking=False,
    base_url=DEFAULT_VLLM_BASE_URL,
    api_key=DEFAULT_API_KEY,
):

    if thinking:
        max_tokens = max(max_tokens, 3072)

    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    # Preserve your previous behavior: respect caller-provided stop sequence.
    # If stop is not specified (None), we do not force a stop sequence.

    messages = _build_messages(prompt, model_name, thinking)

    start_time = time.time()

    message, response = _single_vllm_call(
        client=client,
        messages=messages,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        stop=stop,
        thinking=thinking,
    )

    elapsed_time = time.time() - start_time

    _print_timing_and_usage(response, message, elapsed_time)

    message = _postprocess_message(message, model_name)

    # print("Ran prompt", flush=True)

    if message == "":
        print("Message was None or empty!")
        print(response)

    return message


