import discord
from pydantic import BaseModel, Field
from typing import Union
from ..base import BaseTool

class ReadMessagesParams(BaseModel):
    channel_name_or_id: Union[str, int] = Field(..., description="The name or ID of the channel to read messages from.")
    limit: int = Field(default=10, description="Number of messages to fetch (max 100).")

class ReadMessagesTool(BaseTool):
    name = "read_messages"
    description = "Fetches recent messages from a specific channel."
    schema = ReadMessagesParams
    read_only = True

    async def execute(self, params: ReadMessagesParams, guild: discord.Guild):
        channel = None
        if isinstance(params.channel_name_or_id, int):
            channel = guild.get_channel(params.channel_name_or_id)
        else:
            channel = discord.utils.get(guild.text_channels, name=params.channel_name_or_id)
        
        if not channel or not isinstance(channel, discord.TextChannel):
            return {"error": f"Text channel '{params.channel_name_or_id}' not found."}

        messages = []
        async for msg in channel.history(limit=params.limit):
            messages.append({
                "author": msg.author.name,
                "content": msg.content,
                "timestamp": str(msg.created_at),
                "id": msg.id
            })
        
        return messages
