import json
from typing import Any, Text, Dict, List

import rasa_sdk.events as events
import yaml
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions import ACTIONS_STUBBED, AppCustomAction
from scripts import moto_db, apptools


class ActionValidateMake(AppCustomAction):
    __action_name__ = "validate_user_search_specs_make"

    async def run(self, dispatcher: CollectingDispatcher, trckr: Tracker, domain: Dict[Text, Any], ) -> List[
        Dict[Text, Any]]:
        self.dbg(trckr)
        current_val = trckr.slots['user_search_specs_make']
        makes = moto_db.get_make_levenstain(current_val)
        if makes:
            return [events.SlotSet('user_search_specs_make', makes[0].key)]
        else:
            return [
                events.SlotSet('user_search_specs_make', None),
                events.BotUttered(
                    f'''I can't find any brand, named {current_val}, I know only about models 2022-2025.03'''),
            ]


class ActionValidateModel(AppCustomAction):
    __action_name__ = "validate_user_search_specs_model"

    async def run(self, dispatcher: CollectingDispatcher, trckr: Tracker, domain: Dict[Text, Any], ) -> List[
        Dict[Text, Any]]:
        self.dbg(trckr)
        make = trckr.slots['user_search_specs_make']
        make_df = moto_db.get_specs_by_make(make)
        current_val = trckr.slots['user_search_specs_model']
        models = moto_db.get_model_levenstain(current_val, df=make_df)
        if models:
            return [
                events.SlotSet('user_search_specs_model', models[0].key),
            ]
        else:
            bs = '\n'
            return [
                events.SlotSet('user_search_specs_model', None),
                events.BotUttered(f'''Not found for manufacturer '{make}' '''),
                events.BotUttered(
                    f'Here is the list of models 2022-2025.03 according to my database for {make}:\n- {(bs + "- ").join(moto_db.get_list_of_models(make_df))}'),
            ]


class ActionSearchBasic(AppCustomAction):
    __action_name__ = "action_vehicles_search_by_make_and_model_basic"

    async def run(self, dispatcher: CollectingDispatcher, trckr: Tracker, domain: Dict[Text, Any], ) -> List[
        Dict[Text, Any]]:
        self.dbg(trckr)
        make = trckr.slots['user_search_specs_make']
        model_name = trckr.slots['user_search_specs_model']
        print(f"OBTAINING BASE DATA for {make} {model_name}")

        df = moto_db.get_spec_by_make(make)
        df = moto_db.get_specs_by_model(model_name, df=df)

        df_dicts = moto_db.dictify(df)

        responses = [events.BotUttered(f"✅ Models found ({len(df_dicts)}):")]
        for model_spec in df_dicts:
            responses.append(events.BotUttered(f"URL with more details: {model_spec['str_page_url']}"))
            responses.append(
                events.BotUttered(f"{make} {model_name}", metadata={"image": model_spec['str_image_url']})),

            specs = [
                f'''Name: {model_spec['str_make'] + ' ' + model_spec['str_model']}, Year: {model_spec['int_year']}:''']
            specs += [
                f"- {moto_db.cols_descriptions.get(k, 'Other:')}: "
                + str(v).replace("\n", ", ").replace('\t', ' ') for k, v in model_spec.items()
            ]

            responses.append(events.BotUttered('\n'.join(specs)))

        return responses


class ActionSearch(AppCustomAction):
    __action_name__ = "action_vehicles_search_by_make_and_model_internet"

    async def run(self, dispatcher: CollectingDispatcher, trckr: Tracker, domain: Dict[Text, Any], ) -> List[
        Dict[Text, Any]]:
        self.dbg(trckr)
        make = trckr.slots['user_search_specs_make']
        model = trckr.slots['user_search_specs_model']
        specials = trckr.slots['user_search_specific_request']

        if ACTIONS_STUBBED:
            return [events.BotUttered('STUBBED'), ]
        else:
            dispatcher.utter_message(text="Searching internet on your request...")
            df = moto_db.get_spec_by_make(make)
            df = moto_db.get_specs_by_model(model, df=df)

            df_dicts = moto_db.dictify(df)

            response = apptools.query_openrouter_fast(
                model='perplexity/sonar-reasoning-pro',
                system_prompt=[],
                user_prompt=[
                    f'''
                    You are expert in motocycles/ATVs/scooters.
                    And you are assisting AI agent that communicates directly to user.
                    Your goal is to address properly user\'s request for information about vehicle mentioned.
                    You have to rely on information extracted from Database.
                    Database is limited to 2022-2025.03.
                    You may add additional information, but you MUST emphasize that it is YOUR own opinion and not comes from data source.
                    !!! Avoid using markdown syntax in your answer. !!!
                    Every line break will be transformed to a separate message in the channel we are operating.
                    Use your access to internet to provide best answer.
                    Don't duplicate information from DB, but you can point at discrepancy with info obtained from internet if there any.
                    Do not add follow up message.
                    embed links into the message instead of using [<linknum>] syntax
                    ''',
                    f'''
                    Could you please provide summary for user's inquiry about '{make}, {model}?'
                    I've asked user about any special information he/she would like to know about. Here is the answer:
                    special_request: {specials}
                    If it is not clear, mention it in you response.
                    Anyway, I am asking you to provide additional information (even if it was not asked in special_request):
                    - Who is target audience of the model mentioned?
                    - What should be considered when purchasing this model?
                    - What alternatives you may recommend, if you know any?
                    If there is more than one vehicle was extraced from the database, describe core difference.
                    ''',
                    f'''Extracted info in yaml/json format:\n{yaml.safe_dump(df_dicts)}'''
                ]
            )

            print("AI RESPONSE ON DEEP MODEL SEARCH:\n" + response)

            return [
                events.BotUttered(response),
            ]
