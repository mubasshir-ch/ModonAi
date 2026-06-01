import discord
from pydantic import BaseModel
from ..utils import resolve_channel, resolve_member, resolve_role
from ..base import BaseTool

class ListEmojisParams(BaseModel):
    """No parameters required."""
    pass

class ListEmojisTool(BaseTool):
    name = "list_emojis"
    description = "Lists all custom emojis available in the server."
    schema = ListEmojisParams
    read_only = True

    async def execute(self, params: ListEmojisParams, guild: discord.Guild):
        emojis = []
        for emoji in guild.emojis:
            emojis.append({
                "name": emoji.name,
                "id": emoji.id,
                "animated": emoji.animated,
                "available": emoji.available,
                "require_colons": emoji.require_colons
            })
        return emojis
