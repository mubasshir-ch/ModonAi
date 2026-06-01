import discord
from pydantic import BaseModel, Field
from typing import Union
from ..utils import resolve_channel, resolve_member, resolve_role
from ..base import BaseTool

class DeleteMessageParams(BaseModel):
    channel_name_or_id: Union[str, int] = Field(..., description="The name or ID of the channel where the message is located.")
    message_id: int = Field(..., description="The Snowflake ID of the message to delete.")

class DeleteMessageTool(BaseTool):
    name = "delete_message"
    description = "Deletes a specific message from a channel."
    schema = DeleteMessageParams

    async def execute(self, params: DeleteMessageParams, guild: discord.Guild):
        channel = await resolve_channel(guild, params.channel_name_or_id)

        if not channel or not isinstance(channel, (discord.TextChannel, discord.Thread)):
            return {"error": f"Text channel or thread '{params.channel_name_or_id}' not found."}

        try:
            msg = await channel.fetch_message(params.message_id)
            await msg.delete()
            return {"status": "success", "message": f"Deleted message {params.message_id} in {channel.name}"}
        except discord.NotFound:
            return {"error": f"Message with ID {params.message_id} not found."}
        except discord.Forbidden:
            return {"error": "Bot does not have permission to delete messages in this channel."}
        except Exception as e:
            return {"error": str(e)}
