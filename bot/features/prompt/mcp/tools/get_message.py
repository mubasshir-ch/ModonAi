import discord
from pydantic import BaseModel, Field
from typing import Union
from ..utils import resolve_channel, resolve_member, resolve_role
from ..base import BaseTool

class GetMessageParams(BaseModel):
    channel_id: int = Field(..., description="The Snowflake ID of the channel.")
    message_id: int = Field(..., description="The Snowflake ID of the message.")

class GetMessageTool(BaseTool):
    name = "get_message"
    description = "Retrieves a specific message by its ID and channel ID."
    schema = GetMessageParams
    read_only = True

    async def execute(self, params: GetMessageParams, guild: discord.Guild):
        channel = await resolve_channel(guild, params.channel_id)
        if not channel or not isinstance(channel, discord.TextChannel):
            return {"error": f"Text channel with ID {params.channel_id} not found."}

        try:
            msg = await channel.fetch_message(params.message_id)
            return {
                "author": msg.author.name,
                "content": msg.content,
                "timestamp": str(msg.created_at),
                "id": msg.id,
                "attachments": [a.url for a in msg.attachments],
                "embeds_count": len(msg.embeds)
            }
        except discord.NotFound:
            return {"error": f"Message with ID {params.message_id} not found."}
        except discord.Forbidden:
            return {"error": "Bot does not have permission to read message history in this channel."}
