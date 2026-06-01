import discord
from pydantic import BaseModel, Field
from typing import Union, Optional
from ..utils import resolve_channel, resolve_member, resolve_role
from ..base import BaseTool

class SearchMessagesParams(BaseModel):
    channel_name_or_id: Union[str, int] = Field(..., description="The name or ID of the channel to search in.")
    query: str = Field(..., description="The keyword or phrase to search for.")
    limit: int = Field(default=100, description="The number of recent messages to search through (max 500).")

class SearchMessagesTool(BaseTool):
    name = "search_messages"
    description = "Searches for a keyword in the recent history of a specific channel."
    schema = SearchMessagesParams
    read_only = True

    async def execute(self, params: SearchMessagesParams, guild: discord.Guild):
        channel = await resolve_channel(guild, params.channel_name_or_id)
        
        if not channel or not isinstance(channel, discord.TextChannel):
            return {"error": f"Text channel '{params.channel_name_or_id}' not found."}

        if params.limit > 500:
            params.limit = 500

        results = []
        try:
            async for msg in channel.history(limit=params.limit):
                if params.query.lower() in msg.content.lower():
                    results.append({
                        "author": msg.author.name,
                        "content": msg.content,
                        "timestamp": str(msg.created_at),
                        "id": msg.id
                    })
            return results
        except discord.Forbidden:
            return {"error": "Bot does not have permission to read message history in this channel."}
