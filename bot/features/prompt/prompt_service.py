import os
import discord
import instructor
import logging
import litellm
from litellm import completion
from typing import List, Optional, Union, Dict, Any, Callable
from .models.base import ExecutionPlan, RevisedPlan, Task, InvestigationStep, InvestigationFinish
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

    def _get_system_prompt(self, read_only: bool = None) -> str:
        base_rules = """
        You are ModonAi, a professional Discord server administrator AI.
        Your goal is to parse user instructions and manage a Discord server.

        General Rules:
        1. Accuracy: Use the exact IDs and names retrieved from the server.
        2. Dependency Management: Ensure roles and categories exist before using them.
        3. Human Readable: Provide clear explanations and summaries.
        4. Parameter Nesting: ALL action-specific fields MUST be nested inside the 'parameters' dictionary.
        """
        
        if read_only is True:
            investigation_rules = """
            PHASE 1: INVESTIGATION
            You are currently in the investigation phase. Your goal is to gather all necessary information (IDs, roles, channel structures, etc.) 
            required to fulfill the user's request. 
            - You can ONLY use READ-ONLY tools.
            - If you have all the information you need, use the 'InvestigationFinish' model to provide the final context.
            - Be thorough. If a user asks to modify a channel, first find that channel's ID.
            """
            return base_rules + investigation_rules + "\n" + registry.get_system_prompt_addition(read_only=True)
            
        elif read_only is False:
            planning_rules = """
            PHASE 2: PLANNING
            You have already gathered the necessary context. Now, create a structured execution plan.
            - You can ONLY use MUTATION and MESSAGING tools.
            - Do not include retrieval tools in the final plan.
            - Use the context provided to inject real IDs and names into the parameters.
            """
            return base_rules + planning_rules + "\n" + registry.get_system_prompt_addition(read_only=False)

        return base_rules + "\n" + registry.get_system_prompt_addition()

    async def investigate(self, user_prompt: str, guild: discord.Guild, initial_context: str = "", on_step: Optional[Callable[[str], Any]] = None) -> str:
        """
        Runs an autonomous retrieval loop to gather context.
        on_step: Optional async callback function that takes a string status message.
        """
        self.logger.info("Starting investigation phase...")
        history = [
            {"role": "system", "content": self._get_system_prompt(read_only=True)},
            {"role": "user", "content": f"Initial Context:\n{initial_context}\n\nUser Request: {user_prompt}"}
        ]

        max_steps = 5

        for step in range(max_steps):
            self.logger.info(f"Investigation Step {step + 1}/{max_steps}...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                response_model=Union[InvestigationStep, InvestigationFinish],
                messages=history,
            )

            if isinstance(response, InvestigationFinish):
                self.logger.info(f"Investigation complete: {response.thought}")
                if on_step:
                    await on_step(f"✅ Investigation complete: {response.thought}")
                return response.final_context

            # Execute the read-only tool
            self.logger.info(f"AI Thinks: {response.thought}")
            self.logger.info(f"Calling tool: {response.action}")
            
            if on_step:
                await on_step(f"🔍 **Step {step + 1}:** {response.thought}\n*Calling tool: `{response.action}`*")
            
            tool = registry.get_tool(response.action)
            if not tool or not tool.read_only:
                result = f"Error: Tool '{response.action}' is not available or is not read-only."
            else:
                try:
                    result = await tool.execute(tool.schema(**response.parameters), guild)
                except Exception as e:
                    result = f"Error executing tool: {e}"

            self.logger.debug(f"Tool Result: {result}")
            
            history.append({"role": "assistant", "content": response.model_dump_json()})
            history.append({"role": "user", "content": f"Tool Result:\n{result}"})
            
        self.logger.warning("Investigation reached max steps.")
        return "Max investigation steps reached. Context might be incomplete."

    async def generate_plan(self, user_prompt: str, gathered_context: str) -> ExecutionPlan:
        self.logger.info("Generating final execution plan...")
        messages = [
            {"role": "system", "content": self._get_system_prompt(read_only=False)},
            {"role": "user", "content": f"Gathered Context:\n{gathered_context}\n\nUser Instruction: {user_prompt}"}
        ]

        try:
            plan = self.client.chat.completions.create(
                model=self.model,
                response_model=ExecutionPlan,
                messages=messages,
            )
            return plan
        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}")
            raise e

    async def refine_plan(self, original_plan: ExecutionPlan, suggestion: str, context: str = "") -> RevisedPlan:
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": f"Context:\n{context}\n\nCurrent Plan: {original_plan.model_dump_json()}\n\nSuggestion: {suggestion}\n\nUpdate the plan accordingly and provide an explanation."}
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
            params = tool.schema(**params)

        return await tool.execute(params, guild)
