import discord
from pydantic import BaseModel, Field
from ..utils import resolve_channel, resolve_member, resolve_role
from ..base import BaseTool

class GetChannelInfoParams(BaseModel):
    channel_id: int = Field(..., description="The Snowflake ID of the channel.")

class GetChannelInfoTool(BaseTool):
    name = "get_channel_info"
    description = "Retrieves detailed information about a specific channel by its ID."
    schema = GetChannelInfoParams
    read_only = True

    async def execute(self, params: GetChannelInfoParams, guild: discord.Guild):
        channel = await resolve_channel(guild, params.channel_id)
        if not channel:
            return {"error": f"Channel with ID {params.channel_id} not found in this server."}

        info = {
            "name": channel.name,
            "id": channel.id,
            "type": str(channel.type),
            "position": channel.position,
            "created_at": str(channel.created_at)
        }

        if isinstance(channel, discord.TextChannel):
            info.update({
                "topic": channel.topic,
                "nsfw": channel.nsfw,
                "category": channel.category.name if channel.category else None,
                "slowmode_delay": channel.slowmode_delay
            })
        elif isinstance(channel, discord.VoiceChannel):
            info.update({
                "bitrate": channel.bit_rate,
                "user_limit": channel.user_limit,
                "category": channel.category.name if channel.category else None
            })

        return info
