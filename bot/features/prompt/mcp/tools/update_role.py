import discord
from pydantic import BaseModel, Field
from typing import Union, Optional, List
from ..base import BaseTool
from ..utils import resolve_role

class UpdateRoleParams(BaseModel):
    role_name_or_id: Union[str, int] = Field(..., description="The name or ID of the role to update.")
    name: Optional[str] = Field(None, description="New name for the role.")
    color: Optional[str] = Field(None, description="New hex color code, e.g., '#FF0000'.")
    hoist: Optional[bool] = Field(None, description="Whether the role should be displayed separately in the sidebar.")
    mentionable: Optional[bool] = Field(None, description="Whether the role should be mentionable.")
    permissions: Optional[List[str]] = Field(None, description="List of permission names to set for the role.")

class UpdateRoleTool(BaseTool):
    name = "update_role"
    description = "Updates an existing role's properties like name, color, and permissions."
    schema = UpdateRoleParams

    async def execute(self, params: UpdateRoleParams, guild: discord.Guild):
        role = await resolve_role(guild, params.role_name_or_id)
        if not role:
            return {"error": f"Role '{params.role_name_or_id}' not found."}

        kwargs = {}
        if params.name: kwargs["name"] = params.name
        if params.color: kwargs["color"] = discord.Color(int(params.color.lstrip("#"), 16))
        if params.hoist is not None: kwargs["hoist"] = params.hoist
        if params.mentionable is not None: kwargs["mentionable"] = params.mentionable
        
        if params.permissions:
            perms = discord.Permissions(**{p: True for p in params.permissions})
            kwargs["permissions"] = perms

        try:
            await role.edit(**kwargs)
            return {"status": "success", "message": f"Updated role {role.name}"}
        except discord.Forbidden:
            return {"error": "Bot does not have permission to manage this role."}
        except Exception as e:
            return {"error": str(e)}
