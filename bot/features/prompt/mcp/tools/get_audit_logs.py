import discord
from pydantic import BaseModel, Field
from typing import Optional
from ..base import BaseTool

class GetAuditLogsParams(BaseModel):
    limit: int = Field(default=10, description="Number of audit log entries to fetch (max 100).")
    user_name_or_id: Optional[str] = Field(default=None, description="Optional user name or ID to filter logs by.")

class GetAuditLogsTool(BaseTool):
    name = "get_audit_logs"
    description = "Reads recent administrative actions from the server's audit logs."
    schema = GetAuditLogsParams
    read_only = True

    async def execute(self, params: GetAuditLogsParams, guild: discord.Guild):
        logs = []
        
        user = None
        if params.user_name_or_id:
            if params.user_name_or_id.isdigit():
                user = await guild.fetch_member(int(params.user_name_or_id))
            else:
                user = discord.utils.get(guild.members, name=params.user_name_or_id)

        async for entry in guild.audit_logs(limit=params.limit, user=user):
            logs.append({
                "user": str(entry.user),
                "action": str(entry.action),
                "target": str(entry.target),
                "reason": entry.reason,
                "timestamp": str(entry.created_at)
            })
        
        return logs
