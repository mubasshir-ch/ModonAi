import discord
from pydantic import BaseModel, Field
from typing import Union, Optional
from ..base import BaseTool
from ..utils import resolve_member

class RemoveTimeoutParams(BaseModel):
    member_name_or_id: Union[str, int] = Field(..., description="The name or ID of the member.")
    reason: Optional[str] = Field(None, description="The reason for removing the timeout.")

class RemoveTimeoutTool(BaseTool):
    name = "remove_timeout"
    description = "Removes an active timeout from a member."
    schema = RemoveTimeoutParams

    async def execute(self, params: RemoveTimeoutParams, guild: discord.Guild):
        member = await resolve_member(guild, params.member_name_or_id)
        if not member:
            return {"error": f"Member '{params.member_name_or_id}' not found."}

        try:
            await member.remove_timeout(reason=params.reason)
            return {"status": "success", "message": f"Removed timeout from member {member.name}"}
        except discord.Forbidden:
            return {"error": "Bot does not have permission to remove timeout from this member."}
        except Exception as e:
            return {"error": str(e)}
