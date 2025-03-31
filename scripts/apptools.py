#! .venv/bin/python
import json
import os
from typing import List

import openai
import requests
import yaml
from pydantic import BaseModel, Field
from rasa.e2e_test.assertions import Assertion


def query_openrouter(model: str, messages: list[dict], response_format: dict = None, dry_run=False) -> str:
    """
    Query OpenRouter with a specified model, system prompt, and user prompt.

    Args:
        model (str): The model name to use.
        system_prompt (list[str]): A list of system instructions.
        user_prompt (list[str]): A list of user messages.

    Returns:
        dict: The response from OpenRouter.
    """
    # import pprint
    # pprint.pprint(messages)

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    if response_format:
        payload = {"response_format": {"type": "json_object"}}
        messages = [{"role": "system", "content": response_format}] + messages
        # print("RESPONSE FORMAT:", response_format)
    else:
        payload = dict()

    payload.update({
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024 * 10,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
    })

    if dry_run:
        jresp = json.dumps(payload, indent=1, ensure_ascii=False)
        print(jresp)
        return 'DRY_RUN'

    response = requests.post(url, json=payload, headers=headers)
    jresp = response.json()
    try:
        return jresp['choices'][0]['message']['content']
    except Exception as e:
        print(f"ERROR: {e}")
        print(f"BODY : {jresp}")


def query_openrouter_fast(model: str, system_prompt: list[str], user_prompt: list[str],
                          response_format: dict = None, dry_run=False) -> str:
    messages = [{"role": "system", "content": msg} for msg in system_prompt] + \
               [{"role": "user", "content": msg} for msg in user_prompt]
    return query_openrouter(model, messages, response_format, dry_run)


# OpenAI Embedding Model
EMBEDDING_MODEL = "text-embedding-3-small"


def get_embedding(text):
    """Fetch embedding from OpenAI API with retry logic."""

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    print(text)
    print("Retrieving embedding...")
    print()
    response = openai.OpenAI(api_key=OPENAI_API_KEY).embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    emb = response.data[0]
    return emb.embedding


def get_variations_of(question: str, items_min: int, items_max: int = 100) -> List[str]:
    class QuestionVariations(BaseModel):
        '''Object representing variations of initial phrase'''
        variations: List[str] = Field(
            description="Different phrasings of the same",
            min_items=items_min,
            max_items=items_max
        )

    schema = QuestionVariations.model_json_schema()
    schema = json.dumps(schema, ensure_ascii=False)

    response = query_openrouter_fast(
        system_prompt=[],
        user_prompt=[
            'You are expert in rephrsing.',
            'Provide variatons for given question in json format according to idea provided:',
            question,
            f'!!! Not less then {items_min} variations'
        ],
        model='openai/gpt-4o',
        response_format=schema
    )

    print(response)

    return QuestionVariations.model_validate_json(response).variations

# if __name__ == "__main__":
#     model_name = "openai/chatgpt-4o-latest"
#     system_msgs = ["You are a helpful AI assistant."]
#     user_msgs = ["What is the capital of France?"]
#
#     result = query_openrouter(model_name, system_msgs, user_msgs)
#     pprint(result)

# if __name__ == "__main__":
#     embds = get_embedding("Questions related to the curriculum, academic programs, and educational philosophy")
#     print(embds)
