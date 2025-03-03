from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class HumanInteractionInput(BaseModel):
    """Input schema for HumanInteractionTool."""
    argument: str = Field(..., description="The question that you want to ask for the human or documents for which you want to get approval from the human.")

class HumanInteractionTool(BaseTool):
    name: str = "Human Interaction Tool"
    description: str = "This tool will help you to ask questions to the human or ask for approval for the documents .Send input as String and return human answers as String."
    args_schema: Type[BaseModel] = HumanInteractionInput

    def _run(self, argument: str) -> str:
        res = input(f"{argument} \n")
        return res