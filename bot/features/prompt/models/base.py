from pydantic import BaseModel, Field
from typing import List, Union, Dict, Any, Optional, Literal
from ..mcp import registry

# Extract all tool schemas to build the union for tool_call parameters
tool_schemas = tuple(tool.schema for tool in registry.get_all_tools())
ParamsUnion = Union[*tool_schemas] if tool_schemas else Dict[str, Any]

class ChecklistTask(BaseModel):
    id: int
    description: str = Field(..., description="High-level objective description.")
    status: Literal["pending", "done", "failed", "skipped"] = "pending"

class BroadPlan(BaseModel):
    summary: str = Field(..., description="Concise summary of the proposed mission.")
    tasks: List[ChecklistTask] = Field(..., description="Initial list of high-level objectives.")

class RevisedBroadPlan(BaseModel):
    explanation: str = Field(..., description="Why the plan was changed based on user feedback.")
    plan: BroadPlan

class AgentToolCall(BaseModel):
    action: str = Field(..., description="The name of the MCP tool to call.")
    parameters: ParamsUnion = Field(..., description="Parameters matching the tool's schema.")

class AgentStepResponse(BaseModel):
    thought: str = Field(..., description="Internal reasoning about current progress and next steps.")
    tool_call: Optional[AgentToolCall] = Field(None, description="The tool the AI wants to execute now.")
    updated_checklist: List[ChecklistTask] = Field(..., description="The complete, updated list of mission objectives.")
    is_goal_reached: bool = Field(False, description="Set to true if all objectives are completed.")
    final_summary: Optional[str] = Field(None, description="Required when is_goal_reached is True.")

# Force rebuild to resolve any late-binding issues
ChecklistTask.model_rebuild()
BroadPlan.model_rebuild()
RevisedBroadPlan.model_rebuild()
AgentToolCall.model_rebuild()
AgentStepResponse.model_rebuild()
