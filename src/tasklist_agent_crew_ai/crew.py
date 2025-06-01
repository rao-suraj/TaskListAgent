from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from tasklist_agent_crew_ai.tools.human_interacton_tool import HumanInteractionTool
from tasklist_agent_crew_ai.tools.tavity_search_tool import TavilySearchTool
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

@CrewBase
class TasklistAgentCrewAi():

	"""TasklistAgentCrewAi crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	def __init__(self, google_api_key, tavily_api_key=None):
		super().__init__()
		os.environ['GEMINI_API_KEY'] = google_api_key
		if tavily_api_key is not None:
			os.environ['TAVILY_API_KEY'] = tavily_api_key
		self.tavily_api_key = tavily_api_key
        
        # Create knowledge source with dynamic API key
		self.text_source = TextFileKnowledgeSource(
            file_paths=["examples.txt"]
        )

	@agent
	def business_analyst(self) -> Agent:
		agent = Agent(
			config=self.agents_config['business_analyst'],
			verbose=True,
			multimodal=True,
		)
		if self.tavily_api_key is not None:
			agent.tools = [HumanInteractionTool(),TavilySearchTool()]
		else:
			agent.tools = [HumanInteractionTool()]
		return agent

	@agent
	def developer(self) -> Agent:
		agent = Agent(
			config=self.agents_config['developer'],
			verbose=True,
		)
		if self.tavily_api_key is not None:
			agent.tools = [TavilySearchTool()]
		return agent		
	
	@agent
	def project_manager(self) -> Agent:
		return Agent(
			config=self.agents_config['project_manager'],
			verbose=True,
			knowledge_sources=[self.text_source],
			embedder =dict(
                provider="google", 
                config=dict(
                    model="models/text-embedding-004", 
					api_key = GOOGLE_API_KEY,
                ),
            ),
		)

	@task
	def requirement_generation_task(self) -> Task:
		return Task(
			config=self.tasks_config['requirement_generation_task'],
		)

	@task
	def execution_plannig_task(self) -> Task:
		return Task(
			config=self.tasks_config['execution_plannig_task'],
		)
	
	@task
	def task_list_creation_task(self) -> Task:
		return Task(
			config=self.tasks_config['task_list_creation_task'],
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the TasklistAgentCrewAi crew"""

		return Crew(
			agents=self.agents, 
			tasks= self.tasks,
			process=Process.sequential,
			verbose=True,
		)
