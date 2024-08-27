from langchain_core.pydantic_v1 import BaseModel, Field
from develyn.agent.community_manager_agent.actions import Action
from typing import List, Optional
class MessageRouterResponse(BaseModel):
    """The structure of a message router response"""
    message: str = Field(description="The response message to send as a Community Manager to the user")
    tags: List[Optional[str]] = Field(description="The tags to send")
    sub_tags: List[Optional[str]] = Field(description="The sub tags to send")
    action: Action = Field(description="The action to take")
    description = "Schema for message router responses."