import discord
from pydantic import BaseModel, Field
from typing import Union, Optional
from ..utils import resolve_channel, resolve_member, resolve_role
from ..base import BaseTool

class EditMessageParams(BaseModel):
    channel_name_or_id: Union[str, int] = Field(..., description="The name or ID of the channel.")
    message_id: int = Field(..., description="The Snowflake ID of the message to edit.")
    new_content: str = Field(..., description="The new text content for the message.")

class EditMessageTool(BaseTool):
    name = "edit_message"
    description = "Edits a message previously sent by the bot."
    schema = EditMessageParams

    async def execute(self, params: EditMessageParams, guild: discord.Guild):
        channel = await resolve_channel(guild, params.channel_name_or_id)

        if not channel or not isinstance(channel, (discord.TextChannel, discord.Thread)):
            return {"error": f"Text channel or thread '{params.channel_name_or_id}' not found."}

        try:
            msg = await channel.fetch_message(params.message_id)
            if msg.author.id != guild.me.id:
                return {"error": "Bot can only edit its own messages."}
            
            await msg.edit(content=params.new_content)
            return {"status": "success", "message_id": msg.id}
        except discord.NotFound:
            return {"error": f"Message with ID {params.message_id} not found."}
        except discord.Forbidden:
            return {"error": "Bot does not have permission to edit this message."}
        except Exception as e:
            return {"error": str(e)}
