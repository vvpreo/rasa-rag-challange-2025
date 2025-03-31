from collections import namedtuple
from pprint import pprint
from typing import Any, Text, Dict, List

import rasa.shared.core.events as core_events
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import rasa_sdk.events as events

from actions import oapi_history, ACTIONS_STUBBED, AppCustomAction
from scripts import faq
from scripts.apptools import get_embedding, query_openrouter


class ActionQuerySearchCaptureRequest(AppCustomAction):
    __action_name__ = "action_trigger_search_faq_capture_request"

    async def run(self, dispatcher: CollectingDispatcher, trckr: Tracker, domain: Dict[Text, Any], ) -> List[
        Dict[Text, Any]]:
        self.dbg(trckr)
        text_input = trckr.latest_message['text']
        return [events.SlotSet('user_search_faq_request', text_input)]


class ActionQuerySearch1(AppCustomAction):
    __action_name__ = "action_trigger_search_faq"

    async def run(self, dispatcher: CollectingDispatcher, trckr: Tracker, domain: Dict[Text, Any], ) -> List[
        Dict[Text, Any]]:
        self.dbg(trckr)
        text_input = trckr.slots.get('user_search_faq_request', "ABC")
        embedding = get_embedding(text_input)

        if ACTIONS_STUBBED:
            answers = faq.get_top_answers(embedding, score_threshold=.45, k=1)
            if answers:
                return [events.BotUttered(text=answers[0]['answer'].replace("\n", ' '))]
            else:
                return [events.BotUttered('LLM summarization STUBBED')]
        else:
            sys_prompt = faq.prepare_system_prompt(embedding, score_threshold=.45, k=3)
            messages = [{"role": "system", "content": msg} for msg in sys_prompt] + oapi_history(trckr)
            final_response = query_openrouter('openai/chatgpt-4o-latest', messages)
            return [
                events.BotUttered(
                    text=final_response.replace("\n", ' '),
                )
            ]
