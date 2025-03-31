#! .venv/bin/python
import json
from typing import List

import yaml
from pydantic import BaseModel, Field

from scripts.apptools import query_openrouter_fast, get_variations_of

with open('store/faq_tagged.yml', "r", encoding="utf-8") as f:
    faq_data = yaml.safe_load(f)


def clear_non_alphanum(text) -> str:
    return ''.join(char for char in text if char.isalnum() or char == ' ')


FNAME_PREPEND = './tests/e2e/faq__'

import scripts.rasa_test_suite as rts


def gen_original():
    ts = rts.RasaTestSuite()
    for qa in faq_data['faq']:
        q = qa['question']
        a = qa['answer']
        print("QUESTION: " + q)
        test_name = clear_non_alphanum(q)

        ts.test_cases.append(
            rts.TestCase(test_case=q, steps=[rts.Step(user=q, assertions=[rts.Assertion(flow_started='faq')])]))
    ts.serialize(FNAME_PREPEND + 'original.yml')

def gen_variations():
    ts = rts.RasaTestSuite()
    for qa in faq_data['faq']:
        q = qa['question']
        a = qa['answer']
        q = get_variations_of(q, 1)[0]
        print("QUESTION: " + q)
        test_name = clear_non_alphanum(q)
        ts.test_cases.append(
            rts.TestCase(test_case=q, steps=[rts.Step(user=q, assertions=[rts.Assertion(flow_started='faq')])]))
    ts.serialize(FNAME_PREPEND + 'variations.yml')


if __name__ == "__main__":
    gen_original()
    gen_variations()
