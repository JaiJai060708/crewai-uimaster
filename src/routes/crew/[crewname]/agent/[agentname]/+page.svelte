<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  
  let crewName = $page.params.crewname;
  let agentName = $page.params.agentname;
  
  let agent = {
    role: '',
    goal: '',
    backstory: '',
    allow_delegation: false,
    tools: [] // Initialize tools array
  };
  
  let originalAgent = {};
  let loading = true;
  let error = null;
  let saveSuccess = false;
  let availableTools = []; // Store available tools from API
  let toolsLoading = true; // Separate loading state for tools
  
  // Fetch agent data
  async function fetchAgentData() {
    loading = true;
    error = null;
    
    try {
      // Fetch agents information for the crew
      const agentsResponse = await fetch(`/api/crew/${crewName}/agents`);
      if (!agentsResponse.ok) throw new Error('Failed to fetch crew agents');
      const agentsData = await agentsResponse.json();
      
      if (!agentsData.agents || !agentsData.agents[agentName]) {
        throw new Error(`Agent "${agentName}" not found in crew "${crewName}"`);
      }
      
      agent = agentsData.agents[agentName];
      
      // If allow_delegation is not defined, set it to false by default
      if (agent.allow_delegation === undefined) {
        agent.allow_delegation = false;
      }
      
      // If tools is not defined, set it to an empty array by default
      if (agent.tools === undefined) {
        agent.tools = [];
      }
      
      // Create a deep copy of the original agent data
      originalAgent = JSON.parse(JSON.stringify(agent));
      
    } catch (err) {
      error = err.message;
      console.error('Error fetching agent data:', err);
    } finally {
      loading = false;
    }
  }
  
  // Fetch available tools
  async function fetchTools() {
    toolsLoading = true;
    try {
      const response = await fetch('/api/tools');
      if (!response.ok) throw new Error('Failed to fetch tools');
      availableTools = await response.json();
    } catch (err) {
      console.error('Error fetching tools:', err);
      error = err.message;
    } finally {
      toolsLoading = false;
    }
  }
  
  // Toggle tool selection
  function toggleTool(toolName) {
    if (agent.tools.includes(toolName)) {
      agent.tools = agent.tools.filter(name => name !== toolName);
    } else {
      agent.tools = [...agent.tools, toolName];
    }
  }
  
  // Save agent data
  async function saveAgent() {
    loading = true;
    error = null;
    saveSuccess = false;
    
    try {
      // Fetch all agents first
      const agentsResponse = await fetch(`/api/crew/${crewName}/agents`);
      if (!agentsResponse.ok) throw new Error('Failed to fetch crew agents');
      const agentsData = await agentsResponse.json();
      
      // Update the specific agent
      const updatedAgents = { ...agentsData.agents };
      updatedAgents[agentName] = agent;
      
      // Save the updated agents data
      const saveResponse = await fetch(`/api/crew/${crewName}/agents`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ agents: updatedAgents })
      });
      
      if (!saveResponse.ok) throw new Error('Failed to save agent data');
      
      // Update the original agent data after successful save
      originalAgent = JSON.parse(JSON.stringify(agent));
      saveSuccess = true;
      
      // Hide success message after 3 seconds
      setTimeout(() => {
        saveSuccess = false;
      }, 3000);
      
    } catch (err) {
      error = err.message;
      console.error('Error saving agent data:', err);
    } finally {
      loading = false;
    }
  }
  
  // Delete agent
  async function deleteAgent() {
    if (!confirm(`Are you sure you want to delete the agent "${agentName}"?`)) {
      return;
    }
    
    loading = true;
    error = null;
    
    try {
      // Fetch all agents first
      const agentsResponse = await fetch(`/api/crew/${crewName}/agents`);
      if (!agentsResponse.ok) throw new Error('Failed to fetch crew agents');
      const agentsData = await agentsResponse.json();
      
      // Remove the specific agent
      const updatedAgents = { ...agentsData.agents };
      delete updatedAgents[agentName];
      
      // Save the updated agents data
      const saveResponse = await fetch(`/api/crew/${crewName}/agents`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ agents: updatedAgents })
      });
      
      if (!saveResponse.ok) throw new Error('Failed to delete agent');
      
      // Navigate back to the crew page
      goto(`/crew/${crewName}`);
      
    } catch (err) {
      error = err.message;
      console.error('Error deleting agent:', err);
      loading = false;
    }
  }
  
  // Check if changes were made
  $: hasChanges = JSON.stringify(agent) !== JSON.stringify(originalAgent);
  
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
  
  onMount(() => {
    Promise.all([fetchAgentData(), fetchTools()]).then(() => {
      // Initialize textarea resize after data is loaded
      setTimeout(initTextareaResize, 0);
    });
  });
