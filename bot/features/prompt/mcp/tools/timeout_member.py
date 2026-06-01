import discord
from pydantic import BaseModel, Field
from typing import Union, Optional
from datetime import timedelta
from ..base import BaseTool
from ..utils import resolve_member

class TimeoutMemberParams(BaseModel):
    member_name_or_id: Union[str, int] = Field(..., description="The name or ID of the member to timeout.")
    duration_minutes: int = Field(..., ge=1, le=40320, description="Duration of the timeout in minutes (up to 28 days).")
    reason: Optional[str] = Field(None, description="The reason for the timeout.")

class TimeoutMemberTool(BaseTool):
    name = "timeout_member"
    description = "Temporarily times out a member, preventing them from speaking or reacting."
    schema = TimeoutMemberParams

    async def execute(self, params: TimeoutMemberParams, guild: discord.Guild):
        member = await resolve_member(guild, params.member_name_or_id)
        if not member:
            return {"error": f"Member '{params.member_name_or_id}' not found."}

        try:
            duration = timedelta(minutes=params.duration_minutes)
            await member.timeout(until=discord.utils.utcnow() + duration, reason=params.reason)
            return {"status": "success", "message": f"Timed out member {member.name} for {params.duration_minutes} minutes."}
        except discord.Forbidden:
            return {"error": "Bot does not have permission to timeout this member."}
        except Exception as e:
            return {"error": str(e)}
