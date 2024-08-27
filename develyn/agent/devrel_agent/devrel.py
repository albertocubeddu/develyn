import functools
from typing import Dict

from langchain_openai import ChatOpenAI
from develyn.agent.base import AgentName
from develyn.agent.devrel_agent.prompt import DEVREL_PROMPT
from develyn.state import InboxState
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel

class DevRelAgentResponses(BaseModel):
    "Give the reasoning and then the agent name"
    reasoning: str
    agent_name: AgentName

class DevrelAgent:
    name: str = "Develyn"

    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-4o-mini",
        ).with_structured_output(DevRelAgentResponses)

    def get_node(self):
        return functools.partial(self.agent_node, llm=self.llm, name=self.name)
    
    @staticmethod
    def agent_node(state: InboxState, llm: BaseChatModel, name: str) -> Dict:
        system_message = SystemMessage(content=DEVREL_PROMPT)
        result = llm.invoke([system_message] + state.messages)
        print(result)
        return {
            "next_step": result.agent_name
        }