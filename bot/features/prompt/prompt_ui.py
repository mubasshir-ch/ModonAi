import discord
from discord import ui
from typing import Callable, List, Optional
from .models.base import BroadPlan, ChecklistTask, AgentStepResponse, AgentToolCall

class SuggestionModal(ui.Modal):
    def __init__(self, on_submit: Callable[[str], None], *args, **kwargs):
        super().__init__(title="Suggest Changes", *args, **kwargs)
        self.on_submit = on_submit
        self.add_item(ui.InputText(label="What would you like to change?", style=discord.InputTextStyle.paragraph))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.on_submit(self.children[0].value, interaction)

class PlanReviewView(ui.View):
    def __init__(self, on_proceed: Callable, on_suggest: Callable, on_cancel: Callable):
        super().__init__(timeout=None)
        self.on_proceed = on_proceed
        self.on_suggest = on_suggest
        self.on_cancel = on_cancel

    @ui.button(label="Proceed", style=discord.ButtonStyle.green)
    async def proceed(self, button: ui.Button, interaction: discord.Interaction):
        await self.on_proceed(interaction)

    @ui.button(label="Suggest Changes", style=discord.ButtonStyle.blurple)
    async def suggest(self, button: ui.Button, interaction: discord.Interaction):
        await self.on_suggest(interaction)

    @ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button: ui.Button, interaction: discord.Interaction):
        await self.on_cancel(interaction)

class TaskVerificationView(ui.View):
    def __init__(self, on_accept: Callable, on_accept_all: Callable, on_reject: Callable, on_cancel: Callable):
        super().__init__(timeout=None)
        self.on_accept = on_accept
        self.on_accept_all = on_accept_all
        self.on_reject = on_reject
        self.on_cancel = on_cancel

    @ui.button(label="Approve Action", style=discord.ButtonStyle.green)
    async def accept(self, button: ui.Button, interaction: discord.Interaction):
        await self.on_accept(interaction)

    @ui.button(label="Approve All", style=discord.ButtonStyle.secondary)
    async def accept_all(self, button: ui.Button, interaction: discord.Interaction):
        await self.on_accept_all(interaction)

    @ui.button(label="Reject / Suggest Edit", style=discord.ButtonStyle.blurple)
    async def reject(self, button: ui.Button, interaction: discord.Interaction):
        await self.on_reject(interaction)

    @ui.button(label="Cancel Mission", style=discord.ButtonStyle.red)
    async def cancel(self, button: ui.Button, interaction: discord.Interaction):
        await self.on_cancel(interaction)

def truncate(text: str, limit: int = 1024) -> str:
    if len(text) <= limit:
        return text
    return text[:limit-3] + "..."

def format_checklist(tasks: List[ChecklistTask]) -> str:
    icons = {
        "pending": "⏳",
        "done": "✅",
        "failed": "❌",
        "skipped": "⏩"
    }
    checklist = "\n".join([f"{icons.get(t.status, '❓')} {t.description}" for t in tasks])
    return truncate(checklist, 1024)

def create_broad_plan_embed(plan: BroadPlan) -> discord.Embed:
    embed = discord.Embed(
        title="[Plan-Mode] Mission Objectives",
        description=truncate(plan.summary, 4096),
        color=discord.Color.blue()
    )
    embed.add_field(name="Task Checklist", value=format_checklist(plan.tasks), inline=False)
    embed.set_footer(text="Please approve these high-level objectives.")
    return embed

def create_agent_step_embed(response: AgentStepResponse, result: Any = None) -> discord.Embed:
    embed = discord.Embed(
        title="🤖 Agent Thinking...",
        description=truncate(response.thought, 4096),
        color=discord.Color.orange()
    )
    
    if response.tool_call:
        embed.add_field(name="Next Action", value=f"`{response.tool_call.action}`", inline=True)
        # Format parameters safely
        params = response.tool_call.parameters
        if hasattr(params, "model_dump"):
            params = params.model_dump()
        params_str = "\n".join([f"**{k}:** {v}" for k, v in params.items() if v is not None])
        embed.add_field(name="Parameters", value=truncate(params_str, 1024) or "None", inline=False)

    if result is not None:
        result_str = str(result)
        # Use a different color if it's an error
        if "error" in result_str.lower():
            embed.color = discord.Color.red()
            embed.add_field(name="❌ Tool Error", value=f"```py\n{truncate(result_str, 1000)}\n```", inline=False)
        else:
            embed.add_field(name="📥 Tool Output", value=f"```json\n{truncate(result_str, 1000)}\n```", inline=False)

    embed.add_field(name="Current Checklist", value=format_checklist(response.updated_checklist), inline=False)
    
    return embed

def create_final_summary_embed(summary: str, tasks: List[ChecklistTask]) -> discord.Embed:
    embed = discord.Embed(
        title="✅ Mission Accomplished",
        description=truncate(summary, 4096),
        color=discord.Color.green()
    )
    embed.add_field(name="Final Checklist", value=format_checklist(tasks), inline=False)
    return embed
