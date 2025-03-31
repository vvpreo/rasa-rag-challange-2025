from typing import Any, Text, Dict, List

import rasa.shared.core.events as core_events
import rasa_sdk.events as events
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions import AppCustomAction


class ActionSessionStart(AppCustomAction):
    __action_name__ = "action_session_start"

    async def run(self, dispatcher: CollectingDispatcher, trckr: Tracker, domain: Dict[Text, Any], ) -> List[Dict[Text, Any]]:
        self.dbg(trckr)
        if not trckr.slots.get("action_session_start_already_triggered", False):
            dispatcher.utter_message(response="utter_greet_user")

        return [
            core_events.SessionStarted().as_dict(),
            events.SlotSet('action_session_start_already_triggered', True),
        ]
