import functools    
from typing import Dict, List

from develyn.agent.base import Agent, AgentName
from develyn.agent.qa_agent.prompt import QAAgentPrompt
from develyn.agent.qa_agent.tools.tool import FetchDocs, QAAgentResponse
from develyn.state import InboxState
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

class QAAgent(Agent):
    llm: BaseChatModel= ChatOpenAI(
            temperature=0,
            model="gpt-4o-mini",
        )
    name: AgentName = AgentName.QA_AGENT

    def __init__(self):
        tools = [FetchDocs(),QAAgentResponse()]
        self.agent = create_react_agent(self.llm, tools)
    
    def get_node(self):
        return functools.partial(self.agent_node, agent = self.agent, name = self.name)
    
    @staticmethod
    def agent_node(state: InboxState, agent: CompiledStateGraph, name: str) -> Dict:
        prompt = QAAgentPrompt.format(
            company_name=state.persisted_state.company_name,
            company_description=state.persisted_state.company_description,
            docs_url=state.persisted_state.docs_url,
            project_name=state.persisted_state.project_name
        )
        system_message = SystemMessage(content=prompt)
        result = agent.invoke({
            "messages" : [system_message]+state.messages,
        })
        #print("QA Agent result: ", result)
        return {
            "messages" : [HumanMessage(content=result["messages"][-1].content, name = name)],
            "persisted_state": state.persisted_state,
            "next_step": AgentName.NONE
        }