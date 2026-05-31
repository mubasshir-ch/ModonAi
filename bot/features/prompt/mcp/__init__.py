from .registry import registry
from .tools import (
    CreateRoleTool,
    CreateCategoryTool,
    CreateChannelTool,
    DeleteChannelTool,
    DeleteRoleTool,
    AssignRoleTool,
    RemoveRoleTool,
    ListRolesTool,
    ListChannelsTool,
    ListMembersTool,
    ReadMessagesTool,
    GetServerInfoTool,
    GetAuditLogsTool,
    GetChannelInfoTool,
    GetRoleInfoTool,
    GetMemberInfoTool,
    ListGuildsTool,
    ListEmojisTool,
    ListInvitesTool,
    SendMessageTool,
    SendEmbedMessageTool,
    SendDMTool
)

# Register all tools
registry.register(CreateRoleTool())
registry.register(CreateCategoryTool())
registry.register(CreateChannelTool())
registry.register(DeleteChannelTool())
registry.register(DeleteRoleTool())
registry.register(AssignRoleTool())
registry.register(RemoveRoleTool())
registry.register(ListRolesTool())
registry.register(ListChannelsTool())
registry.register(ListMembersTool())
registry.register(ReadMessagesTool())
registry.register(GetServerInfoTool())
registry.register(GetAuditLogsTool())
registry.register(GetChannelInfoTool())
registry.register(GetRoleInfoTool())
registry.register(GetMemberInfoTool())
registry.register(ListGuildsTool())
registry.register(ListEmojisTool())
registry.register(ListInvitesTool())
registry.register(SendMessageTool())
registry.register(SendEmbedMessageTool())
registry.register(SendDMTool())

__all__ = ["registry"]
