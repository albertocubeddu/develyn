from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.chains.llm import LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.prompts import ChatPromptTemplate
from langchain.tools import BaseTool
from langchain_core.messages import BaseMessage, HumanMessage,SystemMessage
from langchain_openai import ChatOpenAI
from typing import List, Optional
from develyn.agent.qa_agent.tools.utils import fetch_docs
from develyn.agent.qa_agent.state import QAAgentResponseSchema
class FetchDocs(BaseTool):
    name: str = "FETCH_DOCS"
    description: str = "This tool is used to fetch the docs to answer a question."
    llm: BaseLanguageModel

    def __init__(self, *args, **kwargs):
        kwargs["llm"] = ChatOpenAI(
            temperature=0,
            model="gpt-4o-mini",
        )
        super().__init__(*args, **kwargs)
    
    def _run(
            self, url: str,run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        return fetch_docs(url)


class QAAgentResponse(BaseTool):
    name: str = "QA_AGENT_RESPONSE"
    description: str = "This tool is used by the QA Agent to craft a response in the correct format."
    llm: BaseLanguageModel
    return_direct: bool = True

    def __init__(self, *args, **kwargs):
        kwargs["llm"] = ChatOpenAI(
            temperature=0,
            model="gpt-4o-mini",
        )
        super().__init__(*args, **kwargs)
    
    def _run(
            self, message_reponse: str, is_possible: bool,
            run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        return QAAgentResponseSchema(
            message_reponse=message_reponse,
            is_possible=is_possible,
        )