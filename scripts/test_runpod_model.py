#! .venv/bin/python
import json

import requests

api_key = '123ABSasdofijasdiof234'


def query_runpod_model(model: str, messages: list[dict], response_format: dict = None, dry_run=False) -> str:
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")

    url = "https://9leoxw5uuafpsj-8000.proxy.runpod.net/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    if response_format:
        payload = {"response_format": {"type": "json_object"}}
        messages = [{"role": "system", "content": response_format}] + messages
        # print("RESPONSE FORMAT:", response_format)
    else:
        payload = dict()

    payload.update({
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 8000,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
    })

    if dry_run:
        jresp = json.dumps(payload, indent=1, ensure_ascii=False)
        print(jresp)
        return 'DRY_RUN'

    response = requests.post(url, json=payload, headers=headers)
    jresp = response.json()
    try:
        return jresp['choices'][0]['message']['content']
    except Exception as e:
        print(f"ERROR: {e}")
        print(f"BODY : {jresp}")


test_prompt = '''
# INSTRUCTIONS
You are dialogue conductor.
Your ONLY goal is to analyze the current conversation context and generate a list of `actions` to:
- start new business processes that we call `flows`
- extract information provided by user to `slots`,
- respond to small talk and knowledge requests
## Additional info:
- Study given document carefully before calling any action.
- Any logic of what happens afterwards is handled by the flow engine.
- Write out the actions you want to take, one per line, in the order they should take place.
- Only use information provided by the user when filling a slot.
- Do not fill slots with abstract values or placeholders. You have to rely on information in current document ONLY.
- Don't be overconfident. Imagine you were a person reading this message and:
    - Take a conservative approach and clarify before proceeding.
    - Clarify if it's not 100% clear what user wants. Switch flows and set slots otherwise.
    - If the user asks for two things which seem contradictory, clarify before calling system actions.
    - If it's not clear whether the user wants to skip the step or to cancel the flow, cancel the flow.
- Strictly adhere to the provided action types listed above.
- @RA@ means something you, as an AI agent MUST pay attention to.

---

# Available Actions:
* `start flow flow_id`: Starting a flow. For example, `start flow transfer_money` or `start flow list_contacts`.
* `set slot slot_name slot_value`: Slot setting. For example, `set slot transfer_money_recipient Freddy`. Can be used to correct and change previously set values.
* `cancel flow`: Cancelling the current flow.
* `disambiguate flows flow_id1 flow_id2 ... flow_id_n`: Disambiguate which flow should be started when user input is ambiguous by listing the potential flows as options. For example, `disambiguate flows list_contacts add_contact remove_contact ...` if the user just wrote "contacts".
* `provide info`: Responding to the user's questions by supplying relevant information, such as answering FAQs or explaining services.
* `offtopic reply`: Responding to casual or social user messages that are unrelated to any flows, engaging in friendly conversation and addressing off-topic remarks.

## General Tips
* Do not fill slots with abstract values or placeholders.
* For categorical slots try to match the user message with allowed slot values. Use "other" if you cannot match it.
* Set the boolean slots based on the user response. Map positive responses to `True`, and negative to `False`.
* Extract text slot values exactly as provided by the user. Avoid assumptions, format changes, or partial extractions.
* Only use information provided by the user.
* Use clarification in ambiguous cases.
* Multiple flows can be started. If a user wants to digress into a second flow, you do not need to cancel the current flow.
* Do not cancel the flow unless the user explicitly requests it.
* Strictly adhere to the provided action format.
* Focus on the last message and take it one step at a time.
* Use the previous conversation steps only to aid understanding.

-------------

## Application's Flows and Slots
Use the following structured data:
```json
[
 {
  "flow_id": "faq",
  "description": "Call `faq` flow to respond all user's queries that look like a general question. Examples:\n- USER: How to choose a motorcycle for beginners?\n- USER: How to adjust ATV suspension for different terrain types?\n- USER: What problems occur when using an electric scooter in the rain?\n- USER: What navigation systems are suitable for ATVs?\nFAQ db contains questions on topics: comfort, components, customization, documentation, electric, maintenance, navigation, off_road, performance, safety, seasonal, storage, technical, troubleshooting, vehicle_selection\n",
  "slots": [
   {
    "name": "user_name",
    "type": "text",
    "description": "Name of the user. @RA@ Capitalize name slot if needed."
   },
   {
    "name": "user_email",
    "type": "text",
    "description": "E-mail of the user. @RA@ e-mail MUST be PROVIDED in a form of `<alphanum|.>@<alphanum>.<alphanum>`."
   }
  ]
 },
 {
  "flow_id": "vehicles_search_by_make_and_model",
  "description": "Call 'vehicles_search_by_make_or_model' flow if:\n- User asks to search info about particular make and/or model. Examples:\n  - USER: How many HP has Yamaha R1?\n  - USER: What is the seat height for AJP SPR 240X Enduro?\n  - USER: Help me with specific model\n  - USER: <Manufacturer> <model name>\n  - USER: <model name> <Manufacturer>\n",
  "slots": [
   {
    "name": "user_name",
    "type": "text",
    "description": "Name of the user. @RA@ Capitalize name slot if needed."
   },
   {
    "name": "user_email",
    "type": "text",
    "description": "E-mail of the user. @RA@ e-mail MUST be PROVIDED in a form of `<alphanum|.>@<alphanum>.<alphanum>`."
   },
   {
    "name": "user_search_specs_make",
    "type": "text",
    "description": "Get the name of the manufacturer.\n@RA@ Most common case is when user define <manufacturer> <model>. Try to infer model if possible. If not sure don't do it. Examples:\n- USER: Yamaha R1. user_search_specs_make=Yamaha, user_search_specs_model=R1\n- USER: Yamaha Einfield. Both are manufacturers - do not set any slots.\n- USER: Yamaha YFZ 450. user_search_specs_make=Yamaha, user_search_specs_model=YFZ 450\n"
   },
   {
    "name": "user_search_specs_model",
    "type": "text",
    "description": "Get the name of the model from the list provided to user."
   }
  ]
 },
 {
  "flow_id": "other_search",
  "description": "Call 'other_search' flow if:\n- @RA@ User is asking to recommend particular brands or something else.\n- User's intent looks like a search for moto accessories/equipment/other. Examples:\n  - I need top 3 navigation systems for ATVs\n  - Where I can tune my bike?\n  - What shocks are suitable for Aprilia Tuareg 660?\n  - Recommend me 3 driving schools in Madrid.\n  - What are the best motorcycle gloves for winter riding?\n  - Where can I find a motorcycle-friendly road trip planner?\n  - What are the top-rated motorcycle covers for winter?\n  - What are the best motorcycle safety vests?\n  - What are the best motorcycle mirrors for visibility?\n  - Where can I find motorcycle-specific insurance?\n  - What are the best motorcycle horn upgrades?\n  - Where can I find a motorcycle repair manual?\n  - What are the best motorcycle rain covers?\n  - What are the best motorcycle ramp options?\n  - Recommend some comfortable motorcycle seats.\n  - What are the best motorcycle tail light upgrades?\n  - Suggest some effective motorcycle anti-fog solutions.\n",
  "slots": [
   {
    "name": "user_name",
    "type": "text",
    "description": "Name of the user. @RA@ Capitalize name slot if needed."
   },
   {
    "name": "user_email",
    "type": "text",
    "description": "E-mail of the user. @RA@ e-mail MUST be PROVIDED in a form of `<alphanum|.>@<alphanum>.<alphanum>`."
   }
  ]
 },
 {
  "flow_id": "good_bye_user",
  "description": "Call flow `good_bye_user` if user intents to finish conversation. Examples:\n- Cheerio\n- Пока\n- Adios\n- Ciao\n- Keep in touch\n- I wish you well\n- I'm ready to go\n- Have a good one!\n- I'm off to another adventure!\n- Exit stage left!\n",
  "slots": []
 }
]
```

---

# Current State

You are currently not inside any flow.

---

## Conversation History

USER: tell me about yamaha r1

---

## Task
Create an action list with one action per line in response to the user's last message: """bye""".

Your action list:
'''

if __name__ == "__main__":
    messages = [
        {"role": "user", "content": test_prompt}
    ]

    response = query_runpod_model('vvpreo/rasa_2025', messages)
    print(response)
