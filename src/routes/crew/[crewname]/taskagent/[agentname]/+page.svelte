<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    
    let crewName = $page.params.crewname;
    
    // Combined agent and task data structure
    let taskAgent = {
      // Agent properties
      name: $page.params.agentname,
      role: '',
      goal: '',
      backstory: '',
      allow_delegation: false,
      tools: [], // Initialize tools array
      model: 'gpt-4o-mini', // Add default model
      
      // Task properties
      description: '',
      expected_output: '',
      number_iterations: 1
    };
    
    let originalTaskAgent = {};
    let loading = true;
    let error = null;
    let saveSuccess = false;
    let deleteConfirmOpen = false; // Add state for delete confirmation modal
    let availableTools = []; // Store available tools from API
    let availableModels = []; // Store available models from API
    let toolsLoading = true; // Separate loading state for tools
    let modelsLoading = true; // Separate loading state for models
    let isEditingName = false; // New variable to track editing state
    let newAgentName = ''; // Variable to hold the new agent name
    let nameError = null; // Variable to hold name validation errors
    
    // Computed task name based on agent name
    $: taskName = taskAgent.name ? `${taskAgent.name}_task` : '';
    
    // Fetch available models
    async function fetchModels() {
      modelsLoading = true;
      try {
        const response = await fetch('/api/models');
        if (!response.ok) throw new Error('Failed to fetch models');
        const modelsData = await response.json();
        
        // Enhance models with company information
        availableModels = modelsData.flatMap(company => {
          return (company.models || []).map(model => ({
            ...model,
            _company: company.company  // Store company name in model object
          }));
        });
      } catch (err) {
        console.error('Error fetching models:', err);
        error = err.message;
      } finally {
        modelsLoading = false;
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
      if (taskAgent.tools.includes(toolName)) {
        taskAgent.tools = taskAgent.tools.filter(name => name !== toolName);
      } else {
        taskAgent.tools = [...taskAgent.tools, toolName];
      }
    }
    
    // Save agent and task simultaneously
    async function saveTaskAgent() {
       
      if (!taskAgent.name) {
        error = "Agent name is required";
        return;
      }
      
      loading = true;
      error = null;
      saveSuccess = false;
      
      try {
        // Validate number of iterations
        if (taskAgent.number_iterations < 1) {
          throw new Error('Number of iterations must be at least 1');
        }
        
        // 1. Create/update the agent
        // Fetch all agents first
        const agentsResponse = await fetch(`/api/crew/${crewName}/agents`);
        if (!agentsResponse.ok) throw new Error('Failed to fetch crew agents');
        const agentsData = await agentsResponse.json();
        
        // Prepare agent data
        const agentData = {
          name: taskAgent.name,
          role: taskAgent.role,
          goal: taskAgent.goal,
          backstory: taskAgent.backstory,
          allow_delegation: taskAgent.allow_delegation,
          tools: taskAgent.tools,
          model: taskAgent.model // Include model in agent data
        };
        
        // Update the agents data
        const updatedAgents = { ...agentsData.agents };
        updatedAgents[taskAgent.name] = agentData;
        
        // Save the updated agents data
        const saveAgentResponse = await fetch(`/api/crew/${crewName}/agents`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ agents: updatedAgents })
        });
        
        if (!saveAgentResponse.ok) throw new Error('Failed to save agent data');
        
        // 2. Create/update the task
        // Fetch all tasks first
        const tasksResponse = await fetch(`/api/crew/${crewName}/tasks`);
        if (!tasksResponse.ok) throw new Error('Failed to fetch crew tasks');
        const tasksData = await tasksResponse.json();
        
        // Prepare task data
        const taskData = {
          name: taskAgent.name + '_task',
          description: taskAgent.description,
          expected_output: taskAgent.expected_output,
          number_iterations: taskAgent.number_iterations,
          agents: taskAgent.name // Assign this agent to the task
        };
        
        // Update the tasks data
        const updatedTasks = { ...tasksData.tasks };
        updatedTasks[taskName] = taskData;
        
        // Save the updated tasks data
        const saveTaskResponse = await fetch(`/api/crew/${crewName}/tasks`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ tasks: updatedTasks })
        });
        
        if (!saveTaskResponse.ok) throw new Error('Failed to save task data');
        
        // Update the original data after successful save
        originalTaskAgent = JSON.parse(JSON.stringify(taskAgent));
        saveSuccess = true;
        
        // Hide success message after 3 seconds
        setTimeout(() => {
          saveSuccess = false;
        }, 3000);
        
      } catch (err) {
        error = err.message;
        console.error('Error saving task agent data:', err);
      } finally {
        loading = false;
      }
    }
    
    // Check if changes were made
    $: hasChanges = JSON.stringify(taskAgent) !== JSON.stringify(originalTaskAgent);
    
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
    $: inputVariables = extractInputs(taskAgent.description || '');
    
    onMount(() => {
      // Fetch both tools and models
      Promise.all([fetchTools(), fetchModels()]).then(() => {
        // Check if we have an agent name in the URL params
        const agentName = $page.params.agentname;
        
        // If not 'new', we should load the existing task agent data
        if (agentName && agentName !== 'new') {
          loadExistingTaskAgent(agentName);
        } else {
          // For a new task agent, just initialize the empty state and mark as not loading
          loading = false;
        }
        
        // Initialize textarea resize after data is loaded
        setTimeout(initTextareaResize, 0);
        // Set originalTaskAgent to prevent immediate hasChanges detection
        originalTaskAgent = JSON.parse(JSON.stringify(taskAgent));
      });
    });
    
    // Add this function to load an existing task agent
    async function loadExistingTaskAgent(agentName) {
      try {
        // Fetch agent data
        const agentResponse = await fetch(`/api/crew/${crewName}/agents`);
        if (!agentResponse.ok) throw new Error('Failed to fetch agent data');
        const agentData = await agentResponse.json();
        
        // Check if agent exists
        if (!agentData.agents[agentName]) {
          // Remove the error and silently initialize a new task agent
          taskAgent = {
            name: agentName,
            role: '',
            goal: '',
            backstory: '',
            allow_delegation: false,
            tools: [],
            model: 'gpt-4o-mini', // Set default model
            
            description: '',
            expected_output: '',
            number_iterations: 1
          };
        } else {
          // Get agent details
          const agent = agentData.agents[agentName];
          
          // Fetch task data
          const taskName = `${agentName}_task`;
          const taskResponse = await fetch(`/api/crew/${crewName}/tasks`);
          if (!taskResponse.ok) throw new Error('Failed to fetch task data');
          const taskData = await taskResponse.json();
          
          // Get task details if it exists
          const task = taskData.tasks[taskName] || {};
          
          // Populate the taskAgent object with combined data
          taskAgent = {
            name: agentName,
            role: agent.role || '',
            goal: agent.goal || '',
            backstory: agent.backstory || '',
            allow_delegation: agent.allow_delegation || false,
            tools: agent.tools || [],
            model: agent.model || 'gpt-4o-mini', // Use saved model or default
            
            description: task.description || '',
            expected_output: task.expected_output || '',
            number_iterations: task.number_iterations || 1
          };
        }
        
        // Update the original state for change detection
        originalTaskAgent = JSON.parse(JSON.stringify(taskAgent));
      } catch (err) {
        console.error('Error loading task agent:', err);
        error = err.message;
      } finally {
        loading = false;
      }
    }
    
    // Add this new function to handle deletion of task agent
    async function deleteTaskAgent() {
      loading = true;
      error = null;
      
      try {
        // 1. Delete the agent
        const agentsResponse = await fetch(`/api/crew/${crewName}/agents`);
        if (!agentsResponse.ok) throw new Error('Failed to fetch crew agents');
        const agentsData = await agentsResponse.json();
        
        // Create a copy without the agent to be deleted
        const updatedAgents = { ...agentsData.agents };
        delete updatedAgents[taskAgent.name];
        
        // Save the updated agents data
        const saveAgentResponse = await fetch(`/api/crew/${crewName}/agents`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ agents: updatedAgents })
        });
        
        if (!saveAgentResponse.ok) throw new Error('Failed to delete agent data');
        
        // 2. Delete the task
        const tasksResponse = await fetch(`/api/crew/${crewName}/tasks`);
        if (!tasksResponse.ok) throw new Error('Failed to fetch crew tasks');
        const tasksData = await tasksResponse.json();
        
        // Create a copy without the task to be deleted
        const updatedTasks = { ...tasksData.tasks };
        delete updatedTasks[taskName];
        
        // Save the updated tasks data
        const saveTaskResponse = await fetch(`/api/crew/${crewName}/tasks`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ tasks: updatedTasks })
        });
        
        if (!saveTaskResponse.ok) throw new Error('Failed to delete task data');
        
        // 3. Update process.yaml to remove any references to the deleted agent and task
        const processResponse = await fetch(`/api/crew/${crewName}/process`);
        if (!processResponse.ok) throw new Error('Failed to fetch crew process');
        const processData = await processResponse.json();
        
        if (processData && processData.process && processData.process.crew) {
          const processCrew = processData.process.crew;
          
          // Remove agent references from the agents array
          if (Array.isArray(processCrew.agents)) {
            processCrew.agents = processCrew.agents.filter(agent => agent !== taskAgent.name);
          }
          
          // Remove task references from the tasks array
          if (Array.isArray(processCrew.tasks)) {
            processCrew.tasks = processCrew.tasks.filter(task => task !== taskName);
          }
          
          // Save the updated process data
          const saveProcessResponse = await fetch(`/api/crew/${crewName}/process`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ process: processData.process })
          });
          
          if (!saveProcessResponse.ok) throw new Error('Failed to update process data');
        }
        
        // Navigate back to crew page after successful deletion
        goto(`/crew/${crewName}`);
        
      } catch (err) {
        error = err.message;
        console.error('Error deleting task agent:', err);
        loading = false;
      }
    }
    
    function handleAgentNameClick() {
        newAgentName = taskAgent.name; // Initialize with current name
        isEditingName = true; // Enable editing mode
        nameError = null; // Clear any previous errors
    }
    
    function handleAgentNameKeyPress(event) {
        if (event.key === 'Enter') {
            validateAndRename(newAgentName);
        }
    }
    
    function validateAndRename(name) {
        // Check if name is empty
        if (!name.trim()) {
            nameError = "Agent name cannot be empty";
            return;
        }
        
        // Check if name contains only allowed characters (letters, numbers, underscore)
        if (!/^[a-zA-Z0-9_]+$/.test(name)) {
            nameError = "Agent name can only contain letters, numbers, and underscores";
            return;
        }
        
        // If validation passes, attempt to rename
        renameAgent(name);
    }
    
    async function renameAgent(newName) {
        if (!newName || newName === taskAgent.name) {
            isEditingName = false;
            return;
        }
        
        try {
            // First, fetch all agents to check for name uniqueness
            const agentsResponse = await fetch(`/api/crew/${crewName}/agents`);
            if (!agentsResponse.ok) throw new Error('Failed to fetch crew agents');
            const agentsData = await agentsResponse.json();
            
            // Check if the new name already exists
            if (agentsData.agents && newName in agentsData.agents && newName !== taskAgent.name) {
                nameError = `An agent named "${newName}" already exists`;
                return;
            }
            
            // Fetch all tasks
            const tasksResponse = await fetch(`/api/crew/${crewName}/tasks`);
            if (!tasksResponse.ok) throw new Error('Failed to fetch crew tasks');
            const tasksData = await tasksResponse.json();
            
            // Fetch process data
            const processResponse = await fetch(`/api/crew/${crewName}/process`);
            if (!processResponse.ok) throw new Error('Failed to fetch crew process');
            const processData = await processResponse.json();
            
            // Create a copy of the agents object
            const updatedAgents = { ...agentsData.agents };
            
            // Store the old agent data and remove it from the object
            const oldAgentData = { ...updatedAgents[taskAgent.name] };
            delete updatedAgents[taskAgent.name];
            
            // Update agent name and add it back to the agents object
            oldAgentData.name = newName;
            updatedAgents[newName] = oldAgentData;
            
            // Save the updated agents data
            const saveAgentResponse = await fetch(`/api/crew/${crewName}/agents`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ agents: updatedAgents })
            });
            
            if (!saveAgentResponse.ok) throw new Error('Failed to save agent data');
            
            // Now handle the task rename
            const oldTaskName = `${taskAgent.name}_task`;
            const newTaskName = `${newName}_task`;
            
            // Create a copy of the tasks object
            const updatedTasks = { ...tasksData.tasks };
            
            // If the task exists, rename it
            if (updatedTasks[oldTaskName]) {
                // Store the old task data and remove it from the object
                const oldTaskData = { ...updatedTasks[oldTaskName] };
                delete updatedTasks[oldTaskName];
                
                // Update task name and agent reference
                oldTaskData.name = newTaskName;
                oldTaskData.agents = newName;
                updatedTasks[newTaskName] = oldTaskData;
                
                // Save the updated tasks data
                const saveTaskResponse = await fetch(`/api/crew/${crewName}/tasks`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ tasks: updatedTasks })
                });
                
                if (!saveTaskResponse.ok) throw new Error('Failed to save task data');
            }
            
            // Update process.yaml if it contains references to the agent or task
            if (processData && processData.process && processData.process.crew) {
                const processCrew = processData.process.crew;
                
                // Update agent references in the agents array
                if (Array.isArray(processCrew.agents)) {
                    processCrew.agents = processCrew.agents.map(agent => 
                        agent === taskAgent.name ? newName : agent
                    );
                }
                
                // Update task references in the tasks array
                if (Array.isArray(processCrew.tasks)) {
                    processCrew.tasks = processCrew.tasks.map(task => 
                        task === oldTaskName ? newTaskName : task
                    );
                }
                
                // Save the updated process data
                const saveProcessResponse = await fetch(`/api/crew/${crewName}/process`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ process: processData.process })
                });
                
                if (!saveProcessResponse.ok) throw new Error('Failed to update process data');
            }
            
            // Update local state
            taskAgent.name = newName;
            
            // Update the URL without page refresh
            const newUrl = `/crew/${crewName}/taskagent/${newName}`;
            window.history.pushState({ path: newUrl }, '', newUrl);
            
            // Show success message
            saveSuccess = true;
            setTimeout(() => {
                saveSuccess = false;
            }, 3000);
            
            // Update original state to reflect changes
            originalTaskAgent = JSON.parse(JSON.stringify(taskAgent));
            
            // Exit editing mode
            isEditingName = false;
            nameError = null;
            
        } catch (error) {
            console.error('Error renaming agent:', error);
            error = error.message;
        }
    }
    
    // Helper function to get company name from model data
    function getModelCompany(modelId) {
      for (const company of availableModels.map(model => {
        const response = model.model === modelId ? model._company : null;
        return response;
      }).filter(Boolean)) {
        if (company) return company;
      }
      
      // If not found or not associated with company, try to determine from name
      if (modelId.startsWith('gpt-') || modelId.includes('o1') || modelId.includes('o3')) {
        return 'OpenAI';
      }
      
      return '';
    }
