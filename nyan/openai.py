import logging
import os
from dataclasses import dataclass
from typing import Optional, Sequence, List, Dict, Any, cast
from multiprocessing.pool import ThreadPool

import openai
import copy

# Инициализация клиента OpenAI из переменных окружения
def _get_openai_client():
    """Инициализирует клиент OpenAI с настройками из переменных окружения"""
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    api_key = os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    
    # Автоматически добавляем /v1 если его нет (для Ollama и других локальных серверов)
    if not base_url.endswith("/v1") and not base_url.endswith("/v1/"):
        if base_url.endswith("/"):
            base_url = base_url + "v1"
        else:
            base_url = base_url + "/v1"
    
    # Для локальных моделей (например, Ollama) может не быть API ключа
    if not api_key and ("localhost" in base_url or "127.0.0.1" in base_url or "192.168" in base_url):
        api_key = "ollama"  # Заглушка для Ollama
    
    client = openai.OpenAI(
        base_url=base_url,
        api_key=api_key,
    )
    return client


@dataclass
class OpenAIDecodingArguments:
    max_tokens: int = 2400
    temperature: float = 0.0
    top_p: float = 0.95
    n: int = 1
    stream: bool = False
    stop: Optional[Sequence[str]] = None
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0


DEFAULT_ARGS = OpenAIDecodingArguments()


def openai_completion(
    messages: List[Dict[str, Any]],
    decoding_args: OpenAIDecodingArguments = DEFAULT_ARGS,
    model_name: str = "gpt-4",
    sleep_time: int = 2,
) -> str:
    # Получаем модель из переменных окружения, если она задана
    # Это позволяет переопределить модель через .env файл для всех вызовов
    env_model = os.getenv("LLM_MODEL")
    if env_model:
        model_name = env_model
    
    decoding_args = copy.deepcopy(decoding_args)
    assert decoding_args.n == 1
    
    client = _get_openai_client()
    
    while True:
        try:
            # Используем новый API OpenAI (v1.0+)
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=decoding_args.max_tokens,
                temperature=decoding_args.temperature,
                top_p=decoding_args.top_p,
                n=decoding_args.n,
                stream=decoding_args.stream,
                stop=decoding_args.stop,
                presence_penalty=decoding_args.presence_penalty,
                frequency_penalty=decoding_args.frequency_penalty,
            )
            break
        except Exception as e:
            logging.warning("OpenAI error: %s.", e)
            if "Please reduce" in str(e) or "maximum context length" in str(e).lower():
                decoding_args.max_tokens = int(decoding_args.max_tokens * 0.8)
                logging.warning(
                    "Reducing target length to %d, Retrying...",
                    decoding_args.max_tokens,
                )
            else:
                raise e
    return cast(str, response.choices[0].message.content.strip())


def openai_batch_completion(
    batch: List[List[Dict[str, Any]]],
    decoding_args: OpenAIDecodingArguments = DEFAULT_ARGS,
    model_name: str = "gpt-4",
    sleep_time: int = 2,
) -> List[str]:
    completions = []
    with ThreadPool(len(batch)) as pool:
        results = pool.starmap(
            openai_completion,
            [(messages, decoding_args, model_name, sleep_time) for messages in batch],
        )
        for result in results:
            completions.append(result)
    return completions
