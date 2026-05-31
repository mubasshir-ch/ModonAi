from pydantic import BaseModel
from typing import Type, Any
import discord

class BaseTool:
    name: str
    description: str
    schema: Type[BaseModel]

    async def execute(self, params: BaseModel, guild: discord.Guild) -> Any:
        raise NotImplementedError
