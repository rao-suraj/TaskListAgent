from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
from tavily import TavilyClient
import os

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

class TavilySearchInput(BaseModel):
    """Input schema for TavilySearchInput."""
    query: str = Field(..., description="The search query in string format")

class TavilySearchTool(BaseTool):
    name: str = "Tavily Search Tool"
    description: str = "Use this tool to search the web for current information. Input should be a specific search query. Example: query='latest news on AI'"
    args_schema: Type[BaseModel] = TavilySearchInput

    def _run(self, query: Optional[str] = None) -> str:
        try:
            # Validate input
            if not query or not isinstance(query, str):
                return "Error: Please provide a valid search query as a string."
                
            tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
            response = tavily_client.search(query=query,include_answer='advanced')
            return response
        except Exception as e:
            return f"Error performing Tavily search: {str(e)}"