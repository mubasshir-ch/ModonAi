from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal, Dict
from .shared import PermissionOverwrite
from .actions import CreateRoleParams, CreateCategoryParams, CreateChannelParams, DeleteParams

class Task(BaseModel):
    order: int
    action: Literal["create_role", "create_category", "create_channel", "delete_channel", "delete_role", "assign_role", "remove_role"]
    description: str = Field(..., description="A short, human-readable description of what this task does.")
    parameters: Union[CreateRoleParams, CreateCategoryParams, CreateChannelParams, DeleteParams, Dict] = Field(
        ..., 
        description="Action-specific parameters. MUST be nested inside this dictionary."
    )

class ExecutionPlan(BaseModel):
    summary: str = Field(..., description="A concise summary of the entire plan.")
    tasks: List[Task] = Field(..., description="A list of tasks ordered by their execution sequence.")
