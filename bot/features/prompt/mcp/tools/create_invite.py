import discord
from pydantic import BaseModel, Field
from typing import Union, Optional
from ..base import BaseTool
from ..utils import resolve_channel

class CreateInviteParams(BaseModel):
    channel_name_or_id: Union[str, int] = Field(..., description="The name or ID of the channel.")
    max_age: int = Field(default=86400, description="Duration in seconds until expiration (default 24h, 0 for never).")
    max_uses: int = Field(default=0, description="Maximum number of uses (0 for unlimited).")
    temporary: bool = Field(default=False, description="Whether the invite is temporary (members kicked when they leave).")
    unique: bool = Field(default=True, description="Whether a unique invite should be generated.")

class CreateInviteTool(BaseTool):
    name = "create_invite"
    description = "Generates a new invite link for a specific channel."
    schema = CreateInviteParams

    async def execute(self, params: CreateInviteParams, guild: discord.Guild):
        channel = await resolve_channel(guild, params.channel_name_or_id)
        if not channel or not isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
            return {"error": f"Inviteable channel '{params.channel_name_or_id}' not found."}

        try:
            invite = await channel.create_invite(
                max_age=params.max_age,
                max_uses=params.max_uses,
                temporary=params.temporary,
                unique=params.unique
            )
            return {"status": "success", "url": invite.url, "code": invite.code}
        except discord.Forbidden:
            return {"error": "Bot does not have permission to create invites in this channel."}
        except Exception as e:
            return {"error": str(e)}
