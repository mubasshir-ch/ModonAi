import os
import discord
import instructor
import logging
import litellm
from litellm import completion
from typing import List, Optional
from .models.base import ExecutionPlan, RevisedPlan, Task
from .mcp import registry

class PromptService:
    def __init__(self, model: str = None):
        self.model = model or os.getenv("LLM_MODEL", "github/gpt-4o-mini")
        
        self.api_key = os.getenv("GITHUB_API_KEY") or os.getenv("LLM_API_KEY")
        if self.api_key:
            os.environ["GITHUB_API_KEY"] = self.api_key
        
        self.logger = logging.getLogger("modonai.prompt_service")

        if os.getenv("LITELLM_DEBUG") == "True":
            litellm._turn_on_debug()
            self.logger.info("LiteLLM debug mode enabled.")
        
        self.client = instructor.from_litellm(completion)
        self.logger.info(f"PromptService initialized with model: {self.model}")

    def _get_system_prompt(self) -> str:
        base_rules = """
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
        """
        return base_rules + "\n" + registry.get_system_prompt_addition()

    async def generate_plan(self, user_prompt: str, context: str = "") -> ExecutionPlan:
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

    async def refine_plan(self, original_plan: ExecutionPlan, suggestion: str, context: str = "") -> RevisedPlan:
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": f"Current Plan: {original_plan.model_dump_json()}\n\nSuggestion: {suggestion}\n\nUpdate the plan accordingly and provide an explanation."}
        ]

        revised = self.client.chat.completions.create(
            model=self.model,
            response_model=RevisedPlan,
            messages=messages,
        )
        return revised

    async def execute_task(self, task: Task, guild: discord.Guild):
        action = task.action
        tool = registry.get_tool(action)
        
        if not tool:
            raise ValueError(f"Tool '{action}' is not registered or supported.")
            
        params = task.parameters
        if isinstance(params, dict):
            # Parse dict into the tool's schema if it hasn't been parsed yet
            params = tool.schema(**params)

        await tool.execute(params, guild)
