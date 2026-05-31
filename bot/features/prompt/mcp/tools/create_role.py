import discord
from typing import Optional, List
from pydantic import BaseModel, Field
from ..base import BaseTool

class CreateRoleParams(BaseModel):
    name: str
    color: Optional[str] = Field(None, description="Hex color code, e.g., '#FF0000'")
    permissions: List[str] = Field(default_factory=list, description="List of permission names")
    mentionable: bool = False
    hoist: bool = False

class CreateRoleTool(BaseTool):
    name = "create_role"
    description = "Creates a new role in the server."
    schema = CreateRoleParams

    async def execute(self, params: CreateRoleParams, guild: discord.Guild):
        color = discord.Color(int(params.color.lstrip("#"), 16)) if params.color else discord.Color.default()
        await guild.create_role(
            name=params.name,
            color=color,
            mentionable=params.mentionable,
            hoist=params.hoist
        )
