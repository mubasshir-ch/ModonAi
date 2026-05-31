import discord
from pydantic import BaseModel, Field
from ..base import BaseTool

class GetRoleInfoParams(BaseModel):
    role_id: int = Field(..., description="The Snowflake ID of the role.")

class GetRoleInfoTool(BaseTool):
    name = "get_role_info"
    description = "Retrieves detailed information about a specific role by its ID."
    schema = GetRoleInfoParams
    read_only = True

    async def execute(self, params: GetRoleInfoParams, guild: discord.Guild):
        role = guild.get_role(params.role_id)
        if not role:
            return {"error": f"Role with ID {params.role_id} not found in this server."}

        return {
            "name": role.name,
            "id": role.id,
            "color": str(role.color),
            "position": role.position,
            "hoist": role.hoist,
            "mentionable": role.mentionable,
            "permissions": [p[0] for p in role.permissions if p[1]],
            "member_count": len(role.members)
        }
