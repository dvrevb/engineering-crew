from crewai import Agent, Crew, Process, Task
from crewai_tools import FileWriterTool
from crewai.project import CrewBase, agent, crew, task



@CrewBase
class SoftwareEngineeringCrew:
    """
    A multi-agent software engineering crew that takes requirements
    and produces architecture, backend, frontend, and test code.
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # Agents

    @agent
    def engineering_lead(self) -> Agent:
        return Agent(
            config=self.agents_config["engineering_lead"]
        )

    @agent
    def engineering_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["engineering_manager"]
        )

    @agent
    def backend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["backend_engineer"],
            tools=[FileWriterTool()]
        )

    @agent
    def frontend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["frontend_engineer"],
            tools=[FileWriterTool()]
        )

    @agent
    def test_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["test_engineer"],
            tools=[FileWriterTool()]
        )

    # Tasks

    @task
    def design_architecture(self) -> Task:
        return Task(
            config=self.tasks_config["design_architecture"],
        )

    @task
    def create_execution_plan(self) -> Task:
        return Task(
            config=self.tasks_config["create_execution_plan"],
        )

    @task
    def implement_backend(self) -> Task:
        return Task(
            config=self.tasks_config["implement_backend"],
        )

    @task
    def implement_frontend(self) -> Task:
        return Task(
            config=self.tasks_config["implement_frontend"],
        )

    @task
    def write_tests(self) -> Task:
        return Task(
            config=self.tasks_config["write_tests"],
        )

    # Crew

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  
            tasks=self.tasks,     
            process=Process.sequential,
            verbose=True,
            memory=False
        )