# RASA CHALLANGE 2025
My name is Vladimir and I prepared a chatbot called `AI MOTO EXPERT`.
My goal was to prepare a demo of informational AI assistant, that combines several techniques for smooth user experience.

# How to run in codespaces
- Codespaces should load with .venv activated. if not - run `source .venv/bin.activate`
- Next step is to run `uv pip install -r requirements.txt`
- `set -a; source .env; set +a` to source necessary environment variables.
- `rasa train`
- That's it. `rasa shell`, `rasa inspect`, `rasa inspect --voice` should be working as well.

## Basic information
I've developed several user flows:
- `faq`. Approached with a combination of vector search and LLM prompting, called RAG techinque.
- `other_search`. Internet search with Perplexity via openrouter, with context transfer of current conversation.
- `vehicles_search_by_make_and_model`. Local storage search for information about particular brand & model. User also may add some special request, that might be addressed with Perplexity
- `obtain_user_data`. This flow is called once user successfully passes through `faq`/`other_search`/`vehicles_search_by_make_and_model`.
  - Here `AI MOTO EXPERT` collects name, gender, age and e-mail of the user.
- `good_bye_user`. This is a closing flow, where `AI MOTO EXPERT` sais goodbye to user and send's him/her an email with the content of current conversation.
- It is possible to run assistant in voice mode also, but, user experience is much worse, due to the long response time and quite long answers.

## CORE CHALLENGES AND ACHIEVEMENTS
- 💪Fixed data problems in the XLSX file I obtained for this RASA challenge (database of motocyces/scooters/ATV 2022-2025 year of production). It was awfully composed, without any normalisation.
- 💪Applied custom RAG techinique to run FAQ flow. I faced several problems utilizing the approach recommended in documentation.
- 💪Added flexibility for brand+model search in local storage, by applying levenstain distance calculation, to let user make typos, because it is hard to remember right spelling for each brand&model.
- 💪Integrated with gmail, to be able to send conversation summary to user.
- 💪Tuned the prompt I've with custom CompactLLMCommandGenerator implementation to increase LLM's attention to details, by embedding special markers. 
- 💪Generated hundreds of test cases for the dialogue.

## HACKS and customizations applied
- 🦹🏻‍Implemented custom rasa starting point, so I am able to pass predefined user's phrases for quick testing and debugging. see `scripts/rrasa.py`
- 🦹🏻‍Implemented custom RAQ search, because I was not able to configure proper embedding model to be used with yaml configuration.
  - Generated several dozens QA pairs for FAQ flow.
  - Tagged and Pre vectorized all questions
  - Works fast and smooth ))
- 🦹🏻‍Implemented custom CompactLLMCommandGenerator, that (a)gives more information to debug output, (b)Generates slightly different prompt template.
- 🦹🏻Integrated with openrouter, as a main LLM entrypoint for different LLMS.


# FEATURES I WOULD LIKE TO SEE 🤗
- Add bot roles. Sometimes I would like to make user think that conversation with gentle and friendly bot was interrupted by other role. At some point I realised that I want to see two characters, but it was impossible.. Same name, same icon, same prompt.. In my case I have AI MOTO EXPERT (friendly and helpful) and AI ADMIN, that is not so friendly, and he has to collect user's data.
- Add multimodal interface, where I would be able to work with text AND voice at the same time.
- yield events from actions instead of returning list, It is important when implementing something time consuming. I want to notify user that he has to wait a bit, and therfore need to add special step for this.
- Please add openrouter as customizable LLM option, where I would be able to define additional headers.
- Don't understand overall workflow. What work when and why. Will be great to see/hear/watch overall pipeline, where all spagetti of policies is explained.
- Would like to stub particular actions when running e2e tests. STUB all or nothing approach is not workable, as some custom actions are crucial for overall logic.
- Progress for e2e tests is what is REALLY needed. At some point, I generated hundreds of e2e tests and had no idea how much testing will take..
- Atomatic e2e test generator will be a REAL killer feature.
- It would be also great to find a workaround for test cases, when user gives enough information to fill several slots at once, but test_case is built to go one by one.. It fails here, but it is not a problem in real life.
  - Even worse, this is a big limitation for preparing proper dataset for local model, because theese conversations would not be passed due to e2e test failures..
- Would be happy to use logical expressions for `ask_before_filling`. Example: `ask_before_filling: slot.user_name is not null`
- Would like to see more options for slot modifications. Incremeting for example:
  ```yml
  - id: some_step
    set_slots: [ some_slot: slots.some_slot + 1 ]
  ```
