import discord
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from ..base import BaseTool
from ...models.shared import PermissionOverwrite
from ..utils import process_overwrites, resolve_channel, resolve_member, resolve_role

class CreateChannelParams(BaseModel):
    name: str
    channel_type: Literal["text", "voice", "stage", "forum"] = "text"
    category_name: Optional[str] = None
    topic: Optional[str] = None
    overwrites: List[PermissionOverwrite] = Field(default_factory=list)
    nsfw: bool = False
    thread_replies: bool = False

class CreateChannelTool(BaseTool):
    name = "create_channel"
    description = "Creates a new text or voice channel in the server."
    schema = CreateChannelParams

    async def execute(self, params: CreateChannelParams, guild: discord.Guild):
        overwrites = await process_overwrites(guild, params.overwrites)
        category = discord.utils.get(guild.categories, name=params.category_name) if params.category_name else None
        
        if params.channel_type == "text":
            await guild.create_text_channel(
                name=params.name,
                category=category,
                topic=params.topic,
                overwrites=overwrites,
                nsfw=params.nsfw
            )
        elif params.channel_type == "voice":
            await guild.create_voice_channel(
                name=params.name,
                category=category,
                overwrites=overwrites
            )
