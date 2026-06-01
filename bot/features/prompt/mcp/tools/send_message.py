import discord
from pydantic import BaseModel, Field
from typing import Union, Optional
from ..utils import resolve_channel, resolve_member, resolve_role
from ..base import BaseTool

class SendMessageParams(BaseModel):
    channel_name_or_id: Union[str, int] = Field(..., description="The name or ID of the channel to send the message to.")
    content: str = Field(..., description="The text content of the message.")
    tts: bool = Field(default=False, description="Whether the message should be sent using Text-To-Speech.")

class SendMessageTool(BaseTool):
    name = "send_message"
    description = "Sends a plain text message to a specific channel."
    schema = SendMessageParams

    async def execute(self, params: SendMessageParams, guild: discord.Guild):
        channel = await resolve_channel(guild, params.channel_name_or_id)

        if not channel or not isinstance(channel, discord.TextChannel):
            return {"error": f"Text channel '{params.channel_name_or_id}' not found."}

        try:
            message = await channel.send(content=params.content, tts=params.tts)
            return {"status": "success", "message_id": message.id}
        except discord.Forbidden:
            return {"error": "Bot does not have permission to send messages in this channel."}
        except Exception as e:
            return {"error": str(e)}
