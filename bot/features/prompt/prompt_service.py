import os
import discord
import instructor
import logging
import litellm
from litellm import completion
from typing import List, Optional, Union, Dict, Any, Callable
from .models.base import BroadPlan, RevisedBroadPlan, ChecklistTask, AgentStepResponse
from .mcp import registry

class PromptService:
    def __init__(self, model: str = None):
        self.model = model or os.getenv("LLM_MODEL", "vertex_ai/gemini-2.0-flash-exp")
        
        # Determine the correct API key/auth based on the provider
        if self.model.startswith("gemini/"):
            self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
            if self.api_key:
                os.environ["GEMINI_API_KEY"] = self.api_key
        elif self.model.startswith("vertex_ai/"):
            # Vertex AI uses GOOGLE_APPLICATION_CREDENTIALS or gcloud auth, no explicit API key needed
            self.api_key = None 
        else:
            self.api_key = os.getenv("GITHUB_API_KEY") or os.getenv("LLM_API_KEY")
            if self.api_key:
                os.environ["GITHUB_API_KEY"] = self.api_key
        
        self.logger = logging.getLogger("modonai.prompt_service")

        if os.getenv("LITELLM_DEBUG") == "True":
            litellm._turn_on_debug()
        
        self.client = instructor.from_litellm(completion)
        self.logger.info(f"PromptService initialized with model: {self.model}")

    def _get_agent_system_prompt(self) -> str:
        return f"""
        You are ModonAi, a professional Discord server administrator agent.
        Your goal is to execute a mission described by the user.

        MISSION MANAGEMENT:
        - You maintain a dynamic Checklist of high-level objectives.
        - Every step, you must update the status of your objectives (pending/done/failed).
        - A task is ONLY 'done' if you have successfully executed the tool required for it.

        REASONING & EXECUTION:
        1. Public Thoughts: Your `thought` field is visible to the user as a status update. Use it to explain your reasoning and progress.
        2. Action vs. Thought: Thinking about an action (e.g., "I will now send a message") is NOT the same as performing it. To actually perform an action, you MUST use `tool_call`.
        3. No Repetition: Do not repeat the same thought or reasoning. Each step must progress the mission.
        4. Tool Usage: Use retrieval tools to gather data, mutation tools to change the server, and messaging tools (`send_message`, `send_embed_message`) to provide final answers or complex reports.
        5. Stop Condition: Set `is_goal_reached` to True only when the entire checklist is complete and the user has been fully informed of the results.

        {registry.get_system_prompt_addition()}
        """

    async def generate_broad_plan(self, user_prompt: str, context: str = "") -> BroadPlan:
        """Initial high-level goal setting."""
        self.logger.info("Generating broad plan...")
        messages = [
            {"role": "system", "content": "You are a strategic planner. Break down the user's request into high-level objectives. Do not decide on tool parameters yet."},
            {"role": "user", "content": f"Context:\n{context}\n\nRequest: {user_prompt}"}
        ]
        return self.client.chat.completions.create(
            model=self.model,
            response_model=BroadPlan,
            messages=messages,
        )

    async def refine_broad_plan(self, original_plan: BroadPlan, suggestion: str, context: str = "") -> RevisedBroadPlan:
        """Refines the objectives based on user feedback."""
        messages = [
            {"role": "system", "content": "Update the mission objectives based on user feedback."},
            {"role": "user", "content": f"Context:\n{context}\n\nCurrent Objectives: {original_plan.model_dump_json()}\n\nSuggestion: {suggestion}"}
        ]
        return self.client.chat.completions.create(
            model=self.model,
            response_model=RevisedBroadPlan,
            messages=messages,
        )

    async def run_agent_step(self, user_prompt: str, history: List[Dict], context: str) -> AgentStepResponse:
        """A single step in the agentic execution loop."""
        full_history = [
            {"role": "system", "content": self._get_agent_system_prompt()},
            {"role": "user", "content": f"Initial Request: {user_prompt}\n\nCurrent Context: {context}"}
        ] + history

        return self.client.chat.completions.create(
            model=self.model,
            response_model=AgentStepResponse,
            messages=full_history,
        )

    async def execute_tool(self, action: str, parameters: Any, guild: discord.Guild) -> Any:
        """Executes any MCP tool."""
        tool = registry.get_tool(action)
        if not tool:
            return f"Error: Tool '{action}' is not registered."
        
        try:
            # Instructor might have already instantiated the specific model
            if isinstance(parameters, tool.schema):
                params_obj = parameters
            elif isinstance(parameters, dict):
                params_obj = tool.schema(**parameters)
            else:
                # Fallback: try to convert to dict first if it's some other Pydantic model
                data = parameters.model_dump() if hasattr(parameters, "model_dump") else parameters
                params_obj = tool.schema(**data)

            return await tool.execute(params_obj, guild)
        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
            return f"Error executing tool {action}: {str(e)[:1900]}"
