import functools    
from typing import Dict, List

from develyn.agent.base import Agent, AgentName
from develyn.agent.community_manager_agent.prompt import CommunityManagerAgentPrompt
from develyn.agent.community_manager_agent.tools.message_router.tool import MessageRouter
from develyn.state import InboxState
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

class CommunityManagerAgent(Agent):
    llm: BaseChatModel= ChatOpenAI(
            temperature=0,
            model="gpt-4o-mini",
        )
    name: AgentName = AgentName.COMMUNITY_MANAGER_AGENT

    def __init__(self):
        tools = [MessageRouter()]
        self.agent = create_react_agent(self.llm, tools)
    
    def get_node(self):
        return functools.partial(self.agent_node, agent = self.agent, name = self.name)
    
    @staticmethod
    def agent_node(state: InboxState, agent: CompiledStateGraph, name: str) -> Dict:
        print(state)
        prompt = CommunityManagerAgentPrompt.format(
            company_name=state.persisted_state.company_name,
            company_description=state.persisted_state.company_description,
            tag_data=state.persisted_state.tag_data
        )
        system_message = SystemMessage(content=prompt)
        result = agent.invoke({
            "messages" : [system_message]+state.messages,
        })
        #print("Community Manager Agent result: ", result['messages'][-2])
        return{ 
            "messages" : [HumanMessage(content=result["messages"][-1].content, name = name)],
            "persisted_state": state.persisted_state,
            "next_step": AgentName.NONE
        }