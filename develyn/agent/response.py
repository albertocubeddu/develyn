from langchain.pydantic_v1 import BaseModel, Field
from typing import List, Optional
from develyn.agent.actions import Action

class DevRelOutput(BaseModel):
    action: Action = Field(description="The action to take", default=None)
    message: Optional[str] = Field(description="The message to send", default="")
    detected_tags: Optional[List[str]] = Field(description="The tags detected in the message", default=[])
    detected_sub_tags: Optional[List[str]] = Field(description="The sub-tags detected in the message", default=[])