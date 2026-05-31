from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal
from .shared import PermissionOverwrite

class CreateRoleParams(BaseModel):
    name: str
    color: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    mentionable: bool = False
    hoist: bool = False

class CreateCategoryParams(BaseModel):
    name: str
    overwrites: List[PermissionOverwrite] = Field(default_factory=list)

class CreateChannelParams(BaseModel):
    name: str
    channel_type: Literal["text", "voice", "stage", "forum"] = "text"
    category_name: Optional[str] = None
    topic: Optional[str] = None
    overwrites: List[PermissionOverwrite] = Field(default_factory=list)
    nsfw: bool = False
    thread_replies: bool = False

class DeleteParams(BaseModel):
    name_or_id: Union[str, int]
