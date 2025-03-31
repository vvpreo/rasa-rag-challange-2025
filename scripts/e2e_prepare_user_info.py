#! .venv/bin/python
import json
from collections import defaultdict
from pprint import pprint
import random
from typing import List

import yaml
from pydantic import BaseModel, Field

from scripts import moto_db
from scripts.apptools import query_openrouter_fast, get_variations_of
import rasa_test_suite as rts


def clear_non_alphanum(text) -> str:
    return ''.join(char for char in text if char.isalnum() or char == ' ')


FNAME_PREPEND = './tests/e2e_finetune/obtain_user_info__'

# per_data_opts = get_variations_of('''
# I need phrases, each MUST contain
# - name
# - gender [male|female]
# - age [15 to 130]
# - email. Must contain alphanumeric characters, dots, `@` symbols only.
#
# Format:
# <name>|<gender>|<age>|<email>
# ''', 50)
per_data_opts = [
    "John|male|25|john.doe25@example.com",
    "Emily|female|30|emily.smith30@example.net",
    "Michael|male|40|michael.brown40@example.org",
    "Sophia|female|22|sophia.jones22@example.com",
    "Daniel|male|35|daniel.miller35@example.net",
    "Olivia|female|28|olivia.davis28@example.org",
    "James|male|45|james.wilson45@example.com",
    "Emma|female|33|emma.moore33@example.net",
    "David|male|50|david.taylor50@example.org",
    "Isabella|female|37|isabella.anderson37@example.com",
    "Matthew|male|60|matthew.thomas60@example.net",
    "Mia|female|42|mia.jackson42@example.org",
    "Joseph|male|55|joseph.white55@example.com",
    "Ava|female|29|ava.harris29@example.net",
    "Christopher|male|48|christopher.martin48@example.org",
    "Charlotte|female|31|charlotte.thompson31@example.com",
    "Ethan|male|20|ethan.garcia20@example.net",
    "Amelia|female|23|amelia.martinez23@example.org",
    "Noah|male|32|noah.robinson32@example.com",
    "Harper|female|36|harper.clark36@example.net",
    "Alexander|male|65|alexander.lewis65@example.org",
    "Evelyn|female|27|evelyn.lee27@example.com",
    "William|male|70|william.walker70@example.net",
    "Abigail|female|40|abigail.hall40@example.org",
    "Benjamin|male|80|benjamin.allen80@example.com",
    "Ella|female|50|ella.young50@example.net",
    "Samuel|male|55|samuel.king55@example.org",
    "Scarlett|female|35|scarlett.wright35@example.com",
    "Henry|male|45|henry.scott45@example.net",
    "Avery|female|60|avery.green60@example.org",
    "Liam|male|75|liam.adams75@example.com",
    "Grace|female|85|grace.baker85@example.net",
    "Lucas|male|90|lucas.gonzalez90@example.org",
    "Zoe|female|95|zoe.nelson95@example.com",
    "Mason|male|100|mason.carter100@example.net",
    "Lily|female|105|lily.mitchell105@example.org",
    "Logan|male|110|logan.perez110@example.com",
    "Chloe|female|115|chloe.roberts115@example.net",
    "Jacob|male|120|jacob.turner120@example.org",
    "Aria|female|125|aria.phillips125@example.com",
    "Elijah|male|130|elijah.campbell130@example.net",
    "Samantha|female|15|samantha.parker15@example.org",
    "Aiden|male|18|aiden.evans18@example.com",
    "Addison|female|19|addison.edwards19@example.net",
    "Gabriel|male|21|gabriel.collins21@example.org",
    "Madison|female|24|madison.stewart24@example.com",
    "Anthony|male|26|anthony.sanchez26@example.net",
    "Layla|female|34|layla.morris34@example.org",
    "Ryan|male|27|ryan.rogers27@example.com",
    "Hannah|female|29|hannah.reed29@example.net",
    "Andrew|male|31|andrew.cook31@example.org",
    "Natalie|female|38|natalie.morgan38@example.com"
]


def gen_tests():
    ts = rts.RasaTestSuite(
        fixtures=[{'will_call_proper_flow': [{'requests_count': 10}]}]
    )

    for p in per_data_opts:
        print("FOR: ", p)
        name, gender, age, email = p.split('|')

        tc = rts.TestCase(fixtures=['will_call_proper_flow'], test_case=p, steps=list())
        tc.steps.append(rts.Step(user='Find me best winter helmet for ATV', assertions=[]))
        tc.steps.append(
            rts.Step(user=name,
                     assertions=[rts.Assertion(slot_was_set=[rts.SlotWasSetItem(name='user_name', value=name)])]))
        tc.steps.append(
            rts.Step(user=email,
                     assertions=[rts.Assertion(slot_was_set=[rts.SlotWasSetItem(name='user_email', value=email)])]))
        tc.steps.append(
            rts.Step(
                user='YES',
                assertions=[
                    rts.Assertion(slot_was_set=[rts.SlotWasSetItem(name='user_confirmed_personal_data', value=True)])]))
        ts.test_cases.append(tc)

    ts.serialize(FNAME_PREPEND + 'random_data.yml')


if __name__ == "__main__":
    gen_tests()
