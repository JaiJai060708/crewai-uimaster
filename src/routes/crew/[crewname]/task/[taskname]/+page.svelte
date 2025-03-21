<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  
  let crewName = $page.params.crewname;
  let taskName = $page.params.taskname;
  
  let task = {
    description: '',
    expected_output: '',
    number_iterations: 1,
    agents: ''
  };
  
  let originalTask = {};
  let availableAgents = [];
  let assignedAgents = {}; // Track which agents are assigned to which tasks
  let loading = true;
  let error = null;
  let saveSuccess = false;
  
  // Fetch task data and available agents
  async function fetchData() {
    loading = true;
    error = null;
    
    try {
      // Fetch tasks information for the crew
      const tasksResponse = await fetch(`/api/crew/${crewName}/tasks`);
      if (!tasksResponse.ok) throw new Error('Failed to fetch crew tasks');
      const tasksData = await tasksResponse.json();
      
      if (!tasksData.tasks || !tasksData.tasks[taskName]) {
        throw new Error(`Task "${taskName}" not found in crew "${crewName}"`);
      }
      
      // Track which agents are already assigned to tasks
      assignedAgents = {};
      Object.entries(tasksData.tasks).forEach(([tName, tData]) => {
        if (tName !== taskName && tData.agents) {
          // If agents is still an array (backward compatibility)
          if (Array.isArray(tData.agents)) {
            tData.agents.forEach(agent => {
              assignedAgents[agent] = tName;
            });
          } else if (tData.agents) {
            // If agents is a string
            assignedAgents[tData.agents] = tName;
          }
        }
      });
      
      // Set task data
      task = tasksData.tasks[taskName];
      
      // If number_iterations is not defined, set it to 1 by default
      if (task.number_iterations === undefined) {
        task.number_iterations = 1;
      }
      
      // If agents is not defined or is an array, set it to empty string by default
      if (task.agents === undefined) {
        task.agents = '';
      } else if (Array.isArray(task.agents) && task.agents.length > 0) {
        // Convert from array to string if needed (for backward compatibility)
        task.agents = task.agents[0];
      } else if (Array.isArray(task.agents)) {
        task.agents = '';
      }
      
      // Fetch agents information for the crew to populate the dropdown
      const agentsResponse = await fetch(`/api/crew/${crewName}/agents`);
      if (!agentsResponse.ok) throw new Error('Failed to fetch crew agents');
      const agentsData = await agentsResponse.json();
      
      if (agentsData.agents) {
        availableAgents = Object.keys(agentsData.agents);
      }
      
      // Create a deep copy of the original task data
      originalTask = JSON.parse(JSON.stringify(task));
      
    } catch (err) {
      error = err.message;
      console.error('Error fetching data:', err);
    } finally {
      loading = false;
    }
  }
  
  // Save task data
  async function saveTask() {
    loading = true;
    error = null;
    saveSuccess = false;
    
    try {
      // Validate number of iterations
      if (task.number_iterations < 1) {
        throw new Error('Number of iterations must be at least 1');
      }
      
      // Fetch all tasks first
      const tasksResponse = await fetch(`/api/crew/${crewName}/tasks`);
      if (!tasksResponse.ok) throw new Error('Failed to fetch crew tasks');
      const tasksData = await tasksResponse.json();
      
      // Update the specific task
      const updatedTasks = { ...tasksData.tasks };
      updatedTasks[taskName] = task;
      
      // Save the updated tasks data
      const saveResponse = await fetch(`/api/crew/${crewName}/tasks`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ tasks: updatedTasks })
      });
      
      if (!saveResponse.ok) throw new Error('Failed to save task data');
      
      // Update the original task data after successful save
      originalTask = JSON.parse(JSON.stringify(task));
      saveSuccess = true;
      
      // Hide success message after 3 seconds
      setTimeout(() => {
        saveSuccess = false;
      }, 3000);
      
    } catch (err) {
      error = err.message;
      console.error('Error saving task data:', err);
    } finally {
      loading = false;
    }
  }
  
  // Delete task
  async function deleteTask() {
    if (!confirm(`Are you sure you want to delete the task "${taskName}"?`)) {
      return;
    }
    
    loading = true;
    error = null;
    
    try {
      // Fetch all tasks first
      const tasksResponse = await fetch(`/api/crew/${crewName}/tasks`);
      if (!tasksResponse.ok) throw new Error('Failed to fetch crew tasks');
      const tasksData = await tasksResponse.json();
      
      // Remove the specific task
      const updatedTasks = { ...tasksData.tasks };
      delete updatedTasks[taskName];
      
      // Save the updated tasks data
      const saveResponse = await fetch(`/api/crew/${crewName}/tasks`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ tasks: updatedTasks })
      });
      
      if (!saveResponse.ok) throw new Error('Failed to delete task');
      
      // Navigate back to the crew page
      goto(`/crew/${crewName}`);
      
    } catch (err) {
      error = err.message;
      console.error('Error deleting task:', err);
      loading = false;
    }
  }
  
  // Replace toggleAgent with selectAgent
  function selectAgent(agentName) {
    task.agents = agentName;
  }
  
  // Check if changes were made
  $: hasChanges = JSON.stringify(task) !== JSON.stringify(originalTask);
  
  // Helper function to check if an agent is available
  function isAgentAvailable(agentName) {
    // Agent is available if: 
    // 1. It's not assigned to any other task, or
    // 2. It's already assigned to this task
    return !assignedAgents[agentName] || (task.agents === agentName);
  }
  
  // Get a list of available agents that are not assigned to other tasks
  $: filteredAgents = availableAgents.filter(agent => isAgentAvailable(agent));
  
  // Function to auto-resize textareas
  function autoResizeTextarea(e) {
    const textarea = e.target;
    // Reset height to auto to get the correct scrollHeight
    textarea.style.height = 'auto';
    // Set the height to match the content
    textarea.style.height = textarea.scrollHeight + 'px';
  }
  
  // Initialize auto-resize for textareas after component mounts
  function initTextareaResize() {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
      // Set initial height
      textarea.style.height = 'auto';
      textarea.style.height = textarea.scrollHeight + 'px';
      // Add input event listener
      textarea.addEventListener('input', autoResizeTextarea);
    });
  }
  
  // Add this new function to extract inputs from description
  function extractInputs(text) {
    const regex = /{([^{}]+)}/g;
    const matches = [];
    let match;
    
    while ((match = regex.exec(text)) !== null) {
      if (!matches.includes(match[1])) {
        matches.push(match[1]);
      }
    }
    
    return matches;
  }
  
  // Reactive declaration to extract inputs whenever description changes
  $: inputVariables = extractInputs(task.description || '');
  
  onMount(() => {
    fetchData().then(() => {
      // Initialize textarea resize after data is loaded
      setTimeout(initTextareaResize, 0);
    });
  });
