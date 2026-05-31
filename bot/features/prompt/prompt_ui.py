import discord
from discord import ui
from typing import Callable, List
from .models import ExecutionPlan, Task

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

    @ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, button: ui.Button, interaction: discord.Interaction):
        await self.on_accept(interaction)

    @ui.button(label="Accept-All", style=discord.ButtonStyle.secondary)
    async def accept_all(self, button: ui.Button, interaction: discord.Interaction):
        await self.on_accept_all(interaction)

    @ui.button(label="Reject", style=discord.ButtonStyle.blurple)
    async def reject(self, button: ui.Button, interaction: discord.Interaction):
        await self.on_reject(interaction)

    @ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button: ui.Button, interaction: discord.Interaction):
        await self.on_cancel(interaction)

def create_plan_embed(plan: ExecutionPlan) -> discord.Embed:
    embed = discord.Embed(
        title="[Plan-Mode] Proposed Server Changes",
        description=plan.summary,
        color=discord.Color.blue()
    )
    for task in plan.tasks:
        embed.add_field(
            name=f"Task {task.order}: {task.action}",
            value=task.description,
            inline=False
        )
    embed.set_footer(text="Please review the plan before proceeding.")
    return embed

def create_task_embed(task: Task, total_tasks: int) -> discord.Embed:
    embed = discord.Embed(
        title=f"Executing Task {task.order} of {total_tasks}",
        description=task.description,
        color=discord.Color.orange()
    )
    embed.add_field(name="Action", value=task.action, inline=True)
    
    # Format parameters nicely, handling both dict and Pydantic models
    params = task.parameters
    if hasattr(params, "dict"):
        params = params.dict()
    
    params_str = "\n".join([f"**{k}:** {v}" for k, v in params.items() if v is not None])
    embed.add_field(name="Parameters", value=params_str or "None", inline=False)
    
    return embed
