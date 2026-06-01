import discord
from pydantic import BaseModel
from ..utils import resolve_channel, resolve_member, resolve_role
from ..base import BaseTool

class ListGuildsParams(BaseModel):
    """No parameters required."""
    pass

class ListGuildsTool(BaseTool):
    name = "list_guilds"
    description = "Lists all servers (guilds) the bot is currently a member of."
    schema = ListGuildsParams
    read_only = True

    async def execute(self, params: ListGuildsParams, guild: discord.Guild):
        # We use the bot client to get all guilds
        bot = guild.me._state.parent
        guilds = []
        for g in bot.guilds:
            guilds.append({
                "name": g.name,
                "id": g.id,
                "member_count": g.member_count
            })
        return guilds
