from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from tasklist_agent_crew_ai.tools.human_interacton_tool import HumanInteractionTool
from tasklist_agent_crew_ai.tools.tavity_search_tool import TavilySearchTool
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

text_source = TextFileKnowledgeSource(
    file_paths=["examples.txt"]
)

@CrewBase
class TasklistAgentCrewAi():
	"""TasklistAgentCrewAi crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def business_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['business_analyst'],
			verbose=True,
			multimodal=True,
			tools=[HumanInteractionTool(),TavilySearchTool()],
		)

	@agent
	def developer(self) -> Agent:
		return Agent(
			config=self.agents_config['developer'],
			verbose=True,
			tools=[TavilySearchTool()],
		)
	
	@agent
	def project_manager(self) -> Agent:
		return Agent(
			config=self.agents_config['project_manager'],
			verbose=True,
			knowledge_sources=[text_source],
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
