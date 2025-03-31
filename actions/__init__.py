import os
import sys
from typing import List, Text

from rasa_sdk import Action, Tracker

import litellm
litellm.litellm.suppress_debug_info = True


def oapi_history(tracker: Tracker) -> List[dict]:
    messages = list()
    for e in tracker.events:
        if e.get('event') == 'user':
            messages.append({'role': 'user', 'content': e['text']})
        elif e.get('event') in {'agent', 'bot'}:
            messages.append({'role': 'assistant', 'content': e['text']})
    return messages


ACTIONS_STUBBED = True if os.environ.get('ACTIONS_STUBBED', 'False').lower() == 'true' else False
print(f"{ACTIONS_STUBBED=}")


class AppCustomAction(Action):
    __action_name__ = 'XXX'

    def dbg(self, trckr: Tracker):
        try:
            flows = trckr.current_state().get('stack')
            flows = [s['flow_id'] for s in flows]
        except:
            flows = []

        print('🤞', self.name(), end=' ')
        print('MSG:', trckr.latest_message.get('text') if trckr.latest_message else None, end=' ')
        print('AT:', flows, end=' ')
        print()
        # print('AT:', trckr.current_state().get('stack').get('flow_id', None), 'ACTION:', self.name(), 'MSG:',
        #       trckr.latest_message)
        # sys.exit()

    def name(self) -> Text:
        return self.__action_name__
