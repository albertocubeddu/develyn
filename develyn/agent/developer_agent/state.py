from langchain_core.pydantic_v1 import BaseModel, Field

class CodeGeneration(BaseModel):
    """Code output"""

    prefix: str = Field(description="Description of the problem and approach")
    imports: str = Field(description="Code block import statements")
    code: str = Field(description="Code block not including import statements")

class DeveloperAgentResponseSchema(BaseModel):
    """The structure of a QA Agent's response"""
    code: str = Field(description="The entire python code ")
    num_tries: int = Field(description="Number of tries to solve the problem")
    has_errors: bool = Field(description="Does the file code file still have any errors?")
    description = "Schema for QA Agent's response."