from typing import Any, Text, Dict, List

import rasa_sdk.events as events
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions import AppCustomAction, oapi_history, ACTIONS_STUBBED
from scripts.apptools import query_openrouter


class ActionSearchOther(AppCustomAction):
    __action_name__ = "action_trigger_search_other"

    __prompt = f'''
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
                    Conversation below. pay special attention to the last message.
                    '''.replace('                    ', ''),

    async def run(self, dispatcher: CollectingDispatcher, trckr: Tracker, domain: Dict[Text, Any], ) -> List[
        Dict[Text, Any]]:
        self.dbg(trckr)

        if ACTIONS_STUBBED:
            return [events.BotUttered(text="OTHER SEARCH STUBBED", )]

        messages = oapi_history(trckr)
        messages.append({"role": "system", "content": self.__prompt})
        final_response = query_openrouter(
            model='perplexity/sonar-reasoning-pro', messages=messages)
        return [
            events.BotUttered(
                text=final_response.replace("\n", ' '),
            )
        ]
