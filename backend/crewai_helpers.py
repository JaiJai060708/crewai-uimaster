from crewai import Agent, Task, Crew, Process

def run_crewai(process, agents, tasks, input_args):
    # Determine process type
    process_type = Process.sequential
    manager_llm = None
    if process.get('crew', {}).get('process') == 'hierarchical':
        process_type = Process.hierarchical
        manager_llm = 'gpt-4o'
    elif process.get('crew', {}).get('process') == 'parallel':
        process_type = Process.parallel

    # Create agents
    agents_data = []
    for agent_id, agent_info in agents.items():
        if agent_id in process.get('crew', {}).get('agents', []):
            agent = Agent(
                role=agent_info.get('role', ''),
                goal=agent_info.get('goal', ''),
                backstory=agent_info.get('backstory', ''),
                allow_delegation=agent_info.get('allow_delegation', False)
            )
            agents_data.append(agent)

    # Create tasks
    tasks_data = []
    for task_id, task_info in tasks.items():
        if task_id in process.get('crew', {}).get('tasks', []):
            description = task_info.get('description', '')
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
                    agent=agent
                )
                tasks_data.append(task)

    # Create Crew object
    crew = Crew(
        process=process_type,
        agents=agents_data,
        tasks=tasks_data,
        manager_llm=manager_llm,
        verbose=True  # Ensures detailed console output
    )

    return crew