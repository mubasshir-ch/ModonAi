import discord
from typing import Union
from pydantic import BaseModel
from ..utils import resolve_channel, resolve_member, resolve_role
from ..base import BaseTool

class DeleteParams(BaseModel):
    name_or_id: Union[str, int]

class DeleteChannelTool(BaseTool):
    name = "delete_channel"
    description = "Deletes a specific channel from the server."
    schema = DeleteParams

    async def execute(self, params: DeleteParams, guild: discord.Guild):
        channel = await resolve_channel(guild, params.name_or_id)
        if channel:
            await channel.delete()
