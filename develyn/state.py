from langchain.pydantic_v1 import BaseModel
from typing import Annotated, List, Optional
from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage
from develyn.agent.base import AgentName

class PersistedState(BaseModel):
    company_name: str
    company_description: str
    project_name: str
    tag_data: str
    docs_url: List[str]

class InboxState(BaseModel):
    messages: Annotated[List[AnyMessage], add_messages]
    persisted_state: PersistedState
    next_step: Optional[AgentName] = AgentName.NONE