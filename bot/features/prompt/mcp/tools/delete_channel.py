import discord
from typing import Union
from pydantic import BaseModel
from ..base import BaseTool

class DeleteParams(BaseModel):
    name_or_id: Union[str, int]

class DeleteChannelTool(BaseTool):
    name = "delete_channel"
    description = "Deletes a specific channel from the server."
    schema = DeleteParams

    async def execute(self, params: DeleteParams, guild: discord.Guild):
        target = params.name_or_id
        channel = discord.utils.get(guild.channels, name=target) if isinstance(target, str) else guild.get_channel(target)
        if channel:
            await channel.delete()
