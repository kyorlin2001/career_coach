import os
from functools import lru_cache

from huggingface_hub import InferenceClient

MODEL_ID = os.environ.get("HF_MODEL_ID", "meta-llama/Llama-3.1-8B-Instruct")
HF_TOKEN = os.environ.get("HF_TOKEN")


@lru_cache(maxsize=1)
def get_client() -> InferenceClient:
    return InferenceClient(
        model=MODEL_ID,
        token=HF_TOKEN,
    )


def generate_text(prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
    client = get_client()
    response = client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()