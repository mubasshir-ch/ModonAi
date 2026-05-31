import discord
from pydantic import BaseModel
from typing import Union
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
        
        member = discord.utils.get(guild.members, name=member_target) if isinstance(member_target, str) else guild.get_member(member_target)
        role = discord.utils.get(guild.roles, name=role_target) if isinstance(role_target, str) else guild.get_role(role_target)
        
        if member and role:
            await member.add_roles(role)
