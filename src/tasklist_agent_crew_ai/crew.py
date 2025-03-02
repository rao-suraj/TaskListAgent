from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource

import os
API_KEY = os.environ.get("GOOGLE_API_KEY")

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

# class HumanTool(BaseTool):
#     name: str = "Human interact"
#     description: str = (
#         "Fazer perguntas ao usuário para coletar informações"
#     )

#     def _run(self, argument: str) -> str:
#         # Implementation goes here
#         print(argument)
#         res = input(f"{argument} \n")
#         return res

text_source = TextFileKnowledgeSource(
    file_paths=["examples.txt"]
)

class HumanInteractionInput(BaseModel):
    """Input schema for HumanInteractionTool."""
    argument: str = Field(..., description="The question that you want to ask for the human.")

class HumanInteractionTool(BaseTool):
    name: str = "Human Interaction Tool"
    description: str = "This tool will help you to ask questions to the user. I task questions as String and return human answers as String."
    args_schema: Type[BaseModel] = HumanInteractionInput

    def _run(self, argument: str) -> str:
        res = input(f"{argument} \n")
        return res

@CrewBase
class TasklistAgentCrewAi():
	"""TasklistAgentCrewAi crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def business_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['business_analyst'],
			verbose=True,
		)

	@agent
	def developer(self) -> Agent:
		return Agent(
			config=self.agents_config['developer'],
			verbose=True
		)
	
	@agent
	def project_manager(self) -> Agent:
		return Agent(
			config=self.agents_config['project_manager'],
			verbose=True,
			knowledge_sources=[text_source],
			# knowledge= {
			# 	"collection_name": "crew_knowledge",
			# 	"sources":[text_source]
			# },
			embedder =dict(
                provider="google", # or google, openai, anthropic, 
                config=dict(
                    model="models/text-embedding-004", 
					api_key = API_KEY,
                ),
            ),
		)

	# @agent
	# def about_user_agent(self) -> Agent:
	# 	return Agent(
	# 		config=self.agents_config['about_user_agent'],
	# 		verbose=True,
	# 		knowledge_sources=[text_source],
	# 		embedder = dict(
    #         	provider="google", # or google, openai, anthropic, 
    #             config=dict(
    #                 model="models/text-embedding-004", 
	# 				api_key = API_KEY,
    #             ),
    #         ),
	# 	)
	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def requirement_generation_task(self) -> Task:
		return Task(
			config=self.tasks_config['requirement_generation_task'],
			tools=[HumanInteractionTool()],
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
	
	# @task
	# def respond_to_user_query(self) -> Task:
	# 	return Task(
	# 		config=self.tasks_config['respond_to_user_query_task'],
	# 	)

	@crew
	def crew(self) -> Crew:
		"""Creates the TasklistAgentCrewAi crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks= self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
		)
