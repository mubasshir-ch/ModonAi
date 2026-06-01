import discord
from pydantic import BaseModel
from ..utils import resolve_channel, resolve_member, resolve_role
from ..base import BaseTool

class ListInvitesParams(BaseModel):
    """No parameters required."""
    pass

class ListInvitesTool(BaseTool):
    name = "list_invites"
    description = "Lists all active invites for the server."
    schema = ListInvitesParams
    read_only = True

    async def execute(self, params: ListInvitesParams, guild: discord.Guild):
        try:
            invites = await guild.invites()
        except discord.Forbidden:
            return {"error": "Bot does not have permission to view invites."}

        invite_list = []
        for invite in invites:
            invite_list.append({
                "code": invite.code,
                "inviter": str(invite.inviter),
                "channel": invite.channel.name,
                "uses": invite.uses,
                "max_uses": invite.max_uses,
                "created_at": str(invite.created_at),
                "expires_at": str(invite.expires_at) if invite.expires_at else None
            })
        return invite_list
