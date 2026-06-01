import discord
from pydantic import BaseModel
from typing import Union
from ..utils import resolve_channel, resolve_member, resolve_role
from ..base import BaseTool

class AssignRoleParams(BaseModel):
    member_name_or_id: Union[str, int]
    role_name_or_id: Union[str, int]

class AssignRoleTool(BaseTool):
    name = "assign_role"
    description = "Assigns a specific role to a member."
    schema = AssignRoleParams

    async def execute(self, params: AssignRoleParams, guild: discord.Guild):
        member_target = params.member_name_or_id
        role_target = params.role_name_or_id
        
        member = await resolve_member(guild, member_target)
        role = await resolve_role(guild, role_target)
        
        if member and role:
            await member.add_roles(role)
