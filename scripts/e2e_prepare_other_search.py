#! .venv/bin/python

import yaml

from scripts.apptools import get_variations_of

FNAME_PREPEND = './tests/e2e/other_search__'

variations_prompt = '''
I need you to generate 120 phrases that would direct user to other_search flow.
Theese phrases must not be:
- General questions about motorbikes
- Questions about particular motorbike models
- Thees phrases should not be good bye phrases.

Here is overall idea of the flow:
Call 'other_search' flow if:
- User's intent looks like a search for moto accessories/equipment/other. Examples:
- I need top 3 navigation systems for ATVs
- Where I can tune my bike?
- What shocks are suitable for Aprilia Tuareg 660?
- Recommend me 3 driving schools in Madrid.
'''
variations = get_variations_of(variations_prompt, 100, 200)

if __name__ == "__main__":

    test_cases = list()
    for variation in variations:
        print("FOR OTHER SEARCH: ", variation)
        test_case = {
            'test_case': f"OTHER SEARCH: {variation}",
            'steps': [
                {
                    'user': variation,
                    'assertions': [{'flow_started': 'other_search'}]
                },
            ]
        }
        test_cases.append(test_case)
    with open(FNAME_PREPEND + 'other_search__variations.yml', 'w') as f:
        yaml.dump({'test_cases': test_cases}, f)
