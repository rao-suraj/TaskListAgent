from crewai.tools import BaseTool
from typing import Type, Any
from pydantic import BaseModel, Field

class HumanInteractionInput(BaseModel):
    """Input schema for HumanInteractionTool."""
    argument: str = Field(..., description="The question that you want to ask for the human or documents for which you want to get approval from the human.")

class HumanInteractionTool(BaseTool):
    name: str = "Human Interaction Tool"
    description: str = "This tool will help you to ask questions to the human or ask for approval for the documents. Send input as String and return human answers as String."
    args_schema: Type[BaseModel] = HumanInteractionInput
    
    # Define as a Pydantic field
    crew_service_instance: Any = Field(default=None, exclude=True, repr=False)
    
    def __init__(self, crew_service_instance=None, **kwargs):
        super().__init__(crew_service_instance=crew_service_instance, **kwargs)
    
    def _run(self, argument: str) -> str:
        if not self.crew_service_instance:
            raise ValueError("CrewService instance not provided")
            
        self.crew_service_instance.question_queue.put(argument)
        res = self.crew_service_instance.answer_queue.get()
        print(f"Human Interaction Tool: {res}")
        return res