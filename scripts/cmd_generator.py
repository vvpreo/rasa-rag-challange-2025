import json
from pprint import pprint
from typing import List, Dict, Any, Optional

import structlog
import yaml
from rasa.dialogue_understanding.commands import Command
from rasa.dialogue_understanding.generator import CompactLLMCommandGenerator
from rasa.dialogue_understanding.stack.utils import top_flow_frame
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.shared.core.flows import FlowsList
from rasa.shared.core.trackers import DialogueStateTracker
from rasa.shared.nlu.constants import TEXT
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.utils.llm import (
    allowed_values_for_slot,
    sanitize_message_for_prompt,
    tracker_as_readable_transcript,
)

structlogger = structlog.get_logger()


def remove_none(obj):
    if isinstance(obj, dict):
        return {k: remove_none(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [remove_none(item) for item in obj]
    return obj


@DefaultV1Recipe.register(
    [
        DefaultV1Recipe.ComponentType.COMMAND_GENERATOR,
    ],
    is_trainable=True,
)
class CustomCommandGenerator(CompactLLMCommandGenerator):

    def render_template(
            self,
            message: Message,
            tracker: DialogueStateTracker,
            startable_flows: FlowsList,
            all_flows: FlowsList,
    ) -> str:
        """Render the jinja template to create the prompt for the LLM.

        Args:
            message: The current message from the user.
            tracker: The tracker containing the current state of the conversation.
            startable_flows: The flows startable at this point in time by the user.
            all_flows: all flows present in the assistant

        Returns:
            The rendered prompt template.
        """
        # need to make this distinction here because current step of the
        # top_calling_frame would be the call step, but we need the collect step from
        # the called frame. If no call is active calling and called frame are the same.
        top_calling_frame = top_flow_frame(tracker.stack)
        top_called_frame = top_flow_frame(tracker.stack, ignore_call_frames=False)

        top_flow = top_calling_frame.flow(all_flows) if top_calling_frame else None
        current_step = top_called_frame.step(all_flows) if top_called_frame else None

        flow_slots = self.prepare_current_flow_slots_for_template(
            top_flow, current_step, tracker
        )
        current_slot, current_slot_description = self.prepare_current_slot_for_template(
            current_step
        )
        current_slot_type = None
        current_slot_allowed_values = None
        if current_slot:
            current_slot_type = (
                slot.type_name
                if (slot := tracker.slots.get(current_slot)) is not None
                else None
            )
            current_slot_allowed_values = allowed_values_for_slot(
                tracker.slots.get(current_slot)
            )
        current_conversation = tracker_as_readable_transcript(tracker)
        latest_user_message = sanitize_message_for_prompt(message.get(TEXT))
        current_conversation += f"\nUSER: {latest_user_message}"

        flows_data = self.prepare_flows_for_template(startable_flows, tracker)
        flows_data = remove_none(flows_data)
        flows_data = json.dumps(flows_data, indent=1, ensure_ascii=False, allow_nan=False)

        inputs = {
            "available_flows": flows_data,
            "current_conversation": current_conversation,
            "flow_slots": flow_slots,
            "current_flow": top_flow.id if top_flow is not None else None,
            "current_slot": current_slot,
            "current_slot_description": current_slot_description,
            "current_slot_type": current_slot_type,
            "current_slot_allowed_values": current_slot_allowed_values,
            "user_message": latest_user_message,
            "is_repeat_command_enabled": self.repeat_command_enabled,
        }

        tmplt = self.compile_template(self.prompt_template).render(**inputs)
        print('***' * 30)
        print('\n\t' + '\n\t'.join(tmplt.splitlines()))
        print('***' * 30)

        return self.compile_template(self.prompt_template).render(**inputs)

    def prepare_flows_for_template(
            self, flows: FlowsList, tracker: DialogueStateTracker
    ) -> List[Dict[str, Any]]:
        # print('+++' * 30)
        result = []
        for flow in flows.user_flows:
            slots_info = list()
            for q in flow.get_collect_steps():
                if self.is_extractable(q, tracker):
                    # print(flow.id, q.flow_id, q.collect)
                    slots_info.append(
                        {
                            "name": q.collect,
                            "type": tracker.slots[q.collect].type_name,
                            "description": q.description,
                            "allowed_values": allowed_values_for_slot(tracker.slots[q.collect]),
                        }
                    )
            result.append(
                {
                    "flow_id": flow.id,
                    "description": flow.description,
                    "slots": slots_info,
                }
            )
        # print('+++' * 30)
        return result

    async def _predict_commands(self, message: Message, flows: FlowsList,
                                tracker: Optional[DialogueStateTracker] = None, ) -> List[Command]:
        cmds = await super()._predict_commands(message, flows, tracker)
        print('🤖:', cmds)
        return cmds
