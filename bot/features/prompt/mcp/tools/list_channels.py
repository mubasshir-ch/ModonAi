import discord
from pydantic import BaseModel
from ..utils import resolve_channel, resolve_member, resolve_role
from ..base import BaseTool

class ListChannelsParams(BaseModel):
    """Parameters for listing channels. No parameters required."""
    pass

class ListChannelsTool(BaseTool):
    name = "list_channels"
    description = "Lists all channels in the server, including categories, text, and voice channels."
    schema = ListChannelsParams
    read_only = True

    async def execute(self, params: ListChannelsParams, guild: discord.Guild):
        channels = []
        for channel in guild.channels:
            channel_info = {
                "name": channel.name,
                "id": channel.id,
                "type": str(channel.type),
                "position": channel.position,
            }
            if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.StageChannel)):
                channel_info["category"] = channel.category.name if channel.category else None
            
            channels.append(channel_info)
        return channels
