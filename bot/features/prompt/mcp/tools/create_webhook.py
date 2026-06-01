import discord
from pydantic import BaseModel, Field
from typing import Union, Optional
from ..base import BaseTool
from ..utils import resolve_channel

class CreateWebhookParams(BaseModel):
    channel_name_or_id: Union[str, int] = Field(..., description="The name or ID of the channel.")
    name: str = Field(..., description="The name of the new webhook.")

class CreateWebhookTool(BaseTool):
    name = "create_webhook"
    description = "Creates a new webhook for a specific channel."
    schema = CreateWebhookParams

    async def execute(self, params: CreateWebhookParams, guild: discord.Guild):
        channel = await resolve_channel(guild, params.channel_name_or_id)
        if not channel or not isinstance(channel, discord.TextChannel):
            return {"error": f"Text channel '{params.channel_name_or_id}' not found."}

        try:
            webhook = await channel.create_webhook(name=params.name)
            return {"status": "success", "url": webhook.url, "id": webhook.id}
        except discord.Forbidden:
            return {"error": "Bot does not have permission to create webhooks in this channel."}
        except Exception as e:
            return {"error": str(e)}
