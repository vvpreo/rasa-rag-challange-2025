#! .venv/bin/python
import os

from rasa.__main__ import main
import pprint
import sys
from typing import Optional, Dict, Any

import questionary
from prompt_toolkit.styles import Style

import rasa.core.channels.console
import rasa.cli.utils as cli_utils
import rasa.shared.utils.cli

original_input = rasa.core.channels.console._get_user_input


async def input_override(previous_response: Optional[Dict[str, Any]], ):
    print()
    button_response = None
    if previous_response is not None:
        button_response = rasa.core.channels.console._print_bot_output(previous_response, is_latest_message=True)

    if button_response is not None:
        response = await cli_utils.payload_from_button_question(button_response)
        if response == cli_utils.FREE_TEXT_INPUT_PROMPT:
            response = await input_override(None)
    else:
        next_phrase = ALL_PHRASES.pop(0) if ALL_PHRASES else None
        if next_phrase:
            # if next_phrase not in ['/session_start']:
            #     _ = input(f"NEXT PHRASE: '{next_phrase}'")
            response = next_phrase
            print("\033[38;2;179;115;214mYour input ->\033[0m  ", end='')
            rasa.shared.utils.cli.print_color(response, color='\033[33m')
        else:
            question = questionary.text(
                "",
                qmark="Your input ->",
                style=Style([("qmark", "#b373d6"), ("", "#b373d6")]),
            )
            response = await question.ask_async()
    return response.strip() if response is not None else None


rasa.core.channels.console._get_user_input = input_override

if __name__ == "__main__":

    ALL_PHRASES = open(os.environ.get('USER_PHRASES', 'tests/cli.txt'), 'r', ).read().split('\n')
    ALL_PHRASES = [ph for ph in ALL_PHRASES if ph.strip()]

    for phrase in ALL_PHRASES:
        print(phrase)

    if sys.argv[0].endswith("-script.pyw"):
        sys.argv[0] = sys.argv[0][:-11]
    elif sys.argv[0].endswith(".exe"):
        sys.argv[0] = sys.argv[0][:-4]

    sys.exit(main())
