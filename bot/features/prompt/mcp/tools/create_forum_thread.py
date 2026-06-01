import discord
from pydantic import BaseModel, Field
from typing import Union, Optional
from ..base import BaseTool
from ..utils import resolve_channel

class CreateForumThreadParams(BaseModel):
    channel_name_or_id: Union[str, int] = Field(..., description="The name or ID of the forum channel.")
    name: str = Field(..., description="The name of the new thread.")
    content: str = Field(..., description="The initial message content for the thread.")

class CreateForumThreadTool(BaseTool):
    name = "create_forum_thread"
    description = "Creates a new thread in a forum channel with an initial message."
    schema = CreateForumThreadParams

    async def execute(self, params: CreateForumThreadParams, guild: discord.Guild):
        channel = await resolve_channel(guild, params.channel_name_or_id)
        if not channel or not isinstance(channel, discord.ForumChannel):
            return {"error": f"Forum channel '{params.channel_name_or_id}' not found."}

        try:
            thread_data = await channel.create_thread(name=params.name, content=params.content)
            return {"status": "success", "thread_id": thread_data.thread.id}
        except discord.Forbidden:
            return {"error": "Bot does not have permission to create threads in this forum."}
        except Exception as e:
            return {"error": str(e)}
