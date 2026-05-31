import discord
from pydantic import BaseModel, Field
from typing import Union
from ..base import BaseTool

class SendDMParams(BaseModel):
    member_name_or_id: Union[str, int] = Field(..., description="The name or ID of the member to DM.")
    content: str = Field(..., description="The text content of the DM.")

class SendDMTool(BaseTool):
    name = "send_dm"
    description = "Sends a private direct message to a specific server member."
    schema = SendDMParams

    async def execute(self, params: SendDMParams, guild: discord.Guild):
        member = None
        if isinstance(params.member_name_or_id, int):
            member = guild.get_member(params.member_name_or_id) or await guild.fetch_member(params.member_name_or_id)
        else:
            member = discord.utils.get(guild.members, name=params.member_name_or_id)

        if not member:
            return {"error": f"Member '{params.member_name_or_id}' not found."}

        try:
            channel = await member.create_dm()
            await channel.send(content=params.content)
            return {"status": "success"}
        except discord.Forbidden:
            return {"error": "Cannot send DMs to this user (they may have DMs closed or blocked the bot)."}
        except Exception as e:
            return {"error": str(e)}
