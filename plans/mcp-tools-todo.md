# MCP Tools To-Do List

This document tracks the Discord Model Context Protocol (MCP) tools that need to be implemented. The architecture will be refactored so that each tool is a self-contained module encompassing its schema, description, and execution logic.

## High Priority (Server Structure)
- [x] `create_role`
- [x] `create_category`
- [x] `create_channel` (Text & Voice)
- [x] `delete_channel`
- [x] `delete_role`
- [ ] `update_role` (Modify permissions, color, name)
- [ ] `update_channel` (Modify permissions, topic, name)
- [ ] `move_channel` (Change category or position)
- [ ] `update_server_settings` (Name, icon, verification level)

## Medium Priority (Moderation & Membership)
- [x] `assign_role`
- [x] `remove_role`
- [ ] `kick_member`
- [ ] `ban_member`
- [ ] `timeout_member` (Timeout for a specific duration)
- [ ] `remove_timeout`
- [ ] `purge_messages` (Bulk delete messages in a channel)

## Low Priority (Advanced Features)
- [ ] `create_webhook`
- [ ] `delete_webhook`
- [ ] `create_forum_thread`
- [ ] `create_invite`
- [ ] `get_audit_logs` (Read-only tool for the AI to understand recent server events)

## Implementation Notes
When implementing a new tool:
1. Define the Pydantic schema in the tool's specific module.
2. Provide a clear, descriptive docstring for the schema so the LLM understands its purpose.
3. Write the `pycord` execution logic within the same module.
4. Register the tool with the central MCP server orchestrator.
