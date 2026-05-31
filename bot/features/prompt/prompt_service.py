import os
import discord
import instructor
import logging
import litellm
from litellm import completion
from typing import List, Optional
from .models import ExecutionPlan, Task

class PromptService:
    def __init__(self, model: str = None):
        self.model = model or os.getenv("LLM_MODEL", "github/gpt-4o-mini")
        
        # LiteLLM GitHub provider specifically expects GITHUB_API_KEY
        self.api_key = os.getenv("GITHUB_API_KEY") or os.getenv("LLM_API_KEY")
        if self.api_key:
            os.environ["GITHUB_API_KEY"] = self.api_key
        
        self.logger = logging.getLogger("modonai.prompt_service")

        if os.getenv("LITELLM_DEBUG") == "True":
            litellm._turn_on_debug()
            self.logger.info("LiteLLM debug mode enabled.")
        
        # Initialize instructor with litellm
        self.client = instructor.from_litellm(completion)
        self.logger.info(f"PromptService initialized with model: {self.model}")

    def _get_system_prompt(self) -> str:
        return """
        You are ModonAi, a professional Discord server administrator AI.
        Your goal is to parse user instructions and create a structured execution plan to modify a Discord server.

        Rules for Plan Generation:
        1. Order Matters: You must create dependencies before the items that depend on them.
           - Create roles BEFORE creating channels that use those roles in permission overwrites.
           - Create categories BEFORE creating channels that should be inside those categories.
        2. Parameter Nesting: ALL action-specific fields MUST be nested inside the 'parameters' dictionary.
           - Correct: {"action": "create_role", "parameters": {"name": "Admin", "color": "#ff0000"}}
           - Incorrect: {"action": "create_role", "name": "Admin", "color": "#ff0000"}
        3. Permission Overwrites: 
           - 'target_type' can be 'role', 'member', or 'everyone'.
           - 'target_name' for everyone must be '@everyone'.
           - For roles, use the exact name of the role.
        4. Human Readable: Provide a clear summary and short descriptions for each task.
        5. Actions Supported:
           - create_role: {name, color, permissions, mentionable, hoist}
           - create_category: {name, overwrites}
           - create_channel: {name, channel_type, category_name, overwrites, topic, nsfw, thread_replies}
           - delete_channel: {name_or_id}
           - delete_role: {name_or_id}
           - assign_role: {member_name_or_id, role_name_or_id}
           - remove_role: {member_name_or_id, role_name_or_id}
        """

    async def generate_plan(self, user_prompt: str, context: str = "") -> ExecutionPlan:
        """
        Generates an execution plan from a user prompt.
        context: Optional string containing current server state (channels, roles, etc.)
        """
        self.logger.info(f"Generating plan for prompt: {user_prompt[:50]}...")
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": f"Context:\n{context}\n\nUser Instruction: {user_prompt}"}
        ]

        try:
            plan = self.client.chat.completions.create(
                model=self.model,
                response_model=ExecutionPlan,
                messages=messages,
            )
            self.logger.debug(f"Plan generated: {plan}")
            return plan
        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}")
            raise e

    async def refine_plan(self, original_plan: ExecutionPlan, suggestion: str, context: str = "") -> ExecutionPlan:
        """
        Refines an existing plan based on user feedback.
        """
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": f"Current Plan: {original_plan.json()}\n\nSuggestion: {suggestion}\n\nUpdate the plan accordingly."}
        ]

        plan = self.client.chat.completions.create(
            model=self.model,
            response_model=ExecutionPlan,
            messages=messages,
        )
        return plan

    async def execute_task(self, task: Task, guild: discord.Guild):
        """
        Executes a single task using pycord.
        """
        action = task.action
        # Ensure parameters is a dict if it's a Pydantic model
        params = task.parameters
        if hasattr(params, "dict"):
            params = params.dict()

        if action == "create_role":
            color = discord.Color(int(params["color"].lstrip("#"), 16)) if params.get("color") else discord.Color.default()
            await guild.create_role(
                name=params["name"],
                color=color,
                mentionable=params.get("mentionable", False),
                hoist=params.get("hoist", False)
            )

        elif action == "create_category":
            overwrites = await self._process_overwrites(guild, params.get("overwrites", []))
            await guild.create_category(name=params["name"], overwrites=overwrites)

        elif action == "create_channel":
            overwrites = await self._process_overwrites(guild, params.get("overwrites", []))
            category = discord.utils.get(guild.categories, name=params.get("category_name"))
            
            channel_type = params.get("channel_type", "text")
            if channel_type == "text":
                await guild.create_text_channel(
                    name=params["name"],
                    category=category,
                    topic=params.get("topic"),
                    overwrites=overwrites,
                    nsfw=params.get("nsfw", False)
                )
            elif channel_type == "voice":
                await guild.create_voice_channel(
                    name=params["name"],
                    category=category,
                    overwrites=overwrites
                )

        elif action == "delete_channel":
            target = params.get("name_or_id")
            channel = discord.utils.get(guild.channels, name=target) if isinstance(target, str) else guild.get_channel(target)
            if channel:
                await channel.delete()

        elif action == "delete_role":
            target = params.get("name_or_id")
            role = discord.utils.get(guild.roles, name=target) if isinstance(target, str) else guild.get_role(target)
            if role:
                await role.delete()

    async def _process_overwrites(self, guild: discord.Guild, overwrites_data: list) -> dict:
        """
        Converts our PermissionOverwrite model data into discord.PermissionOverwrite objects.
        """
        overwrites = {}
        for data in overwrites_data:
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
