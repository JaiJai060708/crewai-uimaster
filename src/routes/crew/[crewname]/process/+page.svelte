<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  
  let crewName = $page.params.crewname;
  
  let process = {
    process: 'Hierarchical',
    agents: [],
    tasks: [],
    inputs: {}
  };
  
  let originalProcess = {};
  let loading = true;
  let error = null;
  let errorTimeout;
  let saveSuccess = false;
  let successTimeout;
  
  // Function to set error with auto-dismiss
  function setError(message) {
    clearTimeout(errorTimeout);
    error = message;
    
    if (error) {
      errorTimeout = setTimeout(() => {
        error = null;
      }, 3000);
    }
  }
  
  // Function to set success with auto-dismiss
  function setSuccess(value) {
    clearTimeout(successTimeout);
    saveSuccess = value;
    
    if (saveSuccess) {
      successTimeout = setTimeout(() => {
        saveSuccess = false;
      }, 3000);
    }
  }
  
  // Replace these two variables
  // let availableAgents = [];
  // let availableTasks = [];

  // With a single structure that contains both agent and task pairs
  let availableAgentTasks = [];
  
  // Fetch process data
  async function fetchProcessData() {
    loading = true;
    setError(null);
    
    try {
      // Fetch process information for the crew
      const processResponse = await fetch(`/api/crew/${crewName}/process`);
      if (!processResponse.ok) throw new Error('Failed to fetch crew process');
      const processData = await processResponse.json();
      
      // Check if process exists and has the crew structure
      if (!processData.process || !processData.process.crew) {
        throw new Error(`Process not found for crew "${crewName}"`);
      }
      
      const crewData = processData.process.crew;
      
      // Normalize process type to lowercase first, then capitalize first letter
      if (crewData.process) {
        const processType = crewData.process.toLowerCase();
        process.process = processType.charAt(0).toUpperCase() + processType.slice(1);
      }
      
      // Get agents and tasks from the crew structure
      process.agents = crewData.agents || [];
      process.tasks = crewData.tasks || [];
      
      // Initialize inputs object if not present
      process.inputs = crewData.inputs || {};
      
      // Extract all input variables from tasks
      await fetchTaskInputVariables();
      
      // Create a deep copy of the original process data
      originalProcess = JSON.parse(JSON.stringify(process));
      
      // Fetch available agent-task pairs
      await fetchAvailableAgentTasks();
      
    } catch (err) {
      setError(err.message);
      console.error('Error fetching process data:', err);
    } finally {
      loading = false;
    }
  }
  
  // New unified function to fetch agent-task pairs
  async function fetchAvailableAgentTasks() {
    try {
      const tasksResponse = await fetch(`/api/crew/${crewName}/tasks`);
      if (!tasksResponse.ok) throw new Error('Failed to fetch crew tasks');
      const tasksData = await tasksResponse.json();
      
      if (tasksData.tasks) {
        // Reset the available agent-task pairs
        availableAgentTasks = [];
        
        // Loop through all tasks to extract agent associations
        Object.entries(tasksData.tasks).forEach(([taskName, taskData]) => {
          // Only include tasks that have at least one agent defined
          if (taskData.agents) {
            //  create an agent-task pair
              availableAgentTasks.push({
                agent: taskData.agents,
                task: taskName
              });
          }
        });
      }
    } catch (err) {
      console.error('Error fetching available agent-task pairs:', err);
    }
  }
  
  // Extract input variables from all tasks
  async function fetchTaskInputVariables() {
    try {
      const tasksResponse = await fetch(`/api/crew/${crewName}/tasks`);
      if (!tasksResponse.ok) throw new Error('Failed to fetch crew tasks');
      const tasksData = await tasksResponse.json();
      
      if (tasksData.tasks) {
        const allInputs = {};
        const inputSources = {};
        
        // Loop through all tasks to extract input variables
        Object.entries(tasksData.tasks).forEach(([taskName, taskData]) => {
          if (taskData.description) {
            // Use regex to find all {variable} patterns
            const matches = taskData.description.match(/\{([^{}]+)\}/g);
            
            if (matches) {
              matches.forEach(match => {
                // Remove the curly braces to get the variable name
                const varName = match.substring(1, match.length - 1);
                
                // Add to inputs if not already present
                if (!allInputs[varName]) {
                  // Don't use stored values, just initialize empty
                  allInputs[varName] = '';
                  
                  // Track which task uses this input
                  if (!inputSources[varName]) {
                    inputSources[varName] = [];
                  }
                  if (!inputSources[varName].includes(taskName)) {
                    inputSources[varName].push(taskName);
                  }
                }
              });
            }
          }
        });
        
        // Update process inputs without referencing any stored values
        process.inputs = allInputs;
        
        // Store input sources for display
        process.inputSources = inputSources;
      }
    } catch (err) {
      console.error('Error fetching task input variables:', err);
    }
  }
  
  // Save process data
  async function saveProcess() {
    loading = true;
    setError(null);
    setSuccess(false);
    
    try {
      // Prepare the data with correct format to match the crew structure in YAML
      // Don't include inputs in the saved process
      const processData = {
        process: {
          crew: {
            process: process.process.toLowerCase(),
            agents: process.agents,
            tasks: process.tasks
            // Inputs are not included here to avoid storing them
          }
        }
      };
      
      // Save the updated process data
      const saveResponse = await fetch(`/api/crew/${crewName}/process`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(processData)
      });
      
      if (!saveResponse.ok) throw new Error('Failed to save process data');
      
      // Update the original process data after successful save
      originalProcess = JSON.parse(JSON.stringify(process));
      setSuccess(true);
      
    } catch (err) {
      setError(err.message);
      console.error('Error saving process data:', err);
    } finally {
      loading = false;
    }
  }
  
  // Move item in array up or down
  function moveItem(array, index, direction) {
    if (direction === 'up' && index > 0) {
      const temp = array[index];
      array[index] = array[index - 1];
      array[index - 1] = temp;
      
      // Also move the associated task
      if (array === process.agents && process.tasks.length > index) {
        const tempTask = process.tasks[index];
        process.tasks[index] = process.tasks[index - 1];
        process.tasks[index - 1] = tempTask;
      }
      
      process = { ...process }; // Trigger reactivity
    } else if (direction === 'down' && index < array.length - 1) {
      const temp = array[index];
      array[index] = array[index + 1];
      array[index + 1] = temp;
      
      // Also move the associated task
      if (array === process.agents && process.tasks.length > index) {
        const tempTask = process.tasks[index];
        process.tasks[index] = process.tasks[index + 1];
        process.tasks[index + 1] = tempTask;
      }
      
      process = { ...process }; // Trigger reactivity
    }
  }
  
  // Remove item from array
  function removeItem(array, index) {
    array.splice(index, 1);
    
    // Also remove the associated task
    if (array === process.agents && process.tasks.length > index) {
      process.tasks.splice(index, 1);
    }
    
    process = { ...process }; // Trigger reactivity
  }
  
  // Modify the addAgent function to use the availableAgentTasks
  function addAgent(agent) {
    if (!process.agents.includes(agent)) {
      // Find the associated task for this agent
      const agentTaskPair = availableAgentTasks.find(pair => pair.agent === agent);
      
      // Use the associated task if found, otherwise use empty string
      const task = agentTaskPair ? agentTaskPair.task : '';
      
      // Add the agent and its associated task
      process.agents.push(agent);
      process.tasks.push(task);
      process = { ...process }; // Trigger reactivity
    }
  }
  
  // Check if changes were made
  $: hasChanges = JSON.stringify(process) !== JSON.stringify(originalProcess);
  
  onMount(() => {
    fetchProcessData();
    
    // Return cleanup function
    return () => {
      clearTimeout(errorTimeout);
      clearTimeout(successTimeout);
    };
  });
