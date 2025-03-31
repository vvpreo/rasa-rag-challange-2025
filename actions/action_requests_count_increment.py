import sys
from typing import Any, Text, Dict, List

import rasa_sdk.events as events
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions import AppCustomAction


class ActionRequestsIncrementor(AppCustomAction):
    __action_name__ = "action_requests_count_increment"

    async def run(self, dispatcher: CollectingDispatcher, trckr: Tracker, domain: Dict[Text, Any], ) -> List[
        Dict[Text, Any]]:
        self.dbg(trckr)
        req_count: int = int(trckr.slots['requests_count'])
        return [events.SlotSet("requests_count", req_count + 1)]
