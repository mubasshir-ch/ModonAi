import discord
from pydantic import BaseModel, Field
from typing import Union, Optional, List
from ..base import BaseTool
from ..utils import resolve_channel, process_overwrites
from ...models.shared import PermissionOverwrite

class UpdateChannelParams(BaseModel):
    channel_name_or_id: Union[str, int] = Field(..., description="The name or ID of the channel to update.")
    name: Optional[str] = Field(None, description="New name for the channel.")
    topic: Optional[str] = Field(None, description="New topic for the channel.")
    nsfw: Optional[bool] = Field(None, description="Whether the channel should be NSFW.")
    overwrites: Optional[List[PermissionOverwrite]] = Field(None, description="New permission overwrites.")
    slowmode_delay: Optional[int] = Field(None, description="Slowmode delay in seconds (0-21600).")

class UpdateChannelTool(BaseTool):
    name = "update_channel"
    description = "Updates an existing channel's properties like name, topic, and permissions."
    schema = UpdateChannelParams

    async def execute(self, params: UpdateChannelParams, guild: discord.Guild):
        channel = await resolve_channel(guild, params.channel_name_or_id)
        if not channel:
            return {"error": f"Channel '{params.channel_name_or_id}' not found."}

        kwargs = {}
        if params.name: kwargs["name"] = params.name
        if params.topic is not None: kwargs["topic"] = params.topic
        if params.nsfw is not None: kwargs["nsfw"] = params.nsfw
        if params.slowmode_delay is not None: kwargs["slowmode_delay"] = params.slowmode_delay
        
        if params.overwrites:
            kwargs["overwrites"] = await process_overwrites(guild, params.overwrites)

        try:
            await channel.edit(**kwargs)
            return {"status": "success", "message": f"Updated channel {channel.name}"}
        except discord.Forbidden:
            return {"error": "Bot does not have permission to manage this channel."}
        except Exception as e:
            return {"error": str(e)}
