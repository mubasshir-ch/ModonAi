import discord
from pydantic import BaseModel, Field
from typing import Union, Optional
from ..base import BaseTool
from ..utils import resolve_channel

class MoveChannelParams(BaseModel):
    channel_name_or_id: Union[str, int] = Field(..., description="The name or ID of the channel to move.")
    category_name_or_id: Optional[Union[str, int]] = Field(None, description="The name or ID of the category to move the channel into.")
    position: Optional[int] = Field(None, description="The new position of the channel in the list.")

class MoveChannelTool(BaseTool):
    name = "move_channel"
    description = "Moves a channel to a different category or changes its position in the sidebar."
    schema = MoveChannelParams

    async def execute(self, params: MoveChannelParams, guild: discord.Guild):
        channel = await resolve_channel(guild, params.channel_name_or_id)
        if not channel:
            return {"error": f"Channel '{params.channel_name_or_id}' not found."}

        kwargs = {}
        if params.category_name_or_id:
            category = await resolve_channel(guild, params.category_name_or_id)
            if category and isinstance(category, discord.CategoryChannel):
                kwargs["category"] = category
            else:
                return {"error": f"Category '{params.category_name_or_id}' not found or is not a category."}
        
        if params.position is not None:
            kwargs["position"] = params.position

        try:
            await channel.edit(**kwargs)
            return {"status": "success", "message": f"Moved channel {channel.name}"}
        except discord.Forbidden:
            return {"error": "Bot does not have permission to move this channel."}
        except Exception as e:
            return {"error": str(e)}
