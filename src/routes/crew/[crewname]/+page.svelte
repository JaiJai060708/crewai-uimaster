<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  
  let crew = {
    name: $page.params.crewname,
    process: {},
    agents: {},
    tasks: {}
  };
  let loading = true;
  let error = null;
  
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
    <section class="info-section">
      <h2>Process Type</h2>
      <div class="process-badge {crew.process?.crew?.process?.toLowerCase() || 'unknown'}">
        {crew.process?.crew?.process || 'Not defined'}
      </div>
    </section>
    
    <section class="workflow-section">
      <h2>Workflow</h2>
      
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
                  <div class="agent-name">{agentName}</div>
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
                  <div class="agent-name">{crew.process.crew.agents[0]}</div>
                </div>
              </div>
              
              <div class="connector-vertical">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <polyline points="19 12 12 19 5 12"></polyline>
                </svg>
              </div>
              
              <div class="workers-tier">
                {#each crew.process.crew.agents.slice(1) as agentName, index}
                  <div class="agent-node worker">
                    <div class="role-label">Worker</div>
                    <div class="agent-icon">
                      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                      </svg>
                    </div>
                    <div class="agent-name">{agentName}</div>
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
        {#if crew.agents && Object.keys(crew.agents).length > 0}
          <ul class="entity-list">
            {#each Object.keys(crew.agents) as agentName}
              <li class="entity-card">
                <a href="/crew/{crew.name}/agent/{agentName}" class="entity-link">
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
        {#if crew.tasks && Object.keys(crew.tasks).length > 0}
          <ul class="entity-list">
            {#each Object.keys(crew.tasks) as taskName}
              <li class="entity-card">
                <div class="entity-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M9 11l3 3L22 4"></path>
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                  </svg>
                </div>
                <span class="entity-name">{taskName}</span>
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
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 1rem;
  }
  
  .entity-card {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background-color: #f8fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    transition: transform 0.15s, box-shadow 0.15s;
  }
  
  .entity-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }
  
  .entity-icon {
    width: 32px;
    height: 32px;
    border-radius: 6px;
    background-color: #e0f2fe;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #0284c7;
  }
  
  .entity-name {
    font-weight: 500;
    font-size: 0.95rem;
    color: #334155;
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
  }
  
  .entity-link {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    text-decoration: none;
    color: inherit;
    width: 100%;
  }
</style>