</script>
  
  <!-- Fixed position alerts that are always visible -->
  {#if error}
    <div class="alert-fixed">
      <div class="alert error">
        <p>{error}</p>
        <button class="alert-dismiss" on:click={() => error = null}>
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
        <p>Task Agent saved successfully!</p>
        <button class="alert-dismiss" on:click={() => saveSuccess = false}>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </div>
  {/if}
  
  <main class="container">
    <header class="taskagent-header">
      <a href="/crew/{crewName}" class="back-link">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        Back to Crew
      </a>
      <div class="title-section">
        {#if isEditingName}
            <div class="edit-name-container">
                <input 
                    type="text" 
                    class="edit-name-input {nameError ? 'has-error' : ''}" 
                    bind:value={newAgentName} 
                    on:keypress={handleAgentNameKeyPress}
                    on:blur={() => isEditingName = false}
                    autofocus
                />
                {#if nameError}
                    <div class="name-error-message">{nameError}</div>
                {/if}
            </div>
        {:else}
            <h1 on:click={handleAgentNameClick}>{taskAgent.name}</h1>
        {/if}
        <div class="taskagent-crew">
          For crew: <a href="/crew/{crewName}">{crewName}</a>
        </div>
      </div>
      
      <!-- Replace the spacer with an actual delete button for existing task agents -->
      {#if $page.params.agentname !== 'new'}
        <button class="delete-btn" on:click={() => deleteConfirmOpen = true}>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            <line x1="10" y1="11" x2="10" y2="17"></line>
            <line x1="14" y1="11" x2="14" y2="17"></line>
          </svg>
          Delete
        </button>
      {:else}
        <div style="width: 100px;"></div> <!-- Keep the spacer for new task agents -->
      {/if}
    </header>
    
    <!-- Add the ChatGPT template link -->
    <div class="template-link-container">
      <a href="https://chatgpt.com/g/g-67ddbfbc52348191820b9b955ebfcd24-create-an-agent-and-a-task-for-crew-ai" target="_blank" rel="noopener noreferrer" class="template-link">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
          <polyline points="15 3 21 3 21 9"></polyline>
          <line x1="10" y1="14" x2="21" y2="3"></line>
        </svg>
        Create ChatGPT Agent Template Helper
      </a>
    </div>
    
    {#if deleteConfirmOpen}
      <div class="modal-overlay">
        <div class="modal-content delete-confirmation">
          <div class="modal-header delete-header">
            <h3>Delete Task Agent</h3>
            <button class="modal-close" on:click={() => deleteConfirmOpen = false}>
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
            <p class="delete-message">You are about to delete the task agent "<strong>{taskAgent.name}</strong>"</p>
            <div class="delete-details">
              <p class="warning-text">This action cannot be undone. The agent and its associated task will be permanently deleted.</p>
              <ul class="delete-impact-list">
                <li>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                  <span>Agent "<strong>{taskAgent.name}</strong>" will be deleted</span>
                </li>
                <li>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M9 11l3 3L22 4"></path>
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                  </svg>
                  <span>Task "<strong>{taskName}</strong>" will be deleted</span>
                </li>
              </ul>
            </div>
          </div>
          <div class="delete-form-actions">
            <button type="button" class="btn-secondary" on:click={() => deleteConfirmOpen = false}>
              Cancel
            </button>
            <button type="button" class="btn-danger" on:click={deleteTaskAgent}>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              </svg>
              Delete Task Agent
            </button>
          </div>
        </div>
      </div>
    {/if}
    
    {#if loading && !taskAgent.name}
      <div class="loading-container">
        <div class="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    {:else}
      <form on:submit|preventDefault={saveTaskAgent} class="taskagent-form">
        <!-- Agent Configuration Section -->
        <section class="form-section agent-section">
          <h2 class="section-title">Agent Configuration</h2>
          
          <div class="form-group">
            <label for="role">Role</label>
            <input 
              type="text" 
              id="role" 
              bind:value={taskAgent.role}
              placeholder="Enter agent role"
              required
            />
            <div class="field-description">The professional role this agent plays in the crew</div>
          </div>
          
          <div class="form-group">
            <label for="goal">Goal</label>
            <textarea 
              id="goal" 
              bind:value={taskAgent.goal}
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
              bind:value={taskAgent.backstory}
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
                bind:checked={taskAgent.allow_delegation}
              />
              <span class="checkbox-text">Allow Delegation</span>
            </label>
            <div class="field-description">If enabled, this agent can delegate tasks to other agents</div>
          </div>
          
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
                  <div class="tool-card {taskAgent.tools.includes(tool.name) ? 'selected' : ''}">
                    <div class="tool-header">
                      <div class="tool-checkbox">
                        <input 
                          type="checkbox" 
                          id="tool-{tool.name}" 
                          checked={taskAgent.tools.includes(tool.name)}
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
          
          <!-- Add the model selection dropdown at the bottom of the agent section -->
          <div class="form-group">
            <label for="model">Language Model</label>
            {#if modelsLoading}
              <div class="loading-small">
                <div class="loading-spinner-small"></div>
                <span>Loading models...</span>
              </div>
            {:else}
              <select 
                id="model" 
                bind:value={taskAgent.model}
                required
              >
                {#each availableModels as model}
                  <option value={model.model}>{model.name}</option>
                {/each}
              </select>
              
              <!-- Enhanced model description display -->
                {#if taskAgent.model && availableModels.length}
                  {#if availableModels.find(m => m.model === taskAgent.model)}
                  {@const selectedModel = availableModels.find(m => m.model === taskAgent.model)}
                  {@const company = selectedModel ? getModelCompany(selectedModel.model) : ''}
                  <div class="model-details">
                    <div class="model-header">
                      <div class="model-title">
                        <span class="model-name">{selectedModel.name}</span>
                        <span class="model-id">{selectedModel.model}</span>
                      </div>
                      {#if company}
                        <div class="model-company">{company}</div>
                      {/if}
                    </div>
                    <div class="model-description">{selectedModel.description}</div>
                  </div>
                {:else}
                  <div class="field-description">Select the language model this agent will use</div>
                {/if}
              {:else}
                <div class="field-description">Select the language model this agent will use</div>
              {/if}
            {/if}
          </div>
        </section>
        
        <!-- Task Configuration Section -->
        <section class="form-section task-section">
          <h2 class="section-title">Task Configuration</h2>
          
          
          <div class="form-group">
            <label for="description">Description</label>
            <textarea 
              id="description" 
              bind:value={taskAgent.description}
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
              bind:value={taskAgent.expected_output}
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
              bind:value={taskAgent.number_iterations}
              min="1"
              required
            />
            <div class="field-description">How many times this task should be repeated (minimum 1)</div>
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
    
    .taskagent-header {
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
      cursor: pointer; /* Add cursor pointer to indicate it's clickable */
      padding: 0.5rem;
      border-radius: 6px;
      transition: background-color 0.2s ease;
    }
    
    h1:hover {
      background-color: #f1f5f9; /* Light background on hover */
    }
    
    .taskagent-crew {
      font-size: 0.95rem;
      color: #64748b;
    }
    
    .taskagent-crew a {
      color: #3b82f6;
      text-decoration: none;
      font-weight: 500;
    }
    
    .taskagent-crew a:hover {
      text-decoration: underline;
    }
    
    .section-title {
      font-size: 1.5rem;
      font-weight: 600;
      color: #0f172a;
      margin: 0 0 1.5rem 0;
      border-bottom: 2px solid #e2e8f0;
      padding-bottom: 0.75rem;
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
      width: 100%;
      box-sizing: border-box;
    }
    
    .agent-section {
      border-top: 4px solid #3b82f6;
    }
    
    .task-section {
      border-top: 4px solid #8b5cf6;
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
    
    /* Keep number inputs at normal size */
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
    
    /* Task name display styling */
    .task-name-display {
      position: relative;
    }
    
    .task-name-field {
      background-color: white;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 0.85rem 1.2rem;
      font-size: 1rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      color: #334155;
    }
    
    .task-name-badge {
      background-color: #f0f9ff;
      border: 1px solid #bae6fd;
      color: #0284c7;
      font-size: 0.75rem;
      padding: 0.3rem 0.6rem;
      border-radius: 4px;
      font-weight: 500;
    }
    
    /* Input variables styling */
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
    
    .form-actions {
      display: flex;
      justify-content: flex-end;
    }
    
    .save-btn {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.75rem 1.5rem;
      background-color: #6366f1;
      color: white;
      border: none;
      border-radius: 6px;
      font-weight: 600;
      font-size: 1rem;
      cursor: pointer;
      transition: background-color 0.2s;
      box-shadow: 0 2px 4px rgba(99, 102, 241, 0.3);
    }
    
    .save-btn:hover {
      background-color: #4f46e5;
    }
    
    .save-btn:disabled {
      background-color: #94a3b8;
      cursor: not-allowed;
      box-shadow: none;
    }
    
    .taskagent-form {
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }
    
    /* Responsive styling */
    @media (max-width: 768px) {
      .container {
        padding: 1rem;
      }
      
      .taskagent-header {
        flex-direction: column;
        align-items: center;
        gap: 1rem;
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
      
      .taskagent-crew {
        font-size: 0.8rem;
      }
      
      .form-section {
        padding: 1.5rem;
      }
      
      .section-title {
        font-size: 1.3rem;
      }
      
      .form-group {
        padding: 0.75rem;
        margin-bottom: 1.5rem;
      }
      
      .task-name-field {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
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
    
    /* Delete button styling */
    .delete-btn {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: #ef4444;
      background-color: white;
      border: 1px solid #ef4444;
      border-radius: 6px;
      padding: 0.5rem 1rem;
      font-size: 0.95rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }
    
    .delete-btn:hover {
      background-color: #fee2e2;
    }
    
    /* Modal styling - updated to fix transparency issues */
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
    
    .modal-content.delete-confirmation {
      background-color: white;
      max-width: 500px;
      width: 90%;
      overflow: hidden;
      border-radius: 12px;
      box-shadow: 0 10px 35px rgba(0, 0, 0, 0.2);
      padding: 0;
    }
    
    .modal-header.delete-header {
      background-color: #fee2e2;
      border-bottom: 1px solid #fecaca;
      padding: 1.25rem 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .modal-header.delete-header h3 {
      margin: 0;
      font-weight: 600;
      font-size: 1.25rem;
      color: #0f172a;
    }
    
    .delete-confirmation-content {
      background-color: white;
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
    
    .btn-secondary {
      padding: 0.75rem 1.25rem;
      border-radius: 6px;
      font-weight: 500;
      cursor: pointer;
      transition: background-color 0.2s;
      background-color: #f1f5f9;
      color: #334155;
      border: 1px solid #cbd5e1;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    
    .btn-secondary:hover {
      background-color: #e2e8f0;
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
    
    /* Add the fixed alert styles */
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
    
    /* Add template link styles */
    .template-link-container {
      margin-bottom: 2rem;
      text-align: center;
    }
    
    .template-link {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.8rem 1.4rem;
      background-color: #10a37f;
      color: white;
      text-decoration: none;
      border-radius: 8px;
      font-weight: 500;
      transition: all 0.2s ease;
      box-shadow: 0 2px 8px rgba(16, 163, 127, 0.2);
    }
    
    .template-link:hover {
      background-color: #0d866a;
      box-shadow: 0 4px 12px rgba(16, 163, 127, 0.3);
      transform: translateY(-1px);
    }
    
    .template-link:active {
      transform: translateY(0);
    }
    
    @media (max-width: 768px) {
      .template-link-container {
        margin-bottom: 1.5rem;
      }
      
      .template-link {
        padding: 0.7rem 1.2rem;
        font-size: 0.9rem;
      }
    }
    
    /* Edit name input styling */
    .edit-name-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 100%;
    }
    
    .edit-name-input {
      font-size: 2.5rem;
      font-weight: 700;
      color: #0f172a;
      width: 100%;
      text-align: center;
      padding: 0.5rem;
      border: 2px solid #3b82f6;
      border-radius: 6px;
      margin: 0;
      background-color: white;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
    }
    
    .edit-name-input.has-error {
      border-color: #ef4444;
      box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
    }
    
    .name-error-message {
      color: #ef4444;
      font-size: 0.9rem;
      margin-top: 0.5rem;
      font-weight: 500;
      background-color: #fee2e2;
      padding: 0.4rem 0.8rem;
      border-radius: 4px;
      max-width: 100%;
      text-align: center;
    }
    
    /* Enhanced styles for model details */
    .model-details {
      margin-top: 1rem;
      padding: 1.25rem;
      background-color: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    .model-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.75rem;
    }
    
    .model-title {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }
    
    .model-name {
      font-weight: 600;
      color: #0f172a;
      font-size: 1.1rem;
    }
    
    .model-id {
      font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
      color: #64748b;
      font-size: 0.85rem;
    }
    
    .model-company {
      font-size: 0.9rem;
      font-weight: 500;
      color: #3b82f6;
      padding: 0.25rem 0.75rem;
      background-color: #dbeafe;
      border-radius: 4px;
    }
    
    .model-description {
      color: #334155;
      font-size: 0.95rem;
      line-height: 1.5;
    }
    
    @media (max-width: 640px) {
      .model-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
      }
      
      .model-company {
        align-self: flex-start;
      }
    }
  </style>   