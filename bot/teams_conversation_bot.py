# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import List
from botbuilder.core import TurnContext
from botbuilder.core.teams import TeamsActivityHandler
from botbuilder.schema import Activity, ActivityTypes
from botbuilder.schema.teams import TeamInfo, TeamsChannelAccount

from bot.gpt import ask_async

ADAPTIVECARDTEMPLATE = "resources/UserMentionCardTemplate.json"

class TeamsConversationBot(TeamsActivityHandler):
    def __init__(self, app_id: str, app_password: str):
        self._app_id = app_id
        self._app_password = app_password

    async def on_teams_members_added(  # pylint: disable=unused-argument
        self,
        teams_members_added: List[TeamsChannelAccount],
        team_info: TeamInfo,
        turn_context: TurnContext,
    ):
        for member in teams_members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    "Hi, I'm the Azure Spring Apps Wiki Bot powered by ChatGPT. I can answer any questions based on the internal Wiki. \nWhat can I help you with today?"
                )

    async def on_message_activity(self, turn_context: TurnContext):
        await self._send_typeing_activity(turn_context)
        TurnContext.remove_recipient_mention(turn_context.activity)
        text = turn_context.activity.text.strip().lower()
        answer = await ask_async(text)
        reply_activity = turn_context.activity.create_reply(answer)
        await turn_context.send_activity(reply_activity)
        return

    async def _send_typeing_activity(self, context: TurnContext):
        typing_activity = Activity(
            type=ActivityTypes.typing,
            relates_to=context.activity.relates_to,
        )

        conversation_reference = TurnContext.get_conversation_reference(
            context.activity
        )

        typing_activity = TurnContext.apply_conversation_reference(
            typing_activity, conversation_reference
        )

        await context.adapter.send_activities(context, [typing_activity])
