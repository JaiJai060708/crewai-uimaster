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
  
  // New variables for forms
  let showAgentForm = false;
  let showTaskForm = false;
  let newAgentName = '';
  let newTaskName = '';
  let formSubmitting = false;
  let successMessage = null;
  
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
  
  // Create new agent
  async function createAgent(event) {
    event.preventDefault();
    formSubmitting = true;
    
    try {
      // Prepare the data - just create with empty details
      const currentAgents = { ...crew.agents };
      currentAgents[newAgentName] = {};
      
      // Use the existing PUT endpoint
      const response = await fetch(`/api/crew/${crew.name}/agents`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          agents: currentAgents
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to create agent');
      }
      
      // Navigate to the agent detail page
      goto(`/crew/${crew.name}/agent/${newAgentName}`);
      
    } catch (err) {
      error = err.message;
      console.error('Error creating agent:', err);
      formSubmitting = false;
      showAgentForm = false;
    }
  }
  
  // Create new task
  async function createTask(event) {
    event.preventDefault();
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
      error = err.message;
      console.error('Error creating task:', err);
      formSubmitting = false;
      showTaskForm = false;
    }
  }
  
  onMount(fetchCrewData);
</script>

<main class="container">
  <header class="crew-header">
    <h1>{crew.name}</h1>
    <a href="/" class="back-link">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="19" y1="12" x2="5" y2="12"></line>
        <polyline points="12 19 5 12 12 5"></polyline>
      </svg>
      Back to Crews
    </a>
  </header>
  
  {#if error}
    <div class="alert">
      <p>{error}</p>
      <button class="alert-dismiss" on:click={() => error = null}>
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>
  {/if}
  
  {#if loading}
    <div class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading crew data...</p>
    </div>
  {:else}
    <section class="workflow-section">
      <div class="section-header">
        <h2>Workflow</h2>
        <a href="/crew/{crew.name}/process" class="edit-button">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
          </svg>
          Edit Workflow
        </a>
      </div>
      
      {#if crew.process?.crew?.process?.toLowerCase() === 'sequential'}
        <div class="sequential-workflow">
          {#if crew.process?.crew?.agents && crew.process.crew.agents.length > 0}
            <div class="process-description">
              <p>
                <span class="process-tag">Sequential Process:</span> 
                Agents work in order, passing results from one to the next
              </p>
            </div>
            <div class="sequential-chart">
              {#each crew.process.crew.agents as agentName, index}
                <div class="agent-node" class:highlighted={index === 0}>
                  <div class="step-number">{index + 1}</div>
                  <div class="agent-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                      <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                  </div>
                  <div class="agent-name" title={agentName}>{agentName}</div>
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
          {:else}
            <div class="empty-state">No agents defined for this workflow</div>
          {/if}
        </div>
      
      {:else if crew.process?.crew?.process?.toLowerCase() === 'hierarchical'}
        <div class="hierarchical-workflow">
          {#if crew.process?.crew?.agents && crew.process.crew.agents.length > 0}
            <div class="process-description">
              <p>
                <span class="process-tag">Hierarchical Process:</span> 
                A manager agent coordinates multiple worker agents
              </p>
            </div>
            <div class="hierarchical-chart">
              <div class="manager-tier">
                <div class="agent-node manager">
                  <div class="role-label">Manager</div>
                  <div class="agent-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                      <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                  </div>
                  <div class="agent-name" title="Manager Agent">Manager Agent</div>
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
                  <div class="agent-node worker">
                    <div class="role-label">Worker</div>
                    <div class="agent-icon">
                      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                      </svg>
                    </div>
                    <div class="agent-name" title={agentName}>{agentName}</div>
                  </div>
                {/each}
              </div>
            </div>
          {:else}
            <div class="empty-state">No agents defined for this workflow</div>
          {/if}
        </div>
      
      {:else}
        <div class="empty-state">
          <p>Workflow structure not defined or uses an unknown process type.</p>
        </div>
      {/if}
    </section>
    
    <div class="two-column-layout">
      <section class="info-section">
        <h2>Agents</h2>
        <div class="section-header">
          <button class="add-button" on:click={() => showAgentForm = true}>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            Add Agent
          </button>
        </div>
        {#if crew.agents && Object.keys(crew.agents).length > 0}
          <ul class="entity-list">
            {#each Object.keys(crew.agents) as agentName}
              <li class="entity-card">
                <a href="/crew/{crew.name}/agent/{agentName}" class="entity-link" title={agentName}>
                  <div class="entity-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                      <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                  </div>
                  <span class="entity-name">{agentName}</span>
                </a>
              </li>
            {/each}
          </ul>
        {:else}
          <div class="empty-state">No agents defined for this crew</div>
        {/if}
      </section>
      
      <section class="info-section">
        <h2>Tasks</h2>
        <div class="section-header">
          <button class="add-button" on:click={() => showTaskForm = true}>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            Add Task
          </button>
        </div>
        {#if crew.tasks && Object.keys(crew.tasks).length > 0}
          <ul class="entity-list">
            {#each Object.keys(crew.tasks) as taskName}
              <li class="entity-card">
                <a href="/crew/{crew.name}/task/{taskName}" class="entity-link" title={taskName}>
                  <div class="entity-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M9 11l3 3L22 4"></path>
                      <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                    </svg>
                  </div>
                  <span class="entity-name">{taskName}</span>
                </a>
              </li>
            {/each}
          </ul>
        {:else}
          <div class="empty-state">No tasks defined for this crew</div>
        {/if}
      </section>
    </div>
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
  }
  
  .back-link {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #64748b;
    text-decoration: none;
    font-size: 0.95rem;
    transition: color 0.2s;
  }
  
  .back-link:hover {
    color: #3b82f6;
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
      flex-direction: column;
      align-items: flex-start;
      gap: 1rem;
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
  
  .add-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .add-button:hover {
    background-color: #2563eb;
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
</style>
