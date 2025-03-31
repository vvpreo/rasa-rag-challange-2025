#! .venv/bin/python

import os.path
import pprint
import sys
from typing import List, Tuple, Dict, Any

import numpy as np
import yaml

from scripts.apptools import get_embedding

with open('store/faq_vectorized.yml', "r", encoding="utf-8") as f:
    faq_data = yaml.safe_load(f)


def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Computes the cosine similarity between two vectors."""
    v1, v2 = np.array(vec1), np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def search_tags(query_embedding: List[float]) -> List[Tuple[float, Dict[str, Any]]]:
    """Searches tags using cosine similarity."""
    results = []
    for tag in faq_data["tags"]:
        similarity = _cosine_similarity(query_embedding, tag["vector"])
        results.append((similarity, tag))
    return sorted(results, key=lambda x: x[0], reverse=True)


def search_questions(query_embedding: List[float]) -> List[Tuple[float, Dict[str, Any]]]:
    """Searches questions using cosine similarity."""
    results = []
    for faq in faq_data["faq"]:
        similarity = _cosine_similarity(query_embedding, faq["question_vectors"])
        results.append((similarity, faq))
    return sorted(results, key=lambda x: x[0], reverse=True)


def get_top_answers(query_embedding: List[float], score_threshold: float = 0.5, k: int = 3) -> List[Dict]:
    p = list()
    top_answers = search_questions(query_embedding)

    for score, answer in top_answers[:k]:
        if score >= score_threshold:
            p.append({
                'question': answer['question'],
                'answer': answer['answer'],
            })
    return p


def prepare_system_prompt(
        user_msg_embedding: List[float],
        score_threshold: float = 0.5,
        k: int = 3) -> List[str]:
    p = get_top_answers(user_msg_embedding, score_threshold, k)

    if not p:
        return []

    return [
        '''You are expert in motorcycles. You're goal is to give best possible answer to the question''',
        f'''Retrieved info from vector store in yml format:\n```\n{yaml.safe_dump(p)}\n```''',
        f'''Avoid using markdown formatting''',
        f'''Answer may contain multiple sentences, but MUST be written in ONE line (without `\\n`)''',
        f'''Full conversation below, end's with user's latest inquiry''',
    ]


if __name__ == "__main__":
    text = sys.argv[1]

    tmp_file = '.tmp_last_query.yml'

    lq = yaml.safe_load(open(tmp_file, 'r')) if os.path.isfile(tmp_file) else {}

    embedding = lq.get(text, get_embedding(text))
    lq[text] = embedding

    yaml.dump(lq, open('scripts/_tmp_last_query.yml', 'w'))

    for item in prepare_system_prompt(embedding):
        print(item)

    # print("#" * 80)
    # print("TAGS")
    # print("#" * 80)
    #
    # for score, t in search_tags(embedding)[:3]:
    #     print(score, t['description'])
    #
    # print("#" * 80)
    # print("QUESTIONS")
    # print("#" * 80)
    # for score, q in search_questions(embedding)[:3]:
    #     print(score, q['question'])
    #     print(q['answer'])
