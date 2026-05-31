import discord
import logging
import json
from discord.ext import commands
from discord import option
from .prompt_service import PromptService
from .prompt_ui import PlanReviewView, SuggestionModal, TaskVerificationView, create_plan_embed, create_task_embed
from .models.base import ExecutionPlan, RevisedPlan, Task

class PromptCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.service = PromptService()
        self.logger = logging.getLogger("modonai.prompt")

    @discord.slash_command(name="prompt", description="Admin AI agent for server modifications")
    @option("prompt", description="Describe what you want to do (e.g., 'Create a category named Core...')")
    async def prompt(self, ctx: discord.ApplicationContext, prompt: str):
        self.logger.info(f"Received prompt from {ctx.author}: {prompt}")
        await ctx.defer()
        
        initial_context = self._get_execution_context(ctx)
        
        try:
            # Phase 1: Investigation
            async def update_status(msg: str):
                await ctx.edit(content=msg)

            await ctx.edit(content="🚀 Starting investigation phase...")
            gathered_context = await self.service.investigate(prompt, ctx.guild, initial_context, on_step=update_status)
            self.logger.debug(f"Gathered context: {gathered_context}")
            
            # Phase 2: Planning
            await ctx.edit(content="📝 Drafting final execution plan...")
            plan = await self.service.generate_plan(prompt, gathered_context)
            self.logger.info("Execution plan generated successfully.")
            
            # Phase 3: Review (Plan-Mode)
            await self._enter_plan_mode(ctx, plan)
        except Exception as e:
            self.logger.error(f"Failed to process prompt: {e}", exc_info=True)
            error_msg = str(e)
            if len(error_msg) > 1900:
                error_msg = error_msg[:1900] + "... (truncated)"
            await ctx.edit(content=f"Error: {error_msg}")

    def _get_execution_context(self, ctx: discord.ApplicationContext) -> str:
        guild = ctx.guild
        user = ctx.author
        channel = ctx.channel
        
        context_data = {
            "guild": {
                "name": guild.name,
                "id": guild.id,
                "member_count": guild.member_count
            },
            "channel": {
                "name": channel.name,
                "id": channel.id,
                "type": str(channel.type)
            },
            "user": {
                "name": user.name,
                "id": user.id,
                "roles": [role.name for role in user.roles if role.name != "@everyone"]
            },
            "command": {
                "name": ctx.command.name
            }
        }
        return json.dumps(context_data, indent=2)

    async def _enter_plan_mode(self, ctx: discord.ApplicationContext | discord.Interaction, plan: ExecutionPlan, explanation: str = None):
        embed = create_plan_embed(plan)
        content = f"**AI Explanation:** {explanation}" if explanation else ""
        
        async def on_proceed(interaction: discord.Interaction):
            await interaction.response.edit_message(content="Entering Execution-Mode...", embed=None, view=None)
            await self._start_execution(interaction, plan)

        async def on_suggest(interaction: discord.Interaction):
            modal = SuggestionModal(on_submit=lambda sugg, inter: self._on_suggestion_submit(inter, plan, sugg))
            await interaction.response.send_modal(modal)

        async def on_cancel(interaction: discord.Interaction):
            await interaction.response.edit_message(content="Operation cancelled.", embed=None, view=None)

        view = PlanReviewView(on_proceed, on_suggest, on_cancel)
        if isinstance(ctx, discord.ApplicationContext):
            await ctx.respond(content=content, embed=embed, view=view)
        else:
            await ctx.edit_original_response(content=content, embed=embed, view=view)

    async def _on_suggestion_submit(self, interaction: discord.Interaction, original_plan: ExecutionPlan, suggestion: str):
        await interaction.edit_original_response(content="Refining plan...", embed=None, view=None)
        
        try:
            revised = await self.service.refine_plan(original_plan, suggestion)
        except Exception as e:
            await interaction.edit_original_response(content=f"Error refining plan: {e}")
            return

        await self._enter_plan_mode(interaction, revised.plan, explanation=revised.explanation)

    async def _start_execution(self, interaction: discord.Interaction, plan: ExecutionPlan):
        self._current_plan = plan
        self._current_task_index = 0
        self._accept_all = False
        await self._execute_next_task(interaction)

    async def _execute_next_task(self, interaction: discord.Interaction):
        if self._current_task_index >= len(self._current_plan.tasks):
            await interaction.edit_original_response(content="All tasks completed successfully!", embed=None, view=None)
            return

        task = self._current_plan.tasks[self._current_task_index]
        
        if self._accept_all:
            await self._run_task(interaction, task)
            return

        embed = create_task_embed(task, len(self._current_plan.tasks))

        async def on_accept(inter: discord.Interaction):
            await inter.response.edit_message(content=f"Executing Task {task.order}...", embed=None, view=None)
            await self._run_task(inter, task)

        async def on_accept_all(inter: discord.Interaction):
            self._accept_all = True
            await inter.response.edit_message(content="Executing all remaining tasks...", embed=None, view=None)
            await self._run_task(inter, task)

        async def on_reject(inter: discord.Interaction):
            await inter.response.send_message("Reject/Refine is not yet implemented for execution mode.", ephemeral=True)

        async def on_cancel(inter: discord.Interaction):
            await inter.response.edit_message(content="Execution cancelled.", embed=None, view=None)

        view = TaskVerificationView(on_accept, on_accept_all, on_reject, on_cancel)
        await interaction.edit_original_response(content="", embed=embed, view=view)

    async def _run_task(self, interaction: discord.Interaction, task: Task):
        await self._run_task_real(interaction, task)

    async def _run_task_real(self, interaction: discord.Interaction, task: Task):
        try:
            await self.service.execute_task(task, interaction.guild)
            self._current_task_index += 1
            await self._execute_next_task(interaction)
        except Exception as e:
            await interaction.edit_original_response(content=f"Error executing task {task.order}: {e}\nStopping execution.")

def setup(bot: commands.Bot):
    bot.add_cog(PromptCog(bot))
