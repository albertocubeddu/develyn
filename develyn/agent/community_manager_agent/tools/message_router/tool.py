from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.chains.llm import LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.prompts import ChatPromptTemplate
from langchain.tools import BaseTool
from langchain_core.messages import BaseMessage, HumanMessage,SystemMessage
from langchain_openai import ChatOpenAI
from develyn.agent.community_manager_agent.actions import Action
from develyn.agent.community_manager_agent.state import MessageRouterResponse
from typing import List, Optional
class MessageRouter(BaseTool):
    name: str = "MESSAGE_ROUTER"
    description: str = "This tool is used by Community Manager agent to tag a message and route it to correct channels and craft a response."
    llm: BaseLanguageModel
    return_direct: bool = True

    def __init__(self, *args, **kwargs):
        kwargs["llm"] = ChatOpenAI(
            temperature=0,
            model="gpt-4o-mini",
        )
        super().__init__(*args, **kwargs)
    
    def _run(
            self, message: str, tags: List[str], sub_tags: List[str],action: Action,
            run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        return MessageRouterResponse(
            message=message,
            tags=tags,
            sub_tags=sub_tags,
            action=action
        )
