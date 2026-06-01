import discord

async def process_overwrites(guild: discord.Guild, overwrites_data: list) -> dict:
    """
    Converts PermissionOverwrite model data (dict representation) into discord.PermissionOverwrite objects.
    """
    overwrites = {}
    for data in overwrites_data:
        # data might be a dict or a pydantic model, so we ensure dict
        if hasattr(data, "dict"):
            data = data.dict()
            
        target = None
        if data["target_type"] == "everyone":
            target = guild.default_role
        elif data["target_type"] == "role":
            target = discord.utils.get(guild.roles, name=data["target_name"])
        elif data["target_type"] == "member":
            target = discord.utils.get(guild.members, name=data["target_name"])

        if target:
            allow = discord.Permissions(**{p: True for p in data.get("allow", [])})
            deny = discord.Permissions(**{p: True for p in data.get("deny", [])})
            overwrites[target] = discord.PermissionOverwrite.from_pair(allow, deny)
    
    return overwrites

from typing import Union, Optional

async def resolve_channel(guild: discord.Guild, name_or_id: Union[str, int]) -> Optional[discord.abc.GuildChannel]:
    if isinstance(name_or_id, int) or str(name_or_id).isdigit():
        cid = int(name_or_id)
        channel = guild.get_channel(cid)
        if not channel:
            try:
                channel = await guild.fetch_channel(cid)
            except discord.NotFound:
                pass
        return channel
    else:
        name = str(name_or_id)
        channel = discord.utils.get(guild.channels, name=name)
        if not channel:
            try:
                channels = await guild.fetch_channels()
                channel = discord.utils.get(channels, name=name)
            except Exception:
                pass
        return channel

async def resolve_member(guild: discord.Guild, name_or_id: Union[str, int]) -> Optional[discord.Member]:
    if isinstance(name_or_id, int) or str(name_or_id).isdigit():
        mid = int(name_or_id)
        member = guild.get_member(mid)
        if not member:
            try:
                member = await guild.fetch_member(mid)
            except discord.NotFound:
                pass
        return member
    else:
        name = str(name_or_id)
        member = discord.utils.get(guild.members, name=name)
        if not member:
            try:
                members = await guild.query_members(query=name, limit=1)
                if members:
                    member = members[0]
            except Exception:
                pass
        return member

async def resolve_role(guild: discord.Guild, name_or_id: Union[str, int]) -> Optional[discord.Role]:
    if isinstance(name_or_id, int) or str(name_or_id).isdigit():
        rid = int(name_or_id)
        # Roles are strictly cached per guild object in Pycord
        return guild.get_role(rid)
    else:
        return discord.utils.get(guild.roles, name=str(name_or_id))
