import discord
from pydantic import BaseModel, Field
from ..base import BaseTool

class GetMemberInfoParams(BaseModel):
    member_id: int = Field(..., description="The Snowflake ID of the member.")

class GetMemberInfoTool(BaseTool):
    name = "get_member_info"
    description = "Retrieves detailed information about a specific server member by their ID."
    schema = GetMemberInfoParams
    read_only = True

    async def execute(self, params: GetMemberInfoParams, guild: discord.Guild):
        member = guild.get_member(params.member_id)
        if not member:
            # Try to fetch if not in cache (requires privileged intents)
            try:
                member = await guild.fetch_member(params.member_id)
            except discord.NotFound:
                return {"error": f"Member with ID {params.member_id} not found in this server."}

        return {
            "name": member.name,
            "display_name": member.display_name,
            "id": member.id,
            "bot": member.bot,
            "joined_at": str(member.joined_at),
            "created_at": str(member.created_at),
            "roles": [role.name for role in member.roles if role.name != "@everyone"],
            "top_role": member.top_role.name,
            "permissions": [p[0] for p in member.guild_permissions if p[1]],
            "status": str(member.status)
        }
