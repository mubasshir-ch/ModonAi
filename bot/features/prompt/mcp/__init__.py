from .registry import registry
from .tools import (
    CreateRoleTool,
    CreateCategoryTool,
    CreateChannelTool,
    DeleteChannelTool,
    DeleteRoleTool,
    AssignRoleTool,
    RemoveRoleTool
)

# Register all tools
registry.register(CreateRoleTool())
registry.register(CreateCategoryTool())
registry.register(CreateChannelTool())
registry.register(DeleteChannelTool())
registry.register(DeleteRoleTool())
registry.register(AssignRoleTool())
registry.register(RemoveRoleTool())

__all__ = ["registry"]
