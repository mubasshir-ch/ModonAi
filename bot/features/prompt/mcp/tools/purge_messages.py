import discord
from pydantic import BaseModel, Field
from typing import Union, Optional
from ..utils import resolve_channel, resolve_member, resolve_role
from ..base import BaseTool

class PurgeMessagesParams(BaseModel):
    channel_name_or_id: Union[str, int] = Field(..., description="The name or ID of the channel to purge messages from.")
    limit: int = Field(default=10, description="The number of messages to search through and potentially delete (max 100).")
    author_name_or_id: Optional[Union[str, int]] = Field(None, description="Only delete messages from this specific user.")
    contains: Optional[str] = Field(None, description="Only delete messages containing this keyword.")

class PurgeMessagesTool(BaseTool):
    name = "purge_messages"
    description = "Bulk deletes messages in a channel, optionally filtered by author or content."
    schema = PurgeMessagesParams

    async def execute(self, params: PurgeMessagesParams, guild: discord.Guild):
        channel = await resolve_channel(guild, params.channel_name_or_id)

        if not channel or not isinstance(channel, (discord.TextChannel, discord.Thread)):
            return {"error": f"Text channel or thread '{params.channel_name_or_id}' not found."}

        if params.limit > 100:
            params.limit = 100

        def check(m):
            matches = True
            if params.author_name_or_id:
                author_matches = str(m.author.id) == str(params.author_name_or_id) or m.author.name == params.author_name_or_id
                matches = matches and author_matches
            if params.contains:
                matches = matches and (params.contains.lower() in m.content.lower())
            return matches

        try:
            deleted = await channel.purge(limit=params.limit, check=check)
            return {"status": "success", "deleted_count": len(deleted)}
        except discord.Forbidden:
            return {"error": "Bot does not have permission to manage messages in this channel."}
        except Exception as e:
            return {"error": str(e)}
