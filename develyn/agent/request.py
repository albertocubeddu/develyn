from langchain.pydantic_v1 import BaseModel, Field
from typing import List, Optional

class DevRelInput(BaseModel):
    tag: str = Field(description="The tag detected in the message")
    sub_tags: List[str] = Field(description="The sub tags detected in the message", default=[])
    message: str = Field(description="The message from the user", default="")