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


FNAME_PREPEND = './tests/e2e_other/specs__'

# special_req_variations = get_variations_of('''
# I need you to generate me what exactly user may ask additionally
#
# Call 'vehicles_search_by_make_or_model' flow if:
# - User asks to search info about particular make and/or model. Examples:
# - USER: How many HP has Yamaha R1?
# - USER: What is the seat height for AJP SPR 240X Enduro?
# - USER: Help me with specific model
# - USER: <Manufacturer> <model name>
# - USER: <model name> <Manufacturer>
#
# Here is your previous answer:
#   "variations": [
#     "What is the top speed of the Kawasaki Ninja ZX-10R?",
#     "Can you tell me the horsepower of the Ducati Panigale V4?",
#     "I'm looking for the weight of the BMW S1000RR.",
#     "Do you have the engine specs for the Honda CBR1000RR?",
# ]
#
# It is good, But i need you not to add manufacturers and models.
#
# This is what I would like to see:
#   "variations": [
#     "What is the top speed?",
#     "Can you tell me the horsepower?",
#     "I'm looking for the weight.",
#     "Do you have the engine specs?",
# ]
#
# Try again please. And let your requests vary. I mean horsepower for one time is enough.
# For half of your rephrases, please add something that must be searched and not written in specs.
# For example: What is the actual price?
# Your answer:
# ''', 50)

special_req_variations = [
    "How fast can it go?", "What is the horsepower rating?", "Can you provide the weight details?",
    "Do you have information on the engine specifications?", "What is the seat height?",
    "Could you find out the torque?", "I'm curious about the fuel capacity.", "What is the fuel efficiency?",
    "Do you know the tire size?", "What is the braking system like?", "Can you tell me the number of cylinders?",
    "What is the warranty coverage?", "Do you have the dimensions?", "What is the ground clearance?",
    "Can you check the transmission type?", "What type of suspension does it have?", "What is the mileage?",
    "Could you find the release year?", "What is the current market price?", "Do you have the color options?",
    "What is the service interval?", "Could you find out the insurance cost?", "What are the safety features?",
    "Can you tell me the resale value?", "What is the reliability rating?", "Do you know the maintenance cost?",
    "What is the availability?", "Could you check the user reviews?", "What is the maximum load capacity?",
    "I'm interested in the interior features.", "What is the exterior design like?",
    "Can you find the sound system details?", "What is the navigation system?",
    "Do you have the infotainment features?", "What is the climate control system?",
    "Can you tell me about the lighting system?", "What are the customization options?",
    "Could you find the production locations?", "What is the history of this model?",
    "Do you know the key competitors?", "What is the brand reputation?", "Can you tell me the manufacturing materials?",
    "What is the emissions rating?", "Could you find the safety ratings?", "What is the crash test rating?",
    "Do you have the sales figures?", "What is the popularity ranking?", "Can you find the awards received?",
    "What is the electric range?", "Do you know the hybrid capabilities?", "What is the towing capacity?"]

# mm_intro_vars = get_variations_of('''
# Tell me about Yamaha Grizzly EPS SE
# I need options for `Tell me about` part.
# Any vehicle might follow these options.
# I'd prefer short options, like people use when chatting/speaking
# ''', items_min=10)
mm_intro_vars = [
    '', '', '', '', '', '', '', '', '', '', 'Tell me about', "What's up with", "Give me the scoop on",
    "What's the deal with", "Fill me in on", "What can you tell me about", "Share some info about", "Enlighten me on",
    "What's the lowdown on", "Got any details on", "Let me know about", "What's the story with", "Any news on",
    "Clue me in about", "Give me the rundown on", "Spill the beans about"]


def gen_tests_for_make_and_models():
    makes = moto_db.get_list_of_makes()
    mm = [(m, moto_db.get_list_of_models(moto_db.get_specs_by_make(m))) for m in makes]
    mm = sorted(mm, key=lambda e: len(e[1]), reverse=True)

    for make, models in mm[:10]:
        ts = rts.RasaTestSuite()
        print("FOR MAKE: ", make)
        for model in random.choices(models, k=3):
            print("FOR MODEL: ", model)
            special_requests = random.choices(special_req_variations, k=2)
            for special_request in special_requests:
                print("\tFOR SPECIAL REQ: ", special_request)
                intro_var = random.choice(mm_intro_vars)
                tc = rts.TestCase(
                    test_case=f"{intro_var} {make} {model}",
                    steps=[
                        rts.Step(
                            user=f'{intro_var} {make} {model}'.strip(),
                            assertions=[rts.Assertion(flow_started='vehicles_search_by_make_and_model')]
                        ),
                        rts.Step(
                            user=make,
                            assertions=[rts.Assertion(
                                slot_was_set=[rts.SlotWasSetItem(name='user_search_specs_make', value=make)]
                            )]
                        ),
                        rts.Step(
                            user=model,
                            assertions=[rts.Assertion(
                                slot_was_set=[rts.SlotWasSetItem(name='user_search_specs_model', value=model)]
                            )]
                        ),
                        rts.Step(
                            user=special_request,
                            assertions=[rts.Assertion(
                                slot_was_set=[
                                    rts.SlotWasSetItem(name='user_search_specific_request', value=special_request)]
                            )]
                        ),
                    ]
                )
                ts.test_cases.append(tc)
        ts.serialize(FNAME_PREPEND + 'make__' + make + '.yml')


def gen_tests_for_variations():
    # ppp = '''
    # Call 'vehicles_search_by_make_or_model' flow if:
    # - User asks to search info about particular make and/or model. Examples:
    # - USER: Help me with specific model
    # '''
    # get_variations_of("Help me with specific model in this context:\n" + ppp, 30)
    intro_variations = [
        "Can you assist me with a particular model?", "I'm looking for information on a certain model.",
        "Could you provide details about a specific vehicle model?", "I need help with a particular car model.",
        "Can you find information on a specific model for me?", "Can you search for a specific car model?",
        "I would like to learn more about a certain vehicle model.", "Can you guide me on a particular model?",
        "I'm interested in details about a specific model.", "Help me find information on a specific model.",
        "Could you assist me with information on a particular model?",
        "I'm looking for details on a specific car model.", "Can you help me with a certain vehicle model?",
        "Please assist me in finding information about a specific model.",
        "Could you provide information on a particular car model?", "I need details on a specific vehicle model.",
        "Can you give me information about a specific model?", "Help me get information on a particular model.",
        "I'm searching for information regarding a specific model.",
        "Could you help me locate details about a certain model?",
        "Can you provide me with details on a specific model?", "I want to know more about a particular car model.",
        "Can you look up information on a specific model for me?", "I require information on a certain vehicle model.",
        "Could you help me find details on a specific model?",
        "Please provide information on a particular vehicle model.", "I need to know about a specific model.",
        "Can you assist me in finding details about a certain car model?",
        "I'd like help with a specific vehicle model.", "Can you offer information on a particular model?"]

    ts = rts.RasaTestSuite()
    for intro_text in intro_variations:
        print("FOR INTRO: ", intro_text)
        tc = rts.TestCase(
            test_case=intro_text,
            steps=[rts.Step(
                user=intro_text,
                assertions=[rts.Assertion(flow_started='vehicles_search_by_make_and_model')])]
        )
        ts.test_cases.append(tc)
    ts.serialize(FNAME_PREPEND + 'intro__variations.yml')


if __name__ == "__main__":
    gen_tests_for_variations()
    gen_tests_for_make_and_models()