</script>

<main class="container">
  <header class="agent-header">
    <a href="/crew/{crewName}" class="back-link">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="19" y1="12" x2="5" y2="12"></line>
        <polyline points="12 19 5 12 12 5"></polyline>
      </svg>
      Back to Crew
    </a>
    <div class="title-section">
      <h1>{agentName}</h1>
      <div class="agent-crew">
        From crew: <a href="/crew/{crewName}">{crewName}</a>
      </div>
    </div>
    <button class="delete-btn" on:click={deleteAgent} disabled={loading}>
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 6h18"></path>
        <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
        <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
      </svg>
      Delete Agent
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
      <p>Agent saved successfully!</p>
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
      <p>Loading agent data...</p>
    </div>
  {:else}
    <form on:submit|preventDefault={saveAgent} class="agent-form">
      <section class="form-section">
        <div class="form-group">
          <label for="role">Role</label>
          <input 
            type="text" 
            id="role" 
            bind:value={agent.role}
            placeholder="Enter agent role"
            required
          />
          <div class="field-description">The professional role this agent plays in the crew</div>
        </div>
        
        <div class="form-group">
          <label for="goal">Goal</label>
          <textarea 
            id="goal" 
            bind:value={agent.goal}
            placeholder="Enter agent goal"
            rows="3"
            on:input={autoResizeTextarea}
            required
          ></textarea>
          <div class="field-description">What this agent aims to accomplish</div>
        </div>
        
        <div class="form-group">
          <label for="backstory">Backstory</label>
          <textarea 
            id="backstory" 
            bind:value={agent.backstory}
            placeholder="Enter agent backstory"
            rows="4"
            on:input={autoResizeTextarea}
            required
          ></textarea>
          <div class="field-description">Background information and personality traits</div>
        </div>
        
        <div class="form-group checkbox-group">
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              bind:checked={agent.allow_delegation}
            />
            <span class="checkbox-text">Allow Delegation</span>
          </label>
          <div class="field-description">If enabled, this agent can delegate tasks to other agents</div>
        </div>
        
        <!-- New Tools Section -->
        <div class="form-group tools-group">
          <label>Agent Tools</label>
          <div class="field-description">Select the tools this agent can use to accomplish tasks</div>
          
          {#if toolsLoading}
            <div class="tools-loading">
              <div class="loading-spinner-small"></div>
              <span>Loading available tools...</span>
            </div>
          {:else if availableTools.length === 0}
            <div class="no-tools-message">No tools available</div>
          {:else}
            <div class="tools-list">
              {#each availableTools as tool}
                <div class="tool-card {agent.tools.includes(tool.name) ? 'selected' : ''}">
                  <div class="tool-header">
                    <div class="tool-checkbox">
                      <input 
                        type="checkbox" 
                        id="tool-{tool.name}" 
                        checked={agent.tools.includes(tool.name)}
                        on:change={() => toggleTool(tool.name)}
                      />
                      <label for="tool-{tool.name}" class="tool-name">{tool.name}</label>
                    </div>
                    <button 
                      type="button" 
                      class="tool-details-toggle"
                      on:click={() => tool.showDetails = !tool.showDetails}
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        {#if tool.showDetails}
                          <polyline points="18 15 12 9 6 15"></polyline>
                        {:else}
                          <polyline points="6 9 12 15 18 9"></polyline>
                        {/if}
                      </svg>
                    </button>
                  </div>
                  
                  <div class="tool-description">{tool.description}</div>
                  
                  {#if tool.showDetails}
                    <div class="tool-details">
                      <div class="tool-detail-section">
                        <h4>Expected Input</h4>
                        <div class="tool-io-container">
                          {#each Object.entries(tool.expected_input) as [key, value]}
                            <div class="tool-io-item">
                              <span class="tool-io-key">{key}:</span>
                              <span class="tool-io-value">{value}</span>
                            </div>
                          {/each}
                        </div>
                      </div>
                      
                      <div class="tool-detail-section">
                        <h4>Expected Output</h4>
                        <div class="tool-io-container">
                          <div class="tool-io-value">{tool.expected_output}</div>
                        </div>
                      </div>
                    </div>
                  {/if}
                </div>
              {/each}
            </div>
          {/if}
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
  
  .agent-header {
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
  
  .agent-crew {
    font-size: 0.95rem;
    color: #64748b;
  }
  
  .agent-crew a {
    color: #3b82f6;
    text-decoration: none;
    font-weight: 500;
  }
  
  .agent-crew a:hover {
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
    border-top: 4px solid #3b82f6;
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
  
  /* Keep role input at normal size */
  input[type="text"]#role {
    height: auto;
    min-height: unset;
  }
  
  input[type="text"]:focus,
  textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  }
  
  .field-description {
    margin-top: 0.75rem;
    font-size: 0.85rem;
    color: #64748b;
    line-height: 1.4;
    padding-bottom: 0.5rem;
  }
  
  .checkbox-group {
    display: flex;
    flex-direction: column;
  }
  
  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
  }
  
  input[type="checkbox"] {
    appearance: none;
    width: 20px;
    height: 20px;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    background-color: #f8fafc;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
  }
  
  input[type="checkbox"]:checked {
    background-color: #3b82f6;
    border-color: #3b82f6;
  }
  
  input[type="checkbox"]:checked::after {
    content: "";
    position: absolute;
    top: 2px;
    left: 6px;
    width: 6px;
    height: 11px;
    border: solid white;
    border-width: 0 2px 2px 0;
    transform: rotate(45deg);
  }
  
  input[type="checkbox"]:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  }
  
  .checkbox-text {
    font-weight: 600;
    color: #0f172a;
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
  
  .agent-form {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }
  
  /* Styles for the tools section */
  .tools-group {
    background-color: #f8fafc;
    border-radius: 8px;
  }
  
  .tools-loading {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem;
    color: #64748b;
  }
  
  .loading-spinner-small {
    width: 20px;
    height: 20px;
    border: 2px solid rgba(59, 130, 246, 0.2);
    border-radius: 50%;
    border-top-color: #3b82f6;
    animation: spin 1s ease-in-out infinite;
  }
  
  .no-tools-message {
    padding: 1rem;
    color: #64748b;
    text-align: center;
    font-style: italic;
  }
  
  .tools-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-top: 0.5rem;
  }
  
  .tool-card {
    background-color: white;
    border-radius: 8px;
    padding: 1rem;
    border: 1px solid #e2e8f0;
    transition: all 0.2s;
  }
  
  .tool-card.selected {
    border-color: #3b82f6;
    box-shadow: 0 0 0 1px #3b82f6;
  }
  
  .tool-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }
  
  .tool-checkbox {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }
  
  .tool-name {
    font-weight: 600;
    color: #0f172a;
    cursor: pointer;
  }
  
  .tool-description {
    color: #64748b;
    font-size: 0.9rem;
    line-height: 1.5;
    margin-bottom: 0.5rem;
  }
  
  .tool-details-toggle {
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
  
  .tool-details-toggle:hover {
    background-color: #f1f5f9;
    color: #0f172a;
  }
  
  .tool-details {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px dashed #e2e8f0;
  }
  
  .tool-detail-section {
    margin-bottom: 1rem;
  }
  
  .tool-detail-section h4 {
    font-size: 0.85rem;
    color: #64748b;
    margin: 0 0 0.5rem 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .tool-io-container {
    background-color: #f8fafc;
    border-radius: 6px;
    padding: 0.75rem;
    font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
    font-size: 0.85rem;
  }
  
  .tool-io-item {
    margin-bottom: 0.5rem;
  }
  
  .tool-io-item:last-child {
    margin-bottom: 0;
  }
  
  .tool-io-key {
    color: #2563eb;
    font-weight: 600;
  }
  
  .tool-io-value {
    color: #334155;
  }
  
  @media (max-width: 768px) {
    .container {
      padding: 1rem;
    }
    
    .agent-header {
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
    
    .agent-crew {
      font-size: 0.8rem;
    }
    
    .form-section {
      padding: 1.5rem;
    }
    
    .form-group {
      padding: 0.75rem;
      margin-bottom: 1.5rem;
    }
    
    .tool-card {
      padding: 0.75rem;
    }
    
    .tool-description {
      font-size: 0.8rem;
    }
    
    .tool-io-container {
      padding: 0.5rem;
      font-size: 0.75rem;
    }
  }
</style>