</script>

<main class="container">
  <header class="task-header">
    <a href="/crew/{crewName}" class="back-link">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="19" y1="12" x2="5" y2="12"></line>
        <polyline points="12 19 5 12 12 5"></polyline>
      </svg>
      Back to Crew
    </a>
    <div class="title-section">
      <h1>{taskName}</h1>
      <div class="task-crew">
        From crew: <a href="/crew/{crewName}">{crewName}</a>
      </div>
    </div>
    <button class="delete-btn" on:click={deleteTask} disabled={loading}>
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 6h18"></path>
        <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
        <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
      </svg>
      Delete Task
    </button>
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
  
  {#if saveSuccess}
    <div class="success-alert">
      <p>Task saved successfully!</p>
      <button class="alert-dismiss" on:click={() => saveSuccess = false}>
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
      <p>Loading task data...</p>
    </div>
  {:else}
    <form on:submit|preventDefault={saveTask} class="task-form">
      <section class="form-section">
        <div class="form-group">
          <label for="description">Description</label>
          <textarea 
            id="description" 
            bind:value={task.description}
            placeholder="Enter task description"
            rows="4"
            on:input={autoResizeTextarea}
            required
          ></textarea>

          <div class="field-description">Detailed instructions for completing this task</div>
          
          <!-- Add input variables display -->
          {#if inputVariables.length > 0}
            <div class="input-variables">
              <div class="input-variables-header">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="22 12 16 12 14 15 10 15 8 12 2 12"></polyline>
                  <path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path>
                </svg>
                <span>Input Variables</span>
              </div>
              <div class="input-variables-list">
                {#each inputVariables as variable}
                  <div class="input-variable-tag">
                    <span>{variable}</span>
                  </div>
                {/each}
              </div>
            </div>
          {/if}
          
        </div>
        
        <div class="form-group">
          <label for="expected_output">Expected Output</label>
          <textarea 
            id="expected_output" 
            bind:value={task.expected_output}
            placeholder="Enter expected output"
            rows="3"
            on:input={autoResizeTextarea}
            required
          ></textarea>
          <div class="field-description">The format and content expected as output from this task</div>
        </div>
        
        <div class="form-group">
          <label for="number_iterations">Number of Iterations</label>
          <input 
            type="number" 
            id="number_iterations" 
            bind:value={task.number_iterations}
            min="1"
            required
          />
          <div class="field-description">How many times this task should be repeated (minimum 1)</div>
        </div>
        
        <div class="form-group">
          <label>Assigned Agent</label>
          <div class="agents-selector">
            {#if availableAgents.length > 0}
              {#if filteredAgents.length > 0}
                {#each filteredAgents as agentName}
                  <div class="agent-option">
                    <label class="radio-label">
                      <input 
                        type="radio" 
                        name="agent"
                        checked={task.agents === agentName}
                        on:change={() => selectAgent(agentName)}
                      />
                      <span class="radio-text">{agentName}</span>
                    </label>
                  </div>
                {/each}
                {#if task.agents && !filteredAgents.includes(task.agents)}
                  <div class="agent-option current-agent">
                    <label class="radio-label">
                      <input 
                        type="radio" 
                        name="agent"
                        checked={true}
                      />
                      <span class="radio-text">{task.agents} (currently assigned)</span>
                    </label>
                  </div>
                {/if}
              {:else}
                <div class="empty-agents">
                  {#if task.agents}
                    <p>Currently assigned: {task.agents}</p>
                    <p>No other agents available - all are assigned to other tasks</p>
                  {:else}
                    <p>No agents available - all are assigned to other tasks</p>
                  {/if}
                </div>
              {/if}
            {:else}
              <div class="empty-agents">No agents available in this crew</div>
            {/if}
          </div>
          <div class="field-description">
            Select which agent should perform this task. Each agent can only be assigned to one task.
            {#if Object.keys(assignedAgents).length > 0}
              <div class="assigned-agents-info">
                <p>Currently assigned agents:</p>
                <ul>
                  {#each Object.entries(assignedAgents) as [agent, taskName]}
                    <li>{agent} - assigned to task: {taskName}</li>
                  {/each}
                </ul>
              </div>
            {/if}
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
  
  .task-header {
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
  
  h1 {
    font-size: 2.5rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.025em;
    margin: 0;
  }
  
  .task-crew {
    font-size: 0.95rem;
    color: #64748b;
  }
  
  .task-crew a {
    color: #3b82f6;
    text-decoration: none;
    font-weight: 500;
  }
  
  .task-crew a:hover {
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
  
  .delete-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #ef4444;
    background-color: white;
    border: 1px solid #fecaca;
    border-radius: 6px;
    padding: 0.5rem 1rem;
    font-size: 0.95rem;
    cursor: pointer;
    transition: all 0.2s;
    margin-left: 1rem;
  }
  
  .delete-btn:hover {
    background-color: #fee2e2;
    border-color: #ef4444;
  }
  
  .delete-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
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
  
  .success-alert {
    background-color: rgba(110, 231, 183, 0.1);
    color: #10b981;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-left: 4px solid #10b981;
  }
  
  .alert-dismiss {
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    padding: 0.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
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
    padding: 2.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    border-top: 4px solid #8b5cf6;
    width: 100%;
    box-sizing: border-box;
  }
  
  .form-group {
    margin-bottom: 2.5rem;
    width: 100%;
    padding: 1rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #f1f5f9;
    background-color: #f8fafc;
    border-radius: 8px;
  }
  
  .form-group:last-child {
    margin-bottom: 0;
    border-bottom: none;
  }
  
  label {
    display: block;
    margin-bottom: 0.75rem;
    font-weight: 600;
    color: #0f172a;
    font-size: 1rem;
  }
  
  input[type="text"],
  input[type="number"],
  textarea {
    width: 100%;
    padding: 0.85rem 1.2rem;
    border-radius: 6px;
    border: 1px solid #cbd5e1;
    font-family: inherit;
    font-size: 1rem;
    color: #334155;
    background-color: white;
    transition: border-color 0.2s, box-shadow 0.2s;
    box-sizing: border-box;
  }
  
  /* Specific styling for auto-expanding textareas */
  textarea {
    overflow-y: hidden; /* Hide scrollbar for auto-expanding textarea */
    resize: none; /* Disable manual resizing since we're handling it with JS */
    min-height: 100px; /* Set a minimum height */
  }
  
  /* Keep number of iterations input at normal size */
  input[type="number"] {
    width: 120px;
    height: auto;
    min-height: unset;
  }
  
  input[type="text"]:focus,
  input[type="number"]:focus,
  textarea:focus {
    outline: none;
    border-color: #8b5cf6;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2);
  }
  
  .field-description {
    margin-top: 0.75rem;
    font-size: 0.85rem;
    color: #64748b;
    line-height: 1.4;
    padding-bottom: 0.5rem;
  }
  
  .agents-selector {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
    background-color: white;
    border-radius: 6px;
    padding: 1rem;
    border: 1px solid #e2e8f0;
    margin-bottom: 0.5rem;
  }
  
  .agent-option {
    background-color: #f8fafc;
    border-radius: 6px;
    padding: 0.75rem;
    border: 1px solid #e2e8f0;
    transition: all 0.2s;
  }
  
  .agent-option:hover {
    border-color: #cbd5e1;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
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
    border: 5px solid #8b5cf6;
  }
  
  input[type="radio"]:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2);
  }
  
  .radio-text {
    font-weight: 500;
    color: #334155;
  }
  
  .empty-agents {
    grid-column: 1 / -1;
    padding: 1rem;
    text-align: center;
    color: #64748b;
    font-style: italic;
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
    background-color: #8b5cf6;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
    box-shadow: 0 2px 4px rgba(139, 92, 246, 0.3);
  }
  
  .save-btn:hover {
    background-color: #7c3aed;
  }
  
  .save-btn:disabled {
    background-color: #94a3b8;
    cursor: not-allowed;
    box-shadow: none;
  }
  
  .task-form {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }
  
  @media (max-width: 768px) {
    .container {
      padding: 1rem;
    }
    
    .task-header {
      flex-direction: row;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 1.5rem;
    }
    
    h1 {
      font-size: 1.8rem;
    }
    
    .back-link, .delete-btn {
      font-size: 0.8rem;
      margin: 0;
      padding: 0.4rem 0.6rem;
    }
    
    .task-crew {
      font-size: 0.8rem;
    }
    
    .form-section {
      padding: 1.5rem;
    }
    
    .form-group {
      padding: 0.75rem;
      margin-bottom: 1.5rem;
    }
    
    .agents-selector {
      grid-template-columns: 1fr;
    }
  }
  
  .current-agent {
    background-color: #f0f9ff;
    border-color: #bae6fd;
  }
  
  .assigned-agents-info {
    margin-top: 1rem;
    padding: 0.75rem;
    background-color: #f8fafc;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
    font-size: 0.85rem;
  }
  
  .assigned-agents-info p {
    margin: 0 0 0.5rem 0;
    font-weight: 500;
  }
  
  .assigned-agents-info ul {
    margin: 0;
    padding-left: 1.5rem;
  }
  
  .assigned-agents-info li {
    margin-bottom: 0.25rem;
  }
  
  /* Styling for input variables display */
  .input-variables {
    margin-top: 1rem;
    padding: 1rem;
    background-color: #f0f7ff;
    border-radius: 6px;
    border: 1px solid #bfdbfe;
    transition: all 0.2s ease;
  }
  
  .input-variables-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
    color: #2563eb;
    font-size: 0.9rem;
    margin-bottom: 0.75rem;
  }
  
  .input-variables-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .input-variable-tag {
    background-color: white;
    color: #1e40af;
    border: 1px solid #93c5fd;
    border-radius: 4px;
    padding: 0.4rem 0.7rem;
    font-size: 0.9rem;
    font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  }
  
  /* Add responsive styling for the input variables section */
  @media (max-width: 768px) {
    .input-variables {
      padding: 0.75rem;
    }
    
    .input-variables-header {
      font-size: 0.8rem;
      margin-bottom: 0.5rem;
    }
    
    .input-variable-tag {
      padding: 0.3rem 0.5rem;
      font-size: 0.8rem;
    }
  }
</style>
