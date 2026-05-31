import discord
from typing import Union
from pydantic import BaseModel
from ..base import BaseTool

class DeleteParams(BaseModel):
    name_or_id: Union[str, int]

class DeleteRoleTool(BaseTool):
    name = "delete_role"
    description = "Deletes a specific role from the server."
    schema = DeleteParams

    async def execute(self, params: DeleteParams, guild: discord.Guild):
        target = params.name_or_id
        role = discord.utils.get(guild.roles, name=target) if isinstance(target, str) else guild.get_role(target)
        if role:
            await role.delete()
