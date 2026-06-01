import discord
from pydantic import BaseModel, Field
from typing import Optional, Literal
from ..base import BaseTool

class UpdateServerSettingsParams(BaseModel):
    name: Optional[str] = Field(None, description="New name for the server.")
    verification_level: Optional[Literal["none", "low", "medium", "high", "extreme"]] = Field(None, description="New verification level.")
    default_notifications: Optional[Literal["all_messages", "only_mentions"]] = Field(None, description="New default notification level.")
    explicit_content_filter: Optional[Literal["disabled", "members_without_roles", "all_members"]] = Field(None, description="New explicit content filter level.")

class UpdateServerSettingsTool(BaseTool):
    name = "update_server_settings"
    description = "Modifies core server settings like name and security levels."
    schema = UpdateServerSettingsParams

    async def execute(self, params: UpdateServerSettingsParams, guild: discord.Guild):
        kwargs = {}
        if params.name: kwargs["name"] = params.name
        
        if params.verification_level:
            kwargs["verification_level"] = getattr(discord.VerificationLevel, params.verification_level)
        
        if params.default_notifications:
            kwargs["default_notifications"] = getattr(discord.NotificationLevel, params.default_notifications)
            
        if params.explicit_content_filter:
            kwargs["explicit_content_filter"] = getattr(discord.ContentFilter, params.explicit_content_filter)

        try:
            await guild.edit(**kwargs)
            return {"status": "success", "message": f"Updated server settings for {guild.name}"}
        except discord.Forbidden:
            return {"error": "Bot does not have permission to manage server settings."}
        except Exception as e:
            return {"error": str(e)}
