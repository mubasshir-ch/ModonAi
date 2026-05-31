from pydantic import BaseModel, Field
from typing import List, Union, Dict, Any
from ..mcp import registry

# Extract all tool schemas to build the union for Task parameters
tool_schemas = tuple(tool.schema for tool in registry.get_all_tools())
ParamsUnion = Union[*tool_schemas] if tool_schemas else Dict[str, Any]

class Task(BaseModel):
    order: int
    action: str = Field(..., description="The name of the action to perform.")
    description: str = Field(..., description="A short, human-readable description of what this task does.")
    parameters: ParamsUnion = Field(
        ..., 
        description="Action-specific parameters. MUST be nested inside this dictionary and match the schema for the chosen action."
    )

class ExecutionPlan(BaseModel):
    summary: str = Field(..., description="A concise summary of the entire plan.")
    tasks: List[Task] = Field(..., description="A list of tasks ordered by their execution sequence.")

class RevisedPlan(BaseModel):
    explanation: str = Field(..., description="Explanation of how the user's suggestions were incorporated or answers to their questions.")
    plan: ExecutionPlan
