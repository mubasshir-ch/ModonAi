import discord
import logging
import json
from discord.ext import commands
from discord import option
from .prompt_service import PromptService
from .prompt_ui import (
    PlanReviewView, 
    SuggestionModal, 
    TaskVerificationView, 
    create_broad_plan_embed, 
    create_agent_step_embed,
    create_final_summary_embed
)
from .models.base import BroadPlan, RevisedBroadPlan, ChecklistTask, AgentStepResponse
from .mcp import registry

class PromptCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.service = PromptService()
        self.logger = logging.getLogger("modonai.prompt")
        
        # In-memory state for active missions
        # In a production bot, this would be in a database or Redis
        self._active_missions = {}

    @discord.slash_command(name="prompt", description="Agentic AI for complex server management")
    @option("prompt", description="Describe your mission (e.g., 'Setup a staff category and roles')")
    async def prompt(self, ctx: discord.ApplicationContext, prompt: str):
        self.logger.info(f"Received mission from {ctx.author}: {prompt}")
        await ctx.defer()
        
        initial_context = self._get_execution_context(ctx)
        
        try:
            await ctx.edit(content="🛰️ Analyzing mission and drafting objectives...")
            plan = await self.service.generate_broad_plan(prompt, initial_context)
            
            await self._enter_review_phase(ctx, plan, prompt)
        except Exception as e:
            self.logger.error(f"Failed to start mission: {e}", exc_info=True)
            await ctx.edit(content=f"❌ Error starting mission: {str(e)[:1900]}")

    def _get_execution_context(self, ctx: discord.ApplicationContext | discord.Interaction) -> str:
        guild = ctx.guild
        user = ctx.author if isinstance(ctx, discord.ApplicationContext) else ctx.user
        channel = ctx.channel
        return json.dumps({
            "guild": {"name": guild.name, "id": guild.id, "member_count": guild.member_count},
            "channel": {"name": channel.name, "id": channel.id, "type": str(channel.type)},
            "user": {"name": user.name, "id": user.id, "roles": [role.name for role in user.roles if role.name != "@everyone"]}
        }, indent=2)

    async def _enter_review_phase(self, ctx: discord.ApplicationContext | discord.Interaction, plan: BroadPlan, original_prompt: str, explanation: str = None):
        embed = create_broad_plan_embed(plan)
        content = f"**AI Explanation:** {explanation}" if explanation else ""
        
        async def on_proceed(interaction: discord.Interaction):
            await interaction.response.edit_message(content="🚀 Mission Authorized. Entering Agentic Loop...", embed=None, view=None)
            await self._start_agentic_loop(interaction, plan, original_prompt)

        async def on_suggest(interaction: discord.Interaction):
            modal = SuggestionModal(on_submit=lambda sugg, inter: self._on_suggestion_submit(inter, plan, original_prompt, sugg))
            await interaction.response.send_modal(modal)

        async def on_cancel(interaction: discord.Interaction):
            await interaction.response.edit_message(content="🛑 Mission Aborted.", embed=None, view=None)

        view = PlanReviewView(on_proceed, on_suggest, on_cancel)
        if isinstance(ctx, discord.ApplicationContext):
            await ctx.respond(content=content, embed=embed, view=view)
        else:
            await ctx.edit_original_response(content=content, embed=embed, view=view)

    async def _on_suggestion_submit(self, interaction: discord.Interaction, original_plan: BroadPlan, original_prompt: str, suggestion: str):
        await interaction.edit_original_response(content="🔄 Refining objectives...", embed=None, view=None)
        try:
            revised = await self.service.refine_broad_plan(original_plan, suggestion, self._get_execution_context(interaction))
            await self._enter_review_phase(interaction, revised.plan, original_prompt, explanation=revised.explanation)
        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Error refining plan: {str(e)[:1900]}")

    async def _start_agentic_loop(self, interaction: discord.Interaction, plan: BroadPlan, original_prompt: str):
        mission_id = interaction.message.id
        self._active_missions[mission_id] = {
            "prompt": original_prompt,
            "checklist": plan.tasks,
            "history": [],
            "accept_all": False
        }
        await self._run_next_loop_step(interaction, mission_id)

    async def _run_next_loop_step(self, interaction: discord.Interaction, mission_id: int):
        mission = self._active_missions.get(mission_id)
        if not mission: return

        try:
            # 1. AI decides next step
            context = self._get_execution_context(interaction)
            response = await self.service.run_agent_step(mission["prompt"], mission["history"], context)
            
            # Update checklist from AI
            mission["checklist"] = response.updated_checklist

            if response.is_goal_reached:
                embed = create_final_summary_embed(response.final_summary, mission["checklist"])
                await interaction.edit_original_response(content="✅ Mission Complete.", embed=embed, view=None)
                del self._active_missions[mission_id]
                return

            # 2. Handle Tool Call
            if not response.tool_call:
                # Just internal thought, show it and skip to next step
                embed = create_agent_step_embed(response)
                await interaction.edit_original_response(content="🤔 **Thinking...**", embed=embed, view=None)
                
                mission["history"].append({"role": "assistant", "content": response.model_dump_json()})
                
                import asyncio
                await asyncio.sleep(1.5)
                await self._run_next_loop_step(interaction, mission_id)
                return

            tool_name = response.tool_call.action
            tool = registry.get_tool(tool_name)
            
            if not tool:
                mission["history"].append({"role": "assistant", "content": response.model_dump_json()})
                mission["history"].append({"role": "user", "content": f"Error: Tool '{tool_name}' is unknown."})
                await self._run_next_loop_step(interaction, mission_id)
                return

            # Permission Check
            if tool.read_only or mission["accept_all"]:
                # Show what we are doing
                embed = create_agent_step_embed(response)
                status_text = "🔍 **Investigating...**" if tool.read_only else f"⏳ **Executing `{tool_name}`...**"
                await interaction.edit_original_response(content=status_text, embed=embed, view=None)

                # Execute autonomously
                result = await self.service.execute_tool(tool_name, response.tool_call.parameters, interaction.guild)
                
                # Show result in UI before moving on
                result_embed = create_agent_step_embed(response, result=result)
                await interaction.edit_original_response(content=status_text, embed=result_embed, view=None)
                
                mission["history"].append({"role": "assistant", "content": response.model_dump_json()})
                mission["history"].append({"role": "user", "content": f"Tool Result ({tool_name}): {result}"})
                
                # Small delay so the user can read the result
                import asyncio
                await asyncio.sleep(1.5)
                
                await self._run_next_loop_step(interaction, mission_id)
            else:
                # Mutation Tool - Ask for permission
                embed = create_agent_step_embed(response)
                
                async def on_accept(inter: discord.Interaction):
                    await inter.response.edit_message(content=f"⏳ Executing `{tool_name}`...", view=None)
                    result = await self.service.execute_tool(tool_name, response.tool_call.parameters, inter.guild)
                    
                    # Show result
                    result_embed = create_agent_step_embed(response, result=result)
                    await inter.edit_original_response(content=f"✅ Finished `{tool_name}`", embed=result_embed, view=None)
                    
                    mission["history"].append({"role": "assistant", "content": response.model_dump_json()})
                    mission["history"].append({"role": "user", "content": f"Tool Result ({tool_name}): {result}"})
                    
                    import asyncio
                    await asyncio.sleep(1)
                    await self._run_next_loop_step(inter, mission_id)

                async def on_accept_all(inter: discord.Interaction):
                    mission["accept_all"] = True
                    await on_accept(inter)

                async def on_reject(inter: discord.Interaction):
                    modal = SuggestionModal(on_submit=lambda sugg, i: self._on_rejection_submit(i, mission_id, response, sugg))
                    await inter.response.send_modal(modal)

                async def on_cancel(inter: discord.Interaction):
                    await inter.response.edit_message(content="🛑 Mission Aborted during execution.", embed=None, view=None)
                    del self._active_missions[mission_id]

                view = TaskVerificationView(on_accept, on_accept_all, on_reject, on_cancel)
                await interaction.edit_original_response(content="", embed=embed, view=view)

        except Exception as e:
            self.logger.error(f"Loop error: {e}", exc_info=True)
            await interaction.edit_original_response(content=f"⚠️ Loop Error: {str(e)[:1900]}")

    async def _on_rejection_submit(self, interaction: discord.Interaction, mission_id: int, step_response: AgentStepResponse, suggestion: str):
        mission = self._active_missions.get(mission_id)
        if not mission: return
        
        await interaction.edit_original_response(content="🔄 Incorporating rejection feedback...", embed=None, view=None)
        mission["history"].append({"role": "assistant", "content": step_response.model_dump_json()})
        mission["history"].append({"role": "user", "content": f"USER REJECTED THIS ACTION. Feedback: {suggestion}"})
        await self._run_next_loop_step(interaction, mission_id)

def setup(bot: commands.Bot):
    bot.add_cog(PromptCog(bot))
