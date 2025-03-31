#! .venv/bin/python

import yaml

from scripts.apptools import get_variations_of

FNAME_PREPEND = './tests/e2e/bye/bye__'

prompt = '''
I need you to generate different phrases that AI agent may use to direct user to goal oriented conversation and not chitchatting with him/her. be gentle.
We are speaking about motorcycles and can answer to general questions and provide information about particular models. You may highlight this information in your rephrasals.
'''

if __name__ == "__main__":
    variations = get_variations_of(prompt, 20, 200)
    for variation in variations:
        print(variation)
