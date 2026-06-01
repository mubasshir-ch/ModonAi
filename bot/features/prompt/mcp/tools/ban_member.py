import discord
from pydantic import BaseModel, Field
from typing import Union, Optional
from ..base import BaseTool
from ..utils import resolve_member

class BanMemberParams(BaseModel):
    member_name_or_id: Union[str, int] = Field(..., description="The name or ID of the member to ban.")
    reason: Optional[str] = Field(None, description="The reason for banning the member.")
    delete_message_days: int = Field(default=0, ge=0, le=7, description="Number of days of messages to delete (0-7).")

class BanMemberTool(BaseTool):
    name = "ban_member"
    description = "Permanently bans a member from the server."
    schema = BanMemberParams

    async def execute(self, params: BanMemberParams, guild: discord.Guild):
        member = await resolve_member(guild, params.member_name_or_id)
        if not member:
            return {"error": f"Member '{params.member_name_or_id}' not found."}

        try:
            await member.ban(reason=params.reason, delete_message_days=params.delete_message_days)
            return {"status": "success", "message": f"Banned member {member.name}"}
        except discord.Forbidden:
            return {"error": "Bot does not have permission to ban this member."}
        except Exception as e:
            return {"error": str(e)}
