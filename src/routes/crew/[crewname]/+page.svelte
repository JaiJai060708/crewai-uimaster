<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  
  let crew = {
    name: $page.params.crewname,
    process: {},
    agents: {},
    tasks: {}
  };
  let loading = true;
  let error = null;
  let errorTimeout;
  
  // New variables for forms
  let showAgentForm = false;
  let showTaskForm = false;
  let newAgentName = '';
  let newTaskName = '';
  let formSubmitting = false;
  let successMessage = null;
  
  // Function to delete the crew
  let showDeleteConfirmation = false;
  let deleteInProgress = false;
  
  // Fetch crew data
  async function fetchCrewData() {
    loading = true;
    error = null;
    
    try {
      // Fetch process information
      const processResponse = await fetch(`/api/crew/${crew.name}/process`);
      if (!processResponse.ok) throw new Error('Failed to fetch crew process');
      const processData = await processResponse.json();
      crew.process = processData.process;
      
      // Fetch agents information
      const agentsResponse = await fetch(`/api/crew/${crew.name}/agents`);
      if (!agentsResponse.ok) throw new Error('Failed to fetch crew agents');
      const agentsData = await agentsResponse.json();
      crew.agents = agentsData.agents;
      
      // Fetch tasks information
      const tasksResponse = await fetch(`/api/crew/${crew.name}/tasks`);
      if (!tasksResponse.ok) throw new Error('Failed to fetch crew tasks');
      const tasksData = await tasksResponse.json();
      crew.tasks = tasksData.tasks;
      
    } catch (err) {
      error = err.message;
      console.error('Error fetching crew data:', err);
    } finally {
      loading = false;
    }
  }
  
  // Function to clear error after timeout
  function setError(message) {
    clearTimeout(errorTimeout);
    error = message;
    
    if (error) {
      errorTimeout = setTimeout(() => {
        error = null;
      }, 3000);
    }
  }
  
  // Create new agent
  async function createAgent(event) {
    event.preventDefault();
    
    // Validate agent name format - only allow letters, numbers, and underscores
    if (!/^[a-zA-Z0-9_]+$/.test(newAgentName)) {
      setError("Agent name can only contain letters, numbers, and underscores (_)");
      formSubmitting = false;
      return;
    }
    
    // Check if an agent with the same name already exists in this crew
    if (crew.agents && Object.keys(crew.agents).includes(newAgentName)) {
      setError(`An agent named "${newAgentName}" already exists in this crew`);
      formSubmitting = false;
      return;
    }
    
    formSubmitting = true;
      
    // Navigate to the agent detail page
    goto(`/crew/${crew.name}/taskagent/${newAgentName}`);
      
  }
  
  // Create new task
  async function createTask(event) {
    event.preventDefault();
    
    // Validate task name format - only allow letters, numbers, and underscores
    if (!/^[a-zA-Z0-9_]+$/.test(newTaskName)) {
      setError("Task name can only contain letters, numbers, and underscores (_)");
      formSubmitting = false;
      return;
    }
    
    formSubmitting = true;
    
    try {
      // Prepare the data - just create with empty details
      const currentTasks = { ...crew.tasks };
      currentTasks[newTaskName] = {};
      
      // Use the existing PUT endpoint
      const response = await fetch(`/api/crew/${crew.name}/tasks`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tasks: currentTasks
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to create task');
      }
      
      // Navigate to the task detail page
      goto(`/crew/${crew.name}/task/${newTaskName}`);
      
    } catch (err) {
      setError(err.message);
      console.error('Error creating task:', err);
      formSubmitting = false;
      showTaskForm = false;
    }
  }
  
  // Function to delete the crew
  async function deleteCrew() {
    deleteInProgress = true;
    setError(null);
    
    try {
      const response = await fetch(`/api/crew/${crew.name}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete crew');
      }
      
      // Navigate back to the crews list
      goto('/');
      
    } catch (err) {
      setError(err.message);
      console.error('Error deleting crew:', err);
      deleteInProgress = false;
      showDeleteConfirmation = false;
    }
  }
  
  onMount(fetchCrewData);
  
  // Cleanup on component destruction
  onMount(() => {
    fetchCrewData();
    
    return () => {
      clearTimeout(errorTimeout);
    };
  });
</script>

<main class="container">
  <!-- Move the error alert outside main container so it's fixed at the top -->
  {#if error}
    <div class="alert-fixed">
      <div class="alert">
        <p>{error}</p>
        <button class="alert-dismiss" on:click={() => setError(null)}>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </div>
  {/if}
  
  <header class="crew-header">
    <a href="/" class="back-link">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="19" y1="12" x2="5" y2="12"></line>
        <polyline points="12 19 5 12 12 5"></polyline>
      </svg>
      Back to Crews
    </a>
    <h1>{crew.name}</h1>
    <button class="delete-crew-button" on:click={() => showDeleteConfirmation = true}>
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="3 6 5 6 21 6"></polyline>
        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
        <line x1="10" y1="11" x2="10" y2="17"></line>
        <line x1="14" y1="11" x2="14" y2="17"></line>
      </svg>
      Delete Crew
    </button>
  </header>
  
  {#if loading}
    <div class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading crew data...</p>
    </div>
  {:else}
    <section class="workflow-section">
      <div class="section-header">
        <h2>Team Structure</h2>
        <div class="header-actions">
          <a href="/crew/{crew.name}/process" class="edit-button">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
            Edit Team Structure
          </a>
          <button class="add-button professional" on:click={() => showAgentForm = true}>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            Add Agent
          </button>
        </div>
      </div>
      
      {#if crew.process?.crew?.process?.toLowerCase() === 'sequential'}
        <div class="sequential-workflow">
          {#if crew.agents && Object.keys(crew.agents).length > 0}
          {#if crew.process?.crew?.agents && crew.process?.crew?.agents.length > 0}
            <div class="process-description">
              <p>
                <span class="process-tag">Sequential Process:</span> 
                Agents work in order, passing results from one to the next
              </p>
            </div>
            <div class="sequential-chart">
              {#each crew.process.crew.agents as agentName, index}
                <div class="agent-node" class:highlighted={index === 0} on:click={() => goto(`/crew/${crew.name}/taskagent/${agentName}`)}>
                  <div class="step-number">{index + 1}</div>
                  <div class="agent-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                      <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                  </div>
                  <div class="agent-name" title={agentName}>{agentName}</div>
                  
                  <!-- Add delegation indicator badge if agent can delegate -->
                  {#if crew.agents[agentName]?.allow_delegation}
                    <div class="delegation-badge" title="Can delegate to previous agents">
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                      </svg>
                      <span>Delegator</span>
                    </div>
                    
                    <!-- Show delegation arrows to previous agents -->
                    {#if index > 0}
                      <div class="delegation-arrows sequential">
                        {#each Array(index) as _, i}
                          <div class="delegation-arrow" style="--arrow-distance: {(index - i) * 20}px">
                            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                              <path d="M7 13l5 5 5-5M7 6l5 5 5-5"/>
                            </svg>
                          </div>
                        {/each}
                      </div>
                    {/if}
                  {/if}
                  
                  <!-- Add associated tasks display -->
                  <div class="agent-tasks">
                    {#each Object.entries(crew.tasks).filter(([_, taskData]) => taskData.agents && taskData.agents.includes(agentName)) as [taskName, _]}
                      <div class="task-badge" title={taskName}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M9 11l3 3L22 4"></path>
                          <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                        </svg>
                        <span>{taskName}</span>
                      </div>
                    {/each}
                  </div>
                  
                  <!-- Add tools display -->
                  {#if crew.agents[agentName]?.tools && crew.agents[agentName].tools.length > 0}
                    <div class="agent-tools">
                      {#each crew.agents[agentName].tools as tool}
                        <div class="tool-badge" title={tool}>
                          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
                          </svg>
                          <span>{tool}</span>
                        </div>
                      {/each}
                    </div>
                  {/if}
                </div>
                
                {#if index < crew.process.crew.agents.length - 1}
                  <div class="connector">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <line x1="5" y1="12" x2="19" y2="12"></line>
                      <polyline points="12 5 19 12 12 19"></polyline>
                    </svg>
                  </div>
                {/if}
              {/each}
            </div>
            {:else  }
              <div class="empty-state">No agents defined for this team</div>
            {/if}
            
            <!-- Add unused agents section -->
            {#if Object.keys(crew.agents).length > crew.process.crew.agents.length}
              <div class="unused-agents-section">
                <h3>Unused Agents</h3>
                <div class="unused-agents-grid">
                    {#each Object.keys(crew.agents).filter(agentName => !crew.process.crew.agents.includes(agentName)) as agentName}
                    <div class="agent-node unused" on:click={() => goto(`/crew/${crew.name}/taskagent/${agentName}`)}>
                      <div class="agent-icon unused">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                          <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                      </div>
                      <div class="agent-name" title={agentName}>{agentName}</div>
                      
                      <!-- Add delegation indicator badge if agent can delegate -->
                      {#if crew.agents[agentName]?.allow_delegation}
                        <div class="delegation-badge unused" title="Can delegate to other agents">
                          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                          </svg>
                          <span>Delegator</span>
                        </div>
                      {/if}
                      
                      <!-- Add associated tasks display -->
                        <div class="agent-tasks">
                        {#each Object.entries(crew.tasks).filter(([_, taskData]) => taskData.agents && taskData.agents.includes(agentName)) as [taskName, _]}
                            <div class="task-badge" title={taskName}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M9 11l3 3L22 4"></path>
                                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                            </svg>
                            <span>{taskName}</span>
                            </div>
                        {/each}
                        </div>
                        
                      <!-- Add tools display for unused agents -->
                        {#if crew.agents[agentName]?.tools && crew.agents[agentName].tools.length > 0}
                          <div class="agent-tools">
                            {#each crew.agents[agentName].tools as tool}
                              <div class="tool-badge" title={tool}>
                                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                  <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
                                </svg>
                                <span>{tool}</span>
                              </div>
                            {/each}
                          </div>
                        {/if}
                    </div>
                  {/each}
                </div>
              </div>
            {/if}
          {:else}
            <div class="empty-state">No agents defined for this team</div>
          {/if}
        </div>
      
      {:else if crew.process?.crew?.process?.toLowerCase() === 'hierarchical'}
        <div class="hierarchical-workflow">
          {#if crew.agents && Object.keys(crew.agents).length > 0}
            {#if crew.process?.crew?.agents && crew.process?.crew?.agents.length > 0}
                <div class="process-description">
                <p>
                    <span class="process-tag">Hierarchical Process:</span> 
                    A manager agent coordinates multiple worker agents
              </p>
            </div>
                <div class="hierarchical-chart">
                <div class="manager-tier">
                    <div class="agent-node manager" on:click={() => goto(`/crew/${crew.name}/taskagent/Manager Agent`)}>
                    <div class="role-label">Manager</div>
                    <div class="agent-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                    </div>
                    <div class="agent-name" title="Manager Agent">Manager Agent</div>
                    
                    <!-- Add delegation indicator badge if manager can delegate -->
                    {#if crew.agents["Manager Agent"]?.allow_delegation}
                        <div class="delegation-badge hierarchical" title="Can delegate to all workers">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                        </svg>
                        <span>Delegator</span>
                        </div>
                        
                        <!-- Add pulsing delegation aura for manager -->
                        <div class="delegation-aura"></div>
                    {/if}
                    
                    <!-- Add associated tasks display for manager -->
                    <div class="agent-tasks">
                        {#each Object.entries(crew.tasks).filter(([_, taskData]) => taskData.agents && taskData.agents.includes("Manager Agent")) as [taskName, _]}
                        <div class="task-badge" title={taskName}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M9 11l3 3L22 4"></path>
                            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                            </svg>
                            <span>{taskName}</span>
                        </div>
                        {/each}
                    </div>
                    </div>
                </div>
                
                <div class="connector-vertical">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <polyline points="19 12 12 19 5 12"></polyline>
                    </svg>
                </div>
                
                <div class="workers-tier">
                    {#each crew.process.crew.agents as agentName, index}
                    <div class="agent-node worker" on:click={() => goto(`/crew/${crew.name}/taskagent/${agentName}`)}>
                        <div class="role-label">Worker</div>
                        <div class="agent-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                            <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                        </div>
                        <div class="agent-name" title={agentName}>{agentName}</div>
                        
                        <!-- Add delegation indicator badge if worker can delegate -->
                        {#if crew.agents[agentName]?.allow_delegation}
                        <div class="delegation-badge worker" title="Can delegate to other workers">
                            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                            </svg>
                            <span>Delegator</span>
                        </div>
                        
                        <!-- Add pulsing delegation aura for workers who can delegate -->
                        <div class="delegation-aura worker"></div>
                        {/if}
                        
                        <!-- Add associated tasks display for worker -->
                        <div class="agent-tasks">
                        {#each Object.entries(crew.tasks).filter(([_, taskData]) => taskData.agents && taskData.agents.includes(agentName)) as [taskName, _]}
                            <div class="task-badge" title={taskName}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M9 11l3 3L22 4"></path>
                                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                            </svg>
                            <span>{taskName}</span>
                            </div>
                        {/each}
                        </div>
                        
                        <!-- Add tools display -->
                        {#if crew.agents[agentName]?.tools && crew.agents[agentName].tools.length > 0}
                          <div class="agent-tools">
                            {#each crew.agents[agentName].tools as tool}
                              <div class="tool-badge" title={tool}>
                                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                  <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
                                </svg>
                                <span>{tool}</span>
                              </div>
                            {/each}
                          </div>
                        {/if}
                    </div>
                    {/each}
                </div>
              </div>
            {:else}
              <div class="empty-state">No agents defined for this team</div>
            {/if}

            
            <!-- Add unused agents section -->
            {#if Object.keys(crew.agents).length > crew.process.crew.agents.length} <!-- +1 for Manager Agent -->
              <div class="unused-agents-section">
                <h3>Unused Agents</h3>
                <div class="unused-agents-grid">
                  {#each Object.keys(crew.agents).filter(agentName => !crew.process.crew.agents.includes(agentName) && agentName !== "Manager Agent") as unusedAgentName}
                    <div class="agent-node unused" on:click={() => goto(`/crew/${crew.name}/taskagent/${unusedAgentName}`)}>
                      <div class="agent-icon unused">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                          <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                      </div>
                      <div class="agent-name" title={unusedAgentName}>{unusedAgentName}</div>
                      
                      <!-- Add delegation indicator badge if agent can delegate -->
                      {#if crew.agents[unusedAgentName]?.allow_delegation}
                        <div class="delegation-badge unused" title="Can delegate to other agents">
                          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                          </svg>
                          <span>Delegator</span>
                        </div>
                      {/if}
                      
                      <!-- Add associated tasks display -->
                      <div class="agent-tasks">
                        {#each Object.entries(crew.tasks).filter(([_, taskData]) => taskData.agents && taskData.agents.includes(unusedAgentName)) as [taskName, _]}
                          <div class="task-badge" title={taskName}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                              <path d="M9 11l3 3L22 4"></path>
                              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                            </svg>
                            <span>{taskName}</span>
                          </div>
                        {/each}
                      </div>
                      
                      <!-- Add tools display -->
                      {#if crew.agents[unusedAgentName]?.tools && crew.agents[unusedAgentName].tools.length > 0}
                        <div class="agent-tools">
                          {#each crew.agents[unusedAgentName].tools as tool}
                            <div class="tool-badge" title={tool}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
                              </svg>
                              <span>{tool}</span>
                            </div>
                          {/each}
                        </div>
                      {/if}
                    </div>
                  {/each}
                </div>
              </div>
            {/if}
          {:else}
            <div class="empty-state">No agents defined for this team</div>
          {/if}
        </div>
      
      {:else}
        <div class="empty-state">
          <p>Team structure not defined or uses an unknown process type.</p>
        </div>
        
        <!-- Show all agents when no workflow is defined -->
        {#if Object.keys(crew.agents).length > 0}
          <div class="unused-agents-section">
            <h3>Unused Agents</h3>
            <div class="unused-agents-grid">
              {#each Object.keys(crew.agents) as agentName}
                <div class="agent-node unused" on:click={() => goto(`/crew/${crew.name}/taskagent/${agentName}`)}>
                  <div class="agent-icon unused">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                      <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                  </div>
                  <div class="agent-name" title={agentName}>{agentName}</div>
                  
                  <!-- Add delegation indicator badge if agent can delegate -->
                  {#if crew.agents[agentName]?.allow_delegation}
                    <div class="delegation-badge unused" title="Can delegate to other agents">
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                      </svg>
                      <span>Delegator</span>
                    </div>
                  {/if}
                  
                  <!-- Add associated tasks display -->
                  <div class="agent-tasks">
                    {#each Object.entries(crew.tasks).filter(([_, taskData]) => taskData.agents && taskData.agents.includes(agentName)) as [taskName, _]}
                      <div class="task-badge" title={taskName}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M9 11l3 3L22 4"></path>
                          <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                        </svg>
                        <span>{taskName}</span>
                      </div>
                    {/each}
                  </div>
                  
                </div>
              {/each}
            </div>
          </div>
        {/if}
      {/if}
    </section>
    
    <!-- New Run Section -->
    <section class="run-section">
      <div class="section-header">
        <h2>Run Crew</h2>
      </div>
      
      <div class="run-content">
        {#if (crew.process && crew.process.crew && crew.process.crew.agents && crew.process.crew.tasks && Object.keys(crew.process.crew.agents).length > 0 && Object.keys(crew.process.crew.tasks).length > 0)}
          <div class="run-ready">
            <button 
              class="run-button"
              on:click={() => goto(`/crew/${crew.name}/runtime`)}
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
              Run Crew
            </button>
          </div>
        {:else}
          <div class="run-requirements-compact">
            <div class="warning-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
            </div>
            <div class="requirements-content">
              <p>Required to run: At least one <span class="missing">agent</span> needs to be defined in the team with at least one <span class="missing">input</span>.
              </p>
            </div>
          </div>
        {/if}
      </div>
    </section>
  {/if}
</main>

<!-- Add these modal forms before the style tag -->

{#if successMessage}
  <div class="success-message">
    {successMessage}
  </div>
{/if}

{#if showAgentForm}
  <div class="modal-overlay">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Add New Agent</h3>
        <button class="modal-close" on:click={() => showAgentForm = false}>
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <form on:submit={createAgent}>
        <div class="form-group">
          <label for="agentName">Agent Name <span class="required">*</span></label>
          <input 
            id="agentName" 
            type="text" 
            bind:value={newAgentName} 
            placeholder="Enter agent name"
            required
            autofocus
          />
          <p class="form-help">Enter the agent name. You'll be able to edit details after creation.</p>
        </div>
        <div class="form-actions">
          <button type="button" class="btn-secondary" on:click={() => showAgentForm = false}>Cancel</button>
          <button type="submit" class="btn-primary" disabled={formSubmitting}>
            {#if formSubmitting}
              <span class="btn-spinner"></span>
              Creating...
            {:else}
              Create Agent
            {/if}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

{#if showTaskForm}
  <div class="modal-overlay">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Add New Task</h3>
        <button class="modal-close" on:click={() => showTaskForm = false}>
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <form on:submit={createTask}>
        <div class="form-group">
          <label for="taskName">Task Name <span class="required">*</span></label>
          <input 
            id="taskName" 
            type="text" 
            bind:value={newTaskName} 
            placeholder="Enter task name"
            required
            autofocus
          />
          <p class="form-help">Enter the task name. You'll be able to edit details after creation.</p>
        </div>
        <div class="form-actions">
          <button type="button" class="btn-secondary" on:click={() => showTaskForm = false}>Cancel</button>
          <button type="submit" class="btn-primary" disabled={formSubmitting}>
            {#if formSubmitting}
              <span class="btn-spinner"></span>
              Creating...
            {:else}
              Create Task
            {/if}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

{#if showDeleteConfirmation}
  <div class="modal-overlay">
    <div class="modal-content delete-confirmation">
      <div class="modal-header delete-header">
        <h3>Delete Crew</h3>
        <button class="modal-close" on:click={() => showDeleteConfirmation = false}>
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <div class="delete-confirmation-content">
        <div class="warning-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
        </div>
        <h4 class="delete-title">Are you sure?</h4>
        <p class="delete-message">You are about to delete the crew "<strong>{crew.name}</strong>"</p>
        <div class="delete-details">
          <p class="warning-text">This action cannot be undone. All agents, tasks, and processes related to this crew will be permanently deleted.</p>
          <ul class="delete-impact-list">
            <li>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              <span>{Object.keys(crew.agents).length} agent{Object.keys(crew.agents).length !== 1 ? 's' : ''} will be deleted</span>
            </li>
            <li>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 11l3 3L22 4"></path>
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
              </svg>
              <span>{Object.keys(crew.tasks).length} task{Object.keys(crew.tasks).length !== 1 ? 's' : ''} will be deleted</span>
            </li>
          </ul>
        </div>
      </div>
      <div class="delete-form-actions">
        <button type="button" class="btn-secondary" on:click={() => showDeleteConfirmation = false}>
          Cancel
        </button>
        <button type="button" class="btn-danger" on:click={deleteCrew} disabled={deleteInProgress}>
          {#if deleteInProgress}
            <span class="btn-spinner"></span>
            Deleting...
          {:else}
            Delete Crew
          {/if}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  :global(body) {
    background-color: #f8fafc;
    margin: 0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    color: #1e293b;
  }
  
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }
  
  .crew-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2.5rem;
  }
  
  h1 {
    font-size: 2.5rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.025em;
    margin: 0;
    text-align: center;
    flex: 1;
  }
  
  .back-link {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #64748b;
    text-decoration: none;
    font-size: 0.95rem;
    transition: color 0.2s;
    margin-right: 1rem;
  }
  
  .back-link:hover {
    color: #3b82f6;
  }
  
  .delete-crew-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background-color: #fee2e2;
    color: #b91c1c;
    border: 1px solid #fecaca;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s, color 0.2s;
    margin-left: 1rem;
  }
  
  .delete-crew-button:hover {
    background-color: #fecaca;
    color: #991b1b;
  }
  
  h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1.25rem;
    color: #0f172a;
    letter-spacing: -0.015em;
  }
  
  .alert {
    background-color: rgba(245, 101, 101, 0.1);
    color: #ef4444;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-left: 4px solid #ef4444;
  }
  
  .alert-dismiss {
    background: none;
    border: none;
    color: #ef4444;
    cursor: pointer;
    padding: 0.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  section {
    background-color: white;
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  section:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.07);
  }
  
  .info-section {
    border-top: 4px solid #3b82f6;
  }
  
  .workflow-section {
    border-top: 4px solid #8b5cf6;
  }
  
  .two-column-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
  }
  
  .process-badge {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 999px;
    font-weight: 500;
    font-size: 0.875rem;
    text-transform: capitalize;
  }
  
  .process-badge.sequential {
    background-color: #dbeafe;
    color: #1e40af;
  }
  
  .process-badge.hierarchical {
    background-color: #ede9fe;
    color: #5b21b6;
  }
  
  .process-badge.unknown {
    background-color: #e2e8f0;
    color: #475569;
  }
  
  .entity-list {
    list-style-type: none;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 2rem;
    width: 100%;
  }
  
  .entity-card {
    display: flex;
    align-items: center;
    padding: 0.75rem;
    background-color: #f8fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    transition: transform 0.15s, box-shadow 0.15s;
    width: 100%;
    height: 100%;
  }
  
  .entity-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }
  
  .entity-link {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    text-decoration: none;
    color: inherit;
    width: 100%;
    overflow: hidden;
  }
  
  .entity-icon {
    min-width: 32px;
    height: 32px;
    border-radius: 6px;
    background-color: #e0f2fe;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #0284c7;
    flex-shrink: 0;
  }
  
  .entity-name {
    font-weight: 500;
    font-size: 0.875rem;
    color: #334155;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
  }
  
  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem 0;
    color: #64748b;
  }
  
  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(59, 130, 246, 0.2);
    border-radius: 50%;
    border-top-color: #3b82f6;
    animation: spin 1s ease-in-out infinite;
    margin-bottom: 1rem;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem 0;
    color: #64748b;
    background-color: #f8fafc;
    border-radius: 8px;
    font-size: 0.95rem;
  }
  
  /* Enhanced Workflow Styling */
  .process-description {
    margin-bottom: 2rem;
    text-align: center;
    color: #475569;
    font-size: 1rem;
  }
  
  .process-tag {
    font-weight: 600;
    color: #334155;
  }
  
  /* Sequential Workflow Enhanced Styling */
  .sequential-workflow {
    padding: 2rem 0;
  }
  
  .sequential-chart {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 1rem;
    background-color: #f8fafc;
    padding: 2rem;
    border-radius: 12px;
    position: relative;
  }
  
  .agent-node {
    display: flex;
    flex-direction: column;
    align-items: center;
    background-color: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 12px;
    padding: 1.5rem;
    min-width: 120px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    position: relative;
    transition: transform 0.2s, box-shadow 0.2s;
    cursor: pointer; /* Add this to indicate it's clickable */
  }
  
  .agent-node:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  }
  
  .agent-node.highlighted {
    background-color: #e0f2fe;
    border: 1px solid #38bdf8;
    box-shadow: 0 4px 16px rgba(56, 189, 248, 0.15);
  }
  
  .step-number {
    position: absolute;
    top: -10px;
    left: -10px;
    width: 24px;
    height: 24px;
    background-color: #3b82f6;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 600;
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
  }
  
  .agent-icon {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background-color: #e0f2fe;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1rem;
    color: #0284c7;
    box-shadow: 0 2px 6px rgba(2, 132, 199, 0.1);
  }
  
  .agent-name {
    font-weight: 600;
    font-size: 1rem;
    text-align: center;
    color: #334155;
    word-break: break-word;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }
  
  .connector {
    color: #64748b;
    display: flex;
    align-items: center;
    position: relative;
  }
  
  .connector svg {
    filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.1));
  }
  
  /* Hierarchical Workflow Enhanced Styling */
  .hierarchical-workflow {
    padding: 2rem 0;
  }
  
  .hierarchical-chart {
    display: flex;
    flex-direction: column;
    align-items: center;
    background-color: #f8fafc;
    padding: 2.5rem;
    border-radius: 12px;
  }
  
  .manager-tier {
    margin-bottom: 1rem;
  }
  
  .agent-node.manager {
    background-color: #eff6ff;
    border: 1px solid #93c5fd;
    min-width: 140px;
    box-shadow: 0 6px 16px rgba(59, 130, 246, 0.12);
  }
  
  .role-label {
    position: absolute;
    top: -10px;
    right: -10px;
    padding: 0.25rem 0.5rem;
    background-color: #3b82f6;
    color: white;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
  }
  
  .agent-node.manager .role-label {
    background-color: #4f46e5;
  }
  
  .agent-node.worker .role-label {
    background-color: #06b6d4;
  }
  
  .connector-vertical {
    color: #64748b;
    margin: 0.5rem 0 1.5rem;
    height: 40px;
    display: flex;
    align-items: center;
  }
  
  .connector-vertical svg {
    filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.1));
  }
  
  .workers-tier {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 1.25rem;
    width: 100%;
  }
  
  .agent-node.worker {
    background-color: #f0f9ff;
    border: 1px solid #bae6fd;
    min-width: 120px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }
  
  @media (max-width: 768px) {
    .two-column-layout {
      grid-template-columns: 1fr;
    }
    
    .container {
      padding: 1.5rem;
    }
    
    .crew-header {
      flex-direction: row;
      align-items: center;
      gap: 0.5rem;
    }
    
    h1 {
      font-size: 1.8rem;
    }
    
    .back-link, .delete-crew-button {
      font-size: 0.8rem;
      margin: 0;
      padding: 0.4rem 0.6rem;
    }
    
    .sequential-chart {
      flex-direction: column;
      padding: 1.5rem;
    }
    
    .workers-tier {
      flex-direction: column;
      align-items: center;
    }
    
    .connector {
      transform: rotate(90deg);
      margin: 1rem 0;
      height: 30px;
    }
    
    .entity-list {
      grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    }
  }
  
  /* Add this to the existing styles */
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.25rem;
  }
  
  .header-actions {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }
  
  .add-button.professional {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  .add-button.professional:hover {
    background-color: #2563eb;
    transform: translateY(-2px);
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
  }
  
  .add-button.professional:active {
    transform: translateY(0);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  .add-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .add-button:hover {
    background-color: #2563eb;
  }
  
  .add-button:active {
    transform: translateY(0);
  }
  
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(2px);
  }
  
  .modal-content {
    background-color: white;
    border-radius: 12px;
    width: 90%;
    max-width: 500px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    padding: 0;
    overflow: hidden;
  }
  
  .modal-header {
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .modal-header h3 {
    margin: 0;
    font-weight: 600;
    font-size: 1.25rem;
    color: #0f172a;
  }
  
  .modal-close {
    background: none;
    border: none;
    color: #64748b;
    cursor: pointer;
    padding: 0.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: background-color 0.2s;
  }
  
  .modal-close:hover {
    background-color: #f1f5f9;
    color: #334155;
  }
  
  form {
    padding: 1.5rem;
  }
  
  .form-group {
    margin-bottom: 1.25rem;
  }
  
  label {
    display: block;
    font-weight: 500;
    margin-bottom: 0.5rem;
    color: #334155;
    font-size: 0.95rem;
  }
  
  .required {
    color: #ef4444;
  }
  
  input, textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    font-size: 1rem;
    background-color: #f8fafc;
    color: #0f172a;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  
  input:focus, textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  }
  
  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 1.5rem;
  }
  
  .btn-primary, .btn-secondary {
    padding: 0.75rem 1.25rem;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .btn-primary {
    background-color: #3b82f6;
    color: white;
    border: none;
  }
  
  .btn-primary:hover:not(:disabled) {
    background-color: #2563eb;
  }
  
  .btn-primary:disabled {
    background-color: #93c5fd;
    cursor: not-allowed;
  }
  
  .btn-secondary {
    background-color: #f1f5f9;
    color: #334155;
    border: 1px solid #cbd5e1;
  }
  
  .btn-secondary:hover {
    background-color: #e2e8f0;
  }
  
  .btn-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    animation: spin 1s linear infinite;
  }
  
  .success-message {
    position: fixed;
    top: 20px;
    right: 20px;
    background-color: #22c55e;
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    animation: slideIn 0.3s ease-out, fadeOut 0.3s ease-in 2.7s forwards;
  }
  
  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  
  @keyframes fadeOut {
    from { opacity: 1; }
    to { opacity: 0; }
  }
  
  .form-help {
    font-size: 0.85rem;
    color: #64748b;
    margin-top: 0.5rem;
    margin-bottom: 0;
  }
  
  .edit-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background-color: #f1f5f9;
    color: #475569;
    border: 1px solid #cbd5e1;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    text-decoration: none;
    transition: background-color 0.2s, color 0.2s;
  }
  
  .edit-button:hover {
    background-color: #e2e8f0;
    color: #334155;
  }
  
  /* Styles for agent tasks display */
  .agent-tasks {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 0.75rem;
    max-width: 100%;
  }
  
  .task-badge {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    background-color: #dbeafe;
    color: #1e40af;
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
    border-radius: 999px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
    font-weight: 500;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    cursor: default;
  }
  
  .task-badge span {
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  /* Adjust agent node to accommodate tasks */
  .agent-node {
    min-width: 150px;
    min-height: 120px;
    padding: 1.5rem 1rem;
  }
  
  @media (max-width: 768px) {
    .task-badge {
      font-size: 0.65rem;
      padding: 0.2rem 0.4rem;
    }
    
    .agent-tasks {
      flex-direction: column;
      align-items: center;
    }
  }
  
  /* Delegation indicator styling */
  .delegation-badge {
    position: absolute;
    top: -10px;
    right: -10px;
    display: flex;
    align-items: center;
    gap: 0.25rem;
    background-color: #f59e0b;
    color: white;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.25rem 0.5rem;
    border-radius: 999px;
    box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);
    z-index: 10;
  }
  
  .delegation-badge.hierarchical {
    background-color: #8b5cf6;
    box-shadow: 0 2px 4px rgba(139, 92, 246, 0.3);
  }
  
  .delegation-badge.worker {
    background-color: #10b981;
    box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
  }
  
  /* Pulsing aura effect for delegators in hierarchical workflow */
  .delegation-aura {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 12px;
    z-index: -1;
    box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.2);
    animation: pulse 2s infinite;
  }
  
  .delegation-aura.worker {
    box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.2);
  }
  
  @keyframes pulse {
    0% {
      box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.4);
    }
    70% {
      box-shadow: 0 0 0 10px rgba(139, 92, 246, 0);
    }
    100% {
      box-shadow: 0 0 0 0 rgba(139, 92, 246, 0);
    }
  }
  
  /* Delegation arrows for sequential workflow */
  .delegation-arrows.sequential {
    position: absolute;
    left: 50%;
    bottom: -20px;
    transform: translateX(-50%);
    display: flex;
    justify-content: center;
    gap: 5px;
    z-index: 5;
  }
  
  .delegation-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    color: #f59e0b;
    background-color: rgba(255, 255, 255, 0.9);
    border-radius: 50%;
    padding: 2px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transform: translateY(var(--arrow-distance));
    transition: transform 0.3s ease;
  }
  
  /* Enhance agent node for delegation features */
  .agent-node {
    position: relative;
    /* ... existing agent-node styles ... */
  }
  
  /* Agent node hover effect with delegation arrows */
  .agent-node:hover .delegation-arrow {
    transform: translateY(0);
  }
  
  /* Responsive adjustments */
  @media (max-width: 768px) {
    .delegation-badge {
      font-size: 0.65rem;
      padding: 0.2rem 0.4rem;
      right: -5px;
      top: -5px;
    }
    
    .delegation-arrows.sequential {
      flex-direction: column;
      bottom: auto;
      left: -15px;
      top: 50%;
      transform: translateY(-50%);
    }
    
    .delegation-arrow {
      transform: translateX(var(--arrow-distance));
    }
    
    .agent-node:hover .delegation-arrow {
      transform: translateX(0);
    }
  }
  
  .delete-confirmation {
    max-width: 500px;
    overflow: hidden;
    border-radius: 12px;
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.2);
  }
  
  .modal-header.delete-header {
    background-color: #fee2e2;
    border-bottom: 1px solid #fecaca;
  }
  
  .delete-confirmation-content {
    padding: 2rem 1.5rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .warning-icon {
    margin-bottom: 1.25rem;
    color: #dc2626;
    background-color: #fee2e2;
    border-radius: 50%;
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .delete-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #111827;
    margin: 0 0 0.75rem 0;
  }
  
  .delete-message {
    font-size: 1.1rem;
    color: #374151;
    margin: 0 0 1.5rem 0;
  }
  
  .delete-details {
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1.25rem;
    width: 100%;
    text-align: left;
  }
  
  .warning-text {
    color: #b91c1c;
    font-size: 0.9rem;
    margin: 0 0 1rem 0;
    padding-bottom: 1rem;
    border-bottom: 1px dashed #e5e7eb;
  }
  
  .delete-impact-list {
    list-style: none;
    padding: 0;
    margin: 0.5rem 0 0 0;
  }
  
  .delete-impact-list li {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
    color: #4b5563;
    font-size: 0.9rem;
  }
  
  .delete-impact-list li svg {
    color: #9ca3af;
    flex-shrink: 0;
  }
  
  .delete-form-actions {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    padding: 1.25rem 1.5rem;
    background-color: #f9fafb;
    border-top: 1px solid #e5e7eb;
  }
  
  .btn-danger {
    background-color: #dc2626;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .btn-danger:hover:not(:disabled) {
    background-color: #b91c1c;
  }
  
  .btn-danger:disabled {
    background-color: #fca5a5;
    cursor: not-allowed;
  }
  
  @media (max-width: 640px) {
    .delete-confirmation {
      max-width: 90%;
    }
    
    .delete-form-actions {
      flex-direction: column-reverse;
      gap: 0.75rem;
    }
    
    .delete-form-actions button {
      width: 100%;
      justify-content: center;
    }
    
    .warning-icon {
      width: 60px;
      height: 60px;
    }
    
    .delete-title {
      font-size: 1.25rem;
    }
    
    .delete-message {
      font-size: 1rem;
    }
  }
  
  /* Run Section Styles */
  .run-section {
    border-top: 4px solid #16a34a;
    text-align: center;
  }
  
  .run-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1.5rem;
  }
  
  .run-description {
    font-size: 1.1rem;
    color: #334155;
    margin-bottom: 2rem;
  }
  
  .run-button {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    background-color: #16a34a;
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 4px 12px rgba(22, 163, 74, 0.2);
  }
  
  .run-button:hover {
    background-color: #15803d;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(22, 163, 74, 0.3);
  }
  
  .run-button:active {
    transform: translateY(0);
  }
  
  .run-requirements {
    background-color: #f8fafc;
    border-radius: 12px;
    padding: 2rem;
    max-width: 480px;
    margin: 0 auto;
  }
  
  .requirements-list {
    list-style: none;
    padding: 0;
    margin: 1.5rem 0;
    text-align: left;
  }
  
  .requirements-list li {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0;
    font-size: 1rem;
  }
  
  .fulfilled {
    color: #16a34a;
  }
  
  .missing {
    color: #ef4444;
  }
  
  .missing-text {
    font-size: 0.9rem;
    color: #64748b;
    font-style: italic;
  }
  
  @media (max-width: 768px) {
    .run-button {
      width: 100%;
      padding: 0.75rem 1.5rem;
      font-size: 1rem;
    }
    
    .run-requirements {
      padding: 1.5rem;
    }
  }
  
  /* Update the unused-agents-section styling */
  .unused-agents-section {
    margin-top: 3rem;
    padding-top: 2rem;
    border-top: 1px dashed #cbd5e1;
    width: 100%;
  }
  
  .unused-agents-section h3 {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: #475569;
    text-align: center;
  }
  
  .unused-agents-grid {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 1.25rem;
    width: 100%;
    padding: 1rem;
    background-color: #f8fafc;
    border-radius: 12px;
  }
  
  /* Update the unused agent node styling to be even smaller */
  .agent-node.unused {
    transform: scale(0.8);
    background-color: #f0f9ff;
    border: 1px solid #bae6fd;
    border-style: dashed;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s, border-style 0.2s;
    opacity: 0.85;
    min-width: 130px;
    padding: 1.2rem 0.8rem;
  }
  
  .agent-node.unused:hover {
    transform: scale(0.85) translateY(-5px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
    border-color: #38bdf8;
    border-style: solid;
    opacity: 1;
  }
  
  .agent-icon.unused {
    width: 40px;
    height: 40px;
    background-color: #e0f2fe;
    color: #0284c7;
    opacity: 0.8;
    margin-bottom: 0.75rem;
  }
  
  .agent-node.unused .agent-name {
    font-size: 0.9rem;
  }
  
  .agent-node.unused .task-badge {
    font-size: 0.65rem;
    padding: 0.2rem 0.4rem;
  }
  
  .delegation-badge.unused {
    background-color: #94a3b8;
    box-shadow: 0 2px 4px rgba(148, 163, 184, 0.3);
    transform: scale(0.8);
    right: -12px;
    top: -12px;
    font-size: 0.65rem;
    padding: 0.2rem 0.4rem;
  }
  
  /* Responsive adjustments for even smaller unused agents */
  @media (max-width: 768px) {
    .unused-agents-grid {
      padding: 1rem 0.5rem;
      gap: 0.75rem;
    }
    
    .agent-node.unused {
      transform: scale(0.75);
      min-width: 120px;
    }
    
    .agent-node.unused:hover {
      transform: scale(0.8) translateY(-3px);
    }
  }
  
  /* Styles for agent tools display */
  .agent-tools {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 0.75rem;
    max-width: 100%;
  }
  
  .tool-badge {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    background-color: #dbeafe;
    color: #1e40af;
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
    border-radius: 999px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
    font-weight: 500;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    cursor: default;
  }
  
  .tool-badge span {
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  /* Tool badge styling */
  .agent-tools {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 0.75rem;
    max-width: 100%;
  }
  
  .tool-badge {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    background-color: #fef3c7;
    color: #92400e;
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
    border-radius: 999px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
    font-weight: 500;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    cursor: default;
  }
  
  .tool-badge span {
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  /* Update agent node styling to accommodate tools */
  .agent-node {
    min-height: 140px;
  }
  
  .agent-node.unused .tool-badge {
    font-size: 0.65rem;
    padding: 0.2rem 0.4rem;
  }
  
  @media (max-width: 768px) {
    .tool-badge {
      font-size: 0.65rem;
      padding: 0.2rem 0.4rem;
    }
    
    .agent-tools {
      flex-direction: column;
      align-items: center;
    }
  }
  
  /* ... existing styles ... */
  
  .alert-fixed {
    position: fixed;
    top: 20px;
    left: 0;
    right: 0;
    display: flex;
    justify-content: center;
    z-index: 2000; /* Higher than modal overlay */
    pointer-events: none; /* Let clicks pass through to elements below */
    animation: slideDown 0.3s ease-out;
  }
  
  .alert {
    background-color: rgba(245, 101, 101, 0.95);
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 600px;
    width: 90%;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    pointer-events: auto; /* Make the alert itself clickable */
    animation: fadeIn 0.3s ease-out, fadeOut 0.3s ease-in 2.7s forwards;
  }
  
  .alert-dismiss {
    background: none;
    border: none;
    color: white;
    cursor: pointer;
    padding: 0.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  @keyframes slideDown {
    from { transform: translateY(-100%); }
    to { transform: translateY(0); }
  }
  
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  
  @keyframes fadeOut {
    from { opacity: 1; }
    to { opacity: 0; }
  }
  
  /* ... rest of your styles ... */
</style>
