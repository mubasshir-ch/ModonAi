import discord
from pydantic import BaseModel, Field
from typing import Union
from ..utils import resolve_channel, resolve_member, resolve_role
from ..base import BaseTool

class ListPinnedMessagesParams(BaseModel):
    channel_name_or_id: Union[str, int] = Field(..., description="The name or ID of the channel.")

class ListPinnedMessagesTool(BaseTool):
    name = "list_pinned_messages"
    description = "Lists all pinned messages in a specific channel."
    schema = ListPinnedMessagesParams
    read_only = True

    async def execute(self, params: ListPinnedMessagesParams, guild: discord.Guild):
        channel = await resolve_channel(guild, params.channel_name_or_id)
        
        if not channel or not isinstance(channel, discord.TextChannel):
            return {"error": f"Text channel '{params.channel_name_or_id}' not found."}

        try:
            pins = await channel.pins()
            messages = []
            for msg in pins:
                messages.append({
                    "author": msg.author.name,
                    "content": msg.content,
                    "timestamp": str(msg.created_at),
                    "id": msg.id
                })
            return messages
        except discord.Forbidden:
            return {"error": "Bot does not have permission to view pins in this channel."}
