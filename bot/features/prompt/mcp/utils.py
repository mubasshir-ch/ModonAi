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
