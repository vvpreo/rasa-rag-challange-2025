from typing import Any, Text, Dict, List

import rasa.shared.core.events as core_events
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions import ACTIONS_STUBBED, AppCustomAction
from scripts import communicate_user


class ActionSessionStart(AppCustomAction):
    __action_name__ = "action_session_end"

    async def run(
            self, dispatcher: CollectingDispatcher, trckr: Tracker, domain: Dict[Text, Any], ) -> List[Dict[Text, Any]]:
        self.dbg(trckr)
        user_email = trckr.get_slot("user_email")
        user_name = trckr.get_slot("user_name")
        if user_email and not ACTIONS_STUBBED:
            messages = [
                f'''{user_name},''' if user_name else '',
                f'''Thank you for your conversation!''',
                f'''Please find it below, in case you'd like to revise any details''',
            ]
            for e in trckr.events:
                if e.get('event') == 'user':
                    messages.append(f'''\tYOU: {e['text']}''')
                elif e.get('event') in {'agent', 'bot'}:
                    messages.append(f'''\tMOTO EXPERT: {e['text']}''')

            messages += [
                '''\nJust reply to this message in case you'd like to leave a feedback.'''
            ]

            communicate_user.send_email(to_email=user_email, body='\n'.join(messages))

        print("SESSION ENDED")
        return [core_events.SessionEnded().as_dict()]
