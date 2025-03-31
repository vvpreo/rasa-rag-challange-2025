#! .venv/bin/python

import yaml

from scripts.apptools import get_variations_of

FNAME_PREPEND = './tests/e2e/bye__'


prompt = '''
I need you to generate 120 different good bye phrases. 
Let them be with and without '!' at the end
It MUST be absolutely clear from phrases generated that author want's to to finish conversation
'''

if __name__ == "__main__":
    variations = get_variations_of(prompt, 100, 200)

    test_cases = list()
    for variation in variations:
        print("FOR INTRO: ", variation)
        test_case = {
            'test_case': f"BYE: {variation}",
            'steps': [
                {
                    'user': variation,
                    'assertions': [{'flow_started': 'good_bye_user'}]
                },
            ]
        }
        test_cases.append(test_case)
    with open(FNAME_PREPEND + 'bye__variations.yml', 'w') as f:
        yaml.dump({'test_cases':test_cases}, f)
