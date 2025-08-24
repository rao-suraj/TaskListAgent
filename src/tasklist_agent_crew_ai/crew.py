from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from .callback_handler.agent_switch_handler import AgentSwitchHandler
from .tools.human_interacton_tool import HumanInteractionTool
from .tools.tavity_search_tool import TavilySearchTool      # assembles handlers into a single manager :contentReference[oaicite:1]{index=1}
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

@CrewBase
class TasklistAgentCrewAi():

	"""TasklistAgentCrewAi crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	def __init__(self):
		super().__init__()

        # Create knowledge source with dynamic API key
		self.text_source = TextFileKnowledgeSource(
            file_paths=["examples.txt"]
        )


	@agent
	def business_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['business_analyst'],
			verbose=True,
			multimodal=True,
			tools=[HumanInteractionTool(),TavilySearchTool()]
		)

	@agent
	def developer(self) -> Agent:
		return Agent(
			config=self.agents_config['developer'],
			verbose=True,
			tools=[HumanInteractionTool(),TavilySearchTool()]
		)	
	
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
			tools=[HumanInteractionTool(),TavilySearchTool()]
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
			task_callback=AgentSwitchHandler().task_callback
		)