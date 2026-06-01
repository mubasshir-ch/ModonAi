import discord
from pydantic import BaseModel, Field
from typing import Union, Optional
from ..base import BaseTool
from ..utils import resolve_member

class KickMemberParams(BaseModel):
    member_name_or_id: Union[str, int] = Field(..., description="The name or ID of the member to kick.")
    reason: Optional[str] = Field(None, description="The reason for kicking the member.")

class KickMemberTool(BaseTool):
    name = "kick_member"
    description = "Kicks a member from the server."
    schema = KickMemberParams

    async def execute(self, params: KickMemberParams, guild: discord.Guild):
        member = await resolve_member(guild, params.member_name_or_id)
        if not member:
            return {"error": f"Member '{params.member_name_or_id}' not found."}

        try:
            await member.kick(reason=params.reason)
            return {"status": "success", "message": f"Kicked member {member.name}"}
        except discord.Forbidden:
            return {"error": "Bot does not have permission to kick this member."}
        except Exception as e:
            return {"error": str(e)}