</script>

<!-- Fixed position alerts that are always visible -->
{#if error}
  <div class="alert-fixed">
    <div class="alert error">
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

{#if saveSuccess}
  <div class="alert-fixed">
    <div class="alert success">
      <p>Process saved successfully!</p>
      <button class="alert-dismiss" on:click={() => setSuccess(false)}>
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>
  </div>
{/if}

<main class="container">
  <header class="process-header">
    <a href="/crew/{crewName}" class="back-link">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="19" y1="12" x2="5" y2="12"></line>
        <polyline points="12 19 5 12 12 5"></polyline>
      </svg>
      Back to Crew
    </a>
    <div class="title-section">
      <h1>Process Configuration</h1>
      <div class="process-crew">
        For crew: <a href="/crew/{crewName}">{crewName}</a>
      </div>
    </div>
    <div class="spacer"></div>
  </header>
  
  {#if loading}
    <div class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading process data...</p>
    </div>
  {:else}
    <form on:submit|preventDefault={saveProcess} class="process-form">
      <section class="form-section">
        <div class="form-group">
          <label for="process-type">Process Type</label>
          <div class="process-type-selector">
            <label class="radio-label">
              <input 
                type="radio" 
                name="process-type" 
                value="Hierarchical" 
                bind:group={process.process}
              />
              <span class="radio-text">Hierarchical</span>
            </label>
            <label class="radio-label">
              <input 
                type="radio" 
                name="process-type" 
                value="Sequential" 
                bind:group={process.process}
              />
              <span class="radio-text">Sequential</span>
            </label>
          </div>
          <div class="field-description">
            <strong>Hierarchical:</strong> Tasks can be performed concurrently by different agents<br>
            <strong>Sequential:</strong> Tasks are performed one after another in the specified order
          </div>
        </div>
        
        <div class="form-group">
          <label>Agents</label>
          <div class="ordered-list-container">
            {#if process.agents.length === 0}
              <div class="empty-list">No agents selected</div>
            {:else}
              <div class="ordered-list">
                {#each process.agents as agent, index}
                  <div class="ordered-item">
                    <div class="item-name">{agent}</div>
                    <div class="item-actions">
                      <button type="button" on:click={() => moveItem(process.agents, index, 'up')} disabled={index === 0}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <polyline points="18 15 12 9 6 15"></polyline>
                        </svg>
                      </button>
                      <button type="button" on:click={() => moveItem(process.agents, index, 'down')} disabled={index === process.agents.length - 1}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <polyline points="6 9 12 15 18 9"></polyline>
                        </svg>
                      </button>
                      <button type="button" on:click={() => removeItem(process.agents, index)} class="remove-btn">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <line x1="18" y1="6" x2="6" y2="18"></line>
                          <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                      </button>
                    </div>
                  </div>
                {/each}
              </div>
            {/if}
            
            <div class="add-item-container">
              <select id="agent-select" class="item-select">
                <option value="" disabled selected>Select an agent to add</option>
                {#each availableAgentTasks as pair}
                  {#if !process.agents.includes(pair.agent)}
                    <option value={pair.agent}>{pair.agent}</option>
                  {/if}
                {/each}
              </select>
              <button 
                type="button" 
                class="add-btn"
                on:click={() => {
                  const agentSelect = document.getElementById('agent-select');
                  if (agentSelect.value) {
                    addAgent(agentSelect.value);
                    agentSelect.value = '';
                  }
                }}
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                Add
              </button>
            </div>
        
        <div class="form-group">
          <label>Input Variables</label>
          <div class="input-variables-container">
            {#if Object.keys(process.inputs).length === 0}
              <div class="empty-list">No input variables found in task descriptions</div>
            {:else}
              <div class="input-variables-list">
                {#each Object.entries(process.inputs) as [varName, value]}
                  <div class="input-variable-item">
                    <div class="input-variable-header">
                      <span class="input-variable-name">{varName}</span>
                      <div class="input-source-tasks">
                        Used in: 
                        {#each process.inputSources[varName] || [] as taskName, i}
                          <a href="/crew/{crewName}/task/{taskName}">{taskName}</a>{i < (process.inputSources[varName].length - 1) ? ', ' : ''}
                        {/each}
                      </div>
                    </div>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
          <div class="field-description">
            These input variables are found in your task descriptions. To edit their values, visit the individual task pages.
          </div>
        </div>
      </section>
      
      <div class="form-actions">
        <button type="submit" class="save-btn" disabled={loading || !hasChanges}>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
            <polyline points="17 21 17 13 7 13 7 21"></polyline>
            <polyline points="7 3 7 8 15 8"></polyline>
          </svg>
          Save Changes
        </button>
      </div>
    </form>
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
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
  }
  
  .process-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2.5rem;
  }
  
  .title-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    flex: 1;
  }
  
  .spacer {
    width: 115px; /* Approximate width of the back button to maintain balance */
  }
  
  h1 {
    font-size: 2.5rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.025em;
    margin: 0;
  }
  
  .process-crew {
    font-size: 0.95rem;
    color: #64748b;
  }
  
  .process-crew a {
    color: #3b82f6;
    text-decoration: none;
    font-weight: 500;
  }
  
  .process-crew a:hover {
    text-decoration: underline;
  }
  
  .back-link {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #64748b;
    text-decoration: none;
    font-size: 0.95rem;
    transition: color 0.2s;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
    background-color: white;
    margin-right: 1rem;
  }
  
  .back-link:hover {
    color: #3b82f6;
    border-color: #bfdbfe;
    background-color: #f8fafc;
  }
  
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
  }
  
  .alert.error {
    background-color: rgba(245, 101, 101, 0.95);
    color: white;
    animation: fadeIn 0.3s ease-out, fadeOut 0.3s ease-in 2.7s forwards;
  }
  
  .alert.success {
    background-color: rgba(16, 185, 129, 0.95);
    color: white;
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
  
  .form-section {
    background-color: white;
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    border-top: 4px solid #3b82f6;
  }
  
  .form-group {
    margin-bottom: 2rem;
  }
  
  .form-group:last-child {
    margin-bottom: 0;
  }
  
  label {
    display: block;
    margin-bottom: 0.75rem;
    font-weight: 600;
    color: #0f172a;
    font-size: 1rem;
  }
  
  .field-description {
    margin-top: 0.5rem;
    font-size: 0.85rem;
    color: #64748b;
    line-height: 1.4;
  }
  
  .process-type-selector {
    display: flex;
    gap: 2rem;
    margin-bottom: 0.5rem;
  }
  
  .radio-label {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
  }
  
  input[type="radio"] {
    appearance: none;
    width: 20px;
    height: 20px;
    border: 1px solid #cbd5e1;
    border-radius: 50%;
    background-color: #f8fafc;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
  }
  
  input[type="radio"]:checked {
    border-color: #3b82f6;
    border-width: 5px;
  }
  
  input[type="radio"]:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  }
  
  .radio-text {
    font-weight: 500;
    color: #0f172a;
  }
  
  .ordered-list-container {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    overflow: hidden;
  }
  
  .empty-list {
    padding: 1.5rem;
    color: #94a3b8;
    text-align: center;
    background-color: #f8fafc;
    font-style: italic;
  }
  
  .ordered-list {
    max-height: 300px;
    overflow-y: auto;
  }
  
  .ordered-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #e2e8f0;
    background-color: #f8fafc;
  }
  
  .ordered-item:last-child {
    border-bottom: none;
  }
  
  .item-name {
    font-weight: 500;
    flex-grow: 1;
  }
  
  .item-actions {
    display: flex;
    gap: 0.25rem;
  }
  
  .item-actions button {
    background: none;
    border: none;
    padding: 0.25rem;
    border-radius: 4px;
    cursor: pointer;
    color: #64748b;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .item-actions button:hover {
    background-color: #e2e8f0;
    color: #0f172a;
  }
  
  .item-actions button:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }
  
  .remove-btn:hover {
    color: #ef4444 !important;
  }
  
  .add-item-container {
    display: flex;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    border-top: 1px solid #e2e8f0;
    background-color: white;
  }
  
  .item-select {
    flex-grow: 1;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    border: 1px solid #cbd5e1;
    font-family: inherit;
    font-size: 0.95rem;
    color: #334155;
    background-color: #f8fafc;
  }
  
  .item-select:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  }
  
  .add-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 500;
    font-size: 0.95rem;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .add-btn:hover {
    background-color: #2563eb;
  }
  
  .form-actions {
    display: flex;
    justify-content: flex-end;
  }
  
  .save-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
  }
  
  .save-btn:hover {
    background-color: #2563eb;
  }
  
  .save-btn:disabled {
    background-color: #94a3b8;
    cursor: not-allowed;
    box-shadow: none;
  }
  
  .input-variables-container {
    background-color: white;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    overflow: hidden;
  }
  
  .input-variables-list {
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .input-variable-item {
    padding: 1rem;
    background-color: #f8fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
  }
  
  .input-variable-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }
  
  .input-variable-header label {
    margin-bottom: 0;
    color: #334155;
    font-size: 0.95rem;
  }
  
  .input-source-tasks {
    font-size: 0.8rem;
    color: #64748b;
  }
  
  .input-source-tasks a {
    color: #3b82f6;
    text-decoration: none;
  }
  
  .input-source-tasks a:hover {
    text-decoration: underline;
  }
  
  .input-variable-name {
    font-weight: 600;
    color: #334155;
    font-size: 0.95rem;
  }
  
  .input-variable-value {
    background-color: white;
    padding: 0.75rem 1rem;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
    color: #334155;
    font-family: inherit;
    font-size: 0.95rem;
    min-height: 2.5rem;
    display: flex;
    align-items: center;
  }
  
  @media (max-width: 768px) {
    .container {
      padding: 1.5rem;
    }
    
    .process-header {
      flex-direction: row;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 1.5rem;
    }
    
    h1 {
      font-size: 1.8rem;
    }
    
    .back-link {
      font-size: 0.8rem;
      margin: 0;
      padding: 0.4rem 0.6rem;
    }
    
    .process-crew {
      font-size: 0.8rem;
    }
    
    .spacer {
      display: none; /* Hide spacer on mobile to save space */
    }
    
    .form-section {
      padding: 1.5rem;
    }
    
    .process-type-selector {
      flex-direction: column;
      gap: 1rem;
    }
    
    .input-variable-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
    }
  }
</style>
