# MCP Tools To-Do List

This document tracks the Discord Model Context Protocol (MCP) tools that need to be implemented. The architecture will be refactored so that each tool is a self-contained module encompassing its schema, description, and execution logic.

## High Priority (Retrieval & Context)
- [x] `list_roles` (Get all roles in the server)
- [x] `list_channels` (Get all categories, text, and voice channels)
- [x] `list_members` (Get members, optionally filtered by role or search query)
- [x] `read_messages` (Fetch recent messages from a specific channel)
- [x] `get_server_info` (Get overall guild stats, verification level, etc.)
- [x] `get_audit_logs` (Read recent moderation events)
- [x] `get_channel_info` (Get detailed info about a specific channel by ID)
- [x] `get_role_info` (Get detailed info about a specific role by ID)
- [x] `get_member_info` (Get detailed info about a specific member by ID)
- [x] `list_guilds` (List all servers the bot is in)
- [x] `list_emojis` (List all emojis in the server)
- [x] `list_invites` (List all active invites in the server)

## High Priority (Messaging & Interaction)
- [ ] `send_message` (Send a text message to a channel)
- [ ] `send_embed_message` (Send a rich embed message to a channel)
- [ ] `send_dm` (Send a private message to a user)
- [ ] `edit_message` (Edit a message sent by the bot)
- [ ] `delete_message` (Delete a specific message)

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

## Implementation Notes
1. Define the Pydantic schema in the tool's specific module.
2. Provide a clear, descriptive docstring for the schema so the LLM understands its purpose.
3. Write the `pycord` execution logic within the same module.
4. Register the tool with the central MCP server orchestrator in `bot/features/prompt/mcp/__init__.py`.
