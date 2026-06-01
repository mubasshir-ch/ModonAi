import discord
from pydantic import BaseModel
from ..utils import resolve_channel, resolve_member, resolve_role
from ..base import BaseTool

class ListRolesParams(BaseModel):
    """Parameters for listing roles. No parameters required."""
    pass

class ListRolesTool(BaseTool):
    name = "list_roles"
    description = "Lists all roles in the server, including their names and IDs."
    schema = ListRolesParams
    read_only = True

    async def execute(self, params: ListRolesParams, guild: discord.Guild):
        roles = []
        for role in guild.roles:
            roles.append({
                "name": role.name,
                "id": role.id,
                "position": role.position,
                "color": str(role.color),
                "mentionable": role.mentionable
            })
        return roles
