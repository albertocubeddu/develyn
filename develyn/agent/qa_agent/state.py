from langchain_core.pydantic_v1 import BaseModel, Field
from develyn.agent.community_manager_agent.actions import Action
from typing import List, Optional
class QAAgentResponseSchema(BaseModel):
    """The structure of a QA Agent's response"""
    message_reponse: str = Field(description="The response message to send with technical details")
    is_possible:bool = Field(description="Is it possible to perform the task using the project")
    description = "Schema for QA Agent's response."