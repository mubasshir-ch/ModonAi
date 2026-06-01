import discord
from pydantic import BaseModel, Field
from typing import Optional, Union
from ..utils import resolve_channel, resolve_member, resolve_role
from ..base import BaseTool

class ListMembersParams(BaseModel):
    limit: int = Field(default=10, description="Number of members to return (max 100).")
    search_query: Optional[str] = Field(default=None, description="Optional string to search for in usernames or nicknames.")
    role_name_or_id: Optional[Union[str, int]] = Field(default=None, description="Optional role name or ID to filter members by.")

class ListMembersTool(BaseTool):
    name = "list_members"
    description = "Lists members in the server with optional filtering by role or search query."
    schema = ListMembersParams
    read_only = True

    async def execute(self, params: ListMembersParams, guild: discord.Guild):
        members = []
        
        target_role = None
        if params.role_name_or_id:
            if isinstance(params.role_name_or_id, int):
                target_role = guild.get_role(params.role_name_or_id)
            else:
                target_role = discord.utils.get(guild.roles, name=params.role_name_or_id)

        if params.search_query:
            # If search query is provided, use query_members
            search_results = await guild.query_members(query=params.search_query, limit=params.limit)
            source_members = search_results
        elif target_role:
            source_members = target_role.members[:params.limit]
        else:
            source_members = guild.members[:params.limit]

        for member in source_members:
            members.append({
                "name": member.name,
                "display_name": member.display_name,
                "id": member.id,
                "roles": [role.name for role in member.roles if role.name != "@everyone"],
                "joined_at": str(member.joined_at)
            })
        
        return members
