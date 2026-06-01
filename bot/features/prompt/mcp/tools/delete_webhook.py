import discord
from pydantic import BaseModel, Field
from typing import Union
from ..base import BaseTool

class DeleteWebhookParams(BaseModel):
    webhook_id: int = Field(..., description="The Snowflake ID of the webhook to delete.")

class DeleteWebhookTool(BaseTool):
    name = "delete_webhook"
    description = "Deletes an existing webhook by its ID."
    schema = DeleteWebhookParams

    async def execute(self, params: DeleteWebhookParams, guild: discord.Guild):
        try:
            # Note: guild.webhooks() requires Manage Webhooks permission
            webhooks = await guild.webhooks()
            webhook = discord.utils.get(webhooks, id=params.webhook_id)
            if not webhook:
                return {"error": f"Webhook with ID {params.webhook_id} not found."}
            
            await webhook.delete()
            return {"status": "success", "message": f"Deleted webhook {params.webhook_id}"}
        except discord.Forbidden:
            return {"error": "Bot does not have permission to manage webhooks."}
        except Exception as e:
            return {"error": str(e)}
