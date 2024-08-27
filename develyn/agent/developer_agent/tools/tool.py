from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.chains.llm import LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.prompts import ChatPromptTemplate
from langchain.tools import BaseTool
from langchain_core.messages import BaseMessage, HumanMessage,SystemMessage
from langchain_openai import ChatOpenAI
from typing import List, Optional
from develyn.agent.developer_agent.state import CodeGeneration, DeveloperAgentResponseSchema
class CheckCode(BaseTool):
    name: str = "CHECK_CODE"
    description: str = "This tool is used to check if the code executes properly."
    llm: BaseLanguageModel

    def __init__(self, *args, **kwargs):
        kwargs["llm"] = ChatOpenAI(
            temperature=0,
            model="gpt-4o-mini",
        )
        super().__init__(*args, **kwargs)
    
    def _run(
            self,code_generated:CodeGeneration , run_manager: Optional[CallbackManagerForToolRun] = None,**kwargs) -> str:
        print("---CHECKING CODE---")
        print(code_generated)
        # Get solution components
        imports = code_generated['imports']
        print(imports)
        code = code_generated['code']

        # Check imports
        try:
            exec(imports)
        except Exception as e:
            print("---CODE IMPORT CHECK: FAILED---")
            return f"Your solution failed the import test: {e}"

        # Check execution
        try:
            exec(imports + "\n" + code)
        except Exception as e:
            print("---CODE BLOCK CHECK: FAILED---")
            return f"Your solution failed the code execution test: {e}"

        # No errors
        print("---NO CODE TEST FAILURES---")
        return f"Your solution passed both import and code execution tests! No error"
        
class DeveloperAgentResponse(BaseTool):
    name: str = "DEVELOPER_AGENT_RESPONSE"
    description: str = "This tool is used by the Developer Agent to craft a response in the correct format."
    llm: BaseLanguageModel
    return_direct: bool = True

    def __init__(self, *args, **kwargs):
        kwargs["llm"] = ChatOpenAI(
            temperature=0,
            model="gpt-4o-mini",
        )
        super().__init__(*args, **kwargs)
    
    def _run(
            self, code: str, num_tries: int, has_errors: bool,
            run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        return DeveloperAgentResponseSchema(
            code=code,
            num_tries=num_tries,
            has_errors=has_errors,
        )