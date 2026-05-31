import discord
from typing import List
from pydantic import BaseModel, Field
from ..base import BaseTool
from ...models.shared import PermissionOverwrite
from ..utils import process_overwrites

class CreateCategoryParams(BaseModel):
    name: str
    overwrites: List[PermissionOverwrite] = Field(default_factory=list)

class CreateCategoryTool(BaseTool):
    name = "create_category"
    description = "Creates a new category in the server."
    schema = CreateCategoryParams

    async def execute(self, params: CreateCategoryParams, guild: discord.Guild):
        overwrites = await process_overwrites(guild, params.overwrites)
        await guild.create_category(name=params.name, overwrites=overwrites)
