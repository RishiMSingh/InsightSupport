# crew.py

import warnings
warnings.filterwarnings('ignore')
from langchain_openai import ChatOpenAI
import os
import yaml
from crewai import Agent, Task, Crew
from crewai_tools import FileReadTool


# === Load YAML Configurations ===
def load_configs():
    config_paths = {
        'agents': 'config/agents.yaml',
        'tasks': 'config/tasks.yaml'
    }

    configs = {}
    for config_type, file_path in config_paths.items():
        with open(file_path, 'r') as file:
            configs[config_type] = yaml.safe_load(file)

    return configs['agents'], configs['tasks']


# === Create and Return a Crew ===
def create_crew_with_file(file_path, openai_api_key):

    llm = ChatOpenAI(
        model="gpt-4",  # or "gpt-3.5-turbo"
        temperature=0.3,
        openai_api_key=openai_api_key
    )
    agents_config, tasks_config = load_configs()

    # Shared tool for agents working with CSV
    csv_tool = FileReadTool(file_path=file_path)

    # === Define Agents ===
    suggestion_generation_agent = Agent(
        config=agents_config['suggestion_generation_agent'],
        tools=[csv_tool],
        llm=llm
    )

    reporting_agent = Agent(
        config=agents_config['reporting_agent'],
        tools=[csv_tool],
        llm=llm
    )

    chart_generation_agent = Agent(
        config=agents_config['chart_generation_agent'],
        tools=[],  # No CSV tool needed, uses context
        allow_code_execution=False,
        llm=llm
    )

    # === Define Tasks ===
    suggestion_generation = Task(
        config=tasks_config['suggestion_generation'],
        agent=suggestion_generation_agent
    )

    table_generation = Task(
        config=tasks_config['table_generation'],
        agent=reporting_agent
    )

    chart_generation = Task(
        config=tasks_config['chart_generation'],
        agent=chart_generation_agent
    )

    final_report_assembly = Task(
        config=tasks_config['final_report_assembly'],
        agent=reporting_agent,
        context=[
            suggestion_generation,
            table_generation,
            chart_generation
        ]
    )

    # === Define Crew ===
    support_report_crew = Crew(
        agents=[
            suggestion_generation_agent,
            reporting_agent,
            chart_generation_agent
        ],
        tasks=[
            suggestion_generation,
            table_generation,
            chart_generation,
            final_report_assembly
        ],
        verbose=True,
        full_output=True,
        memory=False  # You can change this if agent memory is needed
    )

    return support_report_crew
