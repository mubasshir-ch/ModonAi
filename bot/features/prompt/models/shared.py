from pydantic import BaseModel, Field
from typing import List, Literal

class PermissionOverwrite(BaseModel):
    target_type: Literal["role", "member", "everyone"]
    target_name: str
    allow: List[str] = Field(default_factory=list)
    deny: List[str] = Field(default_factory=list)
