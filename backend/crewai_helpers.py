from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from human_input_tool import HumanInputTool 

def run_crewai(process, agents, tasks, input_args, log_queue):
    # Get the model for the crew
    model_crew = process.get('crew', {}).get('model', 'gpt-4o')
    
    # Determine process type
    process_type = Process.sequential
    manager_llm = None
    if process.get('crew', {}).get('process') == 'hierarchical':
        process_type = Process.hierarchical
        manager_llm = model_crew
    elif process.get('crew', {}).get('process') == 'parallel':
        process_type = Process.parallel

    # Determine if planning is allowed
    allow_planning = False
    if process.get('crew', {}).get('planning') == True:
        allow_planning = True

    # Create agents
    agents_data = []
    for agent_id, agent_info in agents.items():
        if agent_id in process.get('crew', {}).get('agents', []):
            tools = []
            if agent_info.get('tools', []):
                for tool in agent_info.get('tools', []):
                    if tool == 'SerperDevTool':
                        tools.append(SerperDevTool())
                    elif tool == 'ScrapeWebsiteTool':
                        tools.append(ScrapeWebsiteTool())
                    elif tool == 'HumanInputTool':
                        tools.append(HumanInputTool(log_queue))  

            agent = Agent(
                role=agent_info.get('role', ''),
                goal=agent_info.get('goal', ''),
                backstory=agent_info.get('backstory', ''),
                allow_delegation=agent_info.get('allow_delegation', False),
                tools=tools,
                llm=agent_info.get('llm_model', 'gpt-4o-mini')
            )
            agents_data.append(agent)

    # Create tasks
    tasks_data = []
    for task_id, task_info in tasks.items():
        if task_id in process.get('crew', {}).get('tasks', []):
            description = task_info.get('description', '')
            max_retries = task_info.get('max_iterations', 2)
            if description:
                try:
                    description = description.format(**input_args)
                except KeyError as e:
                    return {"error": f"Missing input argument: {e.args[0]}"}

            agent = None
            agent_id = task_info.get('agents')
            for a in agents_data:
                if a.role.strip() == agents.get(agent_id, {}).get('role', '').strip():
                    agent = a
                    break

            if agent:
                task = Task(
                    description=description,
                    expected_output=task_info.get('expected_output', ''),
                    max_iterations=max_retries,
                    agent=agent
                )
                tasks_data.append(task)

    # Create Crew object
    crew = Crew(
        process=process_type,
        agents=agents_data,
        tasks=tasks_data,
        manager_llm=manager_llm,
        verbose=True,
        planning=allow_planning,
        planning_llm=model_crew
    )

    return crew