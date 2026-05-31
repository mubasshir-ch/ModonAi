import discord
from pydantic import BaseModel
from ..base import BaseTool

class GetServerInfoParams(BaseModel):
    """Parameters for getting server info. No parameters required."""
    pass

class GetServerInfoTool(BaseTool):
    name = "get_server_info"
    description = "Returns detailed metadata about the server, such as member count, owner, and features."
    schema = GetServerInfoParams
    read_only = True

    async def execute(self, params: GetServerInfoParams, guild: discord.Guild):
        info = {
            "name": guild.name,
            "id": guild.id,
            "owner": str(guild.owner),
            "member_count": guild.member_count,
            "created_at": str(guild.created_at),
            "description": guild.description,
            "mfa_level": guild.mfa_level,
            "verification_level": str(guild.verification_level),
            "features": guild.features,
            "premium_tier": guild.premium_tier,
            "premium_subscription_count": guild.premium_subscription_count
        }
        return info
