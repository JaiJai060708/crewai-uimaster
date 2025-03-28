<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  
  let crewName = $page.params.crewname;
  
  // State variables
  let loading = true;
  let error = null;
  let isRunning = false;
  let logs = [];
  let finalResult = null;
  let inputVariables = {};
  let showLogs = true; // New state variable to track logs visibility
  let elapsedSeconds = 0; // Add counter for elapsed time
  let timerInterval; // Store interval reference
  let userToggledLogs = false;
  
  // Add new state variables for human input handling
  let waitingForInput = false;
  let currentInputRequest = null;
  let userResponse = '';
  
  // Fetch input variables
  async function fetchInputVariables() {
    loading = true;
    error = null;
    
    try {
      // Fetch process information for the crew
      const processResponse = await fetch(`/api/crew/${crewName}/process`);
      if (!processResponse.ok) throw new Error('Failed to fetch crew process');
      const processData = await processResponse.json();
      
      // Check if process exists and has the crew structure
      if (!processData.process || !processData.process.crew) {
        throw new Error(`Process not found for crew "${crewName}"`);
      }
      
      // Fetch task details to extract input variables
      const tasksResponse = await fetch(`/api/crew/${crewName}/tasks`);
      if (!tasksResponse.ok) throw new Error('Failed to fetch crew tasks');
      const tasksData = await tasksResponse.json();
      
      if (tasksData.tasks) {
        // Extract input variables from task descriptions
        const extractedInputs = {};
        
        Object.entries(tasksData.tasks).forEach(([taskName, taskData]) => {
          if (taskData.description) {
            // Use regex to find all {variable} patterns
            const matches = taskData.description.match(/\{([^{}]+)\}/g);
            
            if (matches) {
              matches.forEach(match => {
                // Remove the curly braces to get the variable name
                const varName = match.substring(1, match.length - 1);
                
                // Add to inputs if not already present
                if (!extractedInputs[varName]) {
                  extractedInputs[varName] = '';
                }
              });
            }
          }
        });
        
        inputVariables = extractedInputs;
      }
      
    } catch (err) {
      error = err.message;
      console.error('Error fetching input variables:', err);
    } finally {
      loading = false;
    }
  }
  
  // Parse ANSI color codes to HTML
  function ansiToHtml(text) {
    if (!text) return '';
    
    // Replace common ANSI color codes with span elements
    // Bold
    text = text.replace(/\u001b\[1m(.*?)(\u001b\[0m|\u001b\[22m)/g, '<span class="ansi-bold">$1</span>');
    
    // Colors
    text = text.replace(/\u001b\[30m(.*?)(\u001b\[0m|\u001b\[39m)/g, '<span class="ansi-black">$1</span>');
    text = text.replace(/\u001b\[31m(.*?)(\u001b\[0m|\u001b\[39m)/g, '<span class="ansi-red">$1</span>');
    text = text.replace(/\u001b\[32m(.*?)(\u001b\[0m|\u001b\[39m)/g, '<span class="ansi-green">$1</span>');
    text = text.replace(/\u001b\[33m(.*?)(\u001b\[0m|\u001b\[39m)/g, '<span class="ansi-yellow">$1</span>');
    text = text.replace(/\u001b\[34m(.*?)(\u001b\[0m|\u001b\[39m)/g, '<span class="ansi-blue">$1</span>');
    text = text.replace(/\u001b\[35m(.*?)(\u001b\[0m|\u001b\[39m)/g, '<span class="ansi-magenta">$1</span>');
    text = text.replace(/\u001b\[36m(.*?)(\u001b\[0m|\u001b\[39m)/g, '<span class="ansi-cyan">$1</span>');
    text = text.replace(/\u001b\[37m(.*?)(\u001b\[0m|\u001b\[39m)/g, '<span class="ansi-white">$1</span>');
    
    // Background colors
    text = text.replace(/\u001b\[40m(.*?)(\u001b\[0m|\u001b\[49m)/g, '<span class="ansi-bg-black">$1</span>');
    text = text.replace(/\u001b\[41m(.*?)(\u001b\[0m|\u001b\[49m)/g, '<span class="ansi-bg-red">$1</span>');
    text = text.replace(/\u001b\[42m(.*?)(\u001b\[0m|\u001b\[49m)/g, '<span class="ansi-bg-green">$1</span>');
    text = text.replace(/\u001b\[43m(.*?)(\u001b\[0m|\u001b\[49m)/g, '<span class="ansi-bg-yellow">$1</span>');
    text = text.replace(/\u001b\[44m(.*?)(\u001b\[0m|\u001b\[49m)/g, '<span class="ansi-bg-blue">$1</span>');
    
    // Remove any remaining ANSI escape sequences
    text = text.replace(/\u001b\[\d+(;\d+)*m/g, '');
    
    return text;
  }
  
  // Parse markdown to HTML
  function markdownToHtml(markdown) {
    if (!markdown) return '';
    
    // Simple markdown parser for common elements
    let html = markdown;
    
    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    // Bold and italic
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Lists
    html = html.replace(/^\s*\*\s+(.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
    
    // Numbered lists
    html = html.replace(/^\s*\d+\.\s+(.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/gs, '<ol>$1</ol>');
    
    // Links
    html = html.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');
    
    // Code blocks
    html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    
    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Line breaks
    html = html.replace(/\n/g, '<br>');
    
    return html;
  }
  
  // Run the crew
  async function runCrew() {
    isRunning = true;
    logs = [];
    finalResult = null;
    error = null;
    elapsedSeconds = 0; // Reset timer
    
    // Reset input-related state
    waitingForInput = false;
    currentInputRequest = null;
    userResponse = '';
    
    // Start the timer
    timerInterval = setInterval(() => {
      elapsedSeconds += 1;
    }, 1000);
    
    try {
      // Add a log to show that we're starting
      logs = [...logs, { type: 'system', message: 'Starting crew execution...' }];
      
      // Call the run endpoint with the input variables
      const response = await fetch(`/api/crew/${crewName}/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(inputVariables)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to run the crew');
      }
      
      // Handle the streaming response
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          logs = [...logs, { type: 'system', message: 'Execution completed.' }];
          break;
        }
        
        // Decode the chunk and split by newlines
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n').filter(line => line.trim());
        
        // Process each line as a JSON message
        for (const line of lines) {
          try {
            const message = JSON.parse(line);
            
            if (message.type === 'final_result') {
              finalResult = message.result;
            } else if (message.type === 'error') {
              logs = [...logs, { type: 'error', message: message.message, raw: message.message }];
              throw new Error(message.message);
            } else if (message.type === 'log') {
              logs = [...logs, { type: 'log', message: message.message, raw: message.message }];
            } else if (message.type === 'input_required') {
              // Handle input required message
              waitingForInput = true;
              currentInputRequest = message;
              logs = [...logs, { 
                type: 'input_request', 
                message: `Human input required: ${message.prompt}`, 
                raw: message.prompt,
                requestId: message.id
              }];
              // Make sure logs are visible when input is required
              if (!showLogs) {
                toggleLogs();
              }
            }
          } catch (e) {
            if (e.message !== line) {
              console.error('Error parsing log message:', e);
            }
          }
        }
      }
      
    } catch (err) {
      error = err.message;
      console.error('Error running crew:', err);
      logs = [...logs, { type: 'error', message: `Error: ${err.message}` }];
    } finally {
      isRunning = false;
      clearInterval(timerInterval); // Clear the timer
    }
  }
  
  // Toggle logs visibility with animation
  function toggleLogs() {
    if (finalResult) {
      userToggledLogs = true;
    }
    const logContainer = document.querySelector('.log-container');
    const resultContainer = document.querySelector('.result-container');
    
    if (showLogs) {
      // We're about to hide logs and show results
      if (logContainer) {
        logContainer.classList.add('animating-out');
        setTimeout(() => {
          showLogs = false;
          if (resultContainer) {
            resultContainer.classList.add('animating-in');
            setTimeout(() => {
              resultContainer.classList.remove('animating-in');
            }, 500);
          }
        }, 500);
      }
    } else {
      // We're about to show logs and hide results
      if (resultContainer) {
        resultContainer.classList.add('animating-out');
        setTimeout(() => {
          showLogs = true;
          if (logContainer) {
            logContainer.classList.add('animating-in');
            setTimeout(() => {
              logContainer.classList.remove('animating-in');
              logContainer.scrollTo({
                top: logContainer.scrollHeight,
                behavior: 'smooth'
              });
            }, 500);
          }
        }, 500);
      }
    }
  }
  
  // Track when final result is received to trigger animation
  $: if (finalResult && logs.length > 0) {
  setTimeout(() => {
    if (showLogs && !userToggledLogs) {
      const logContainer = document.querySelector('.log-container');
      const resultContainer = document.querySelector('.result-container');
      
      if (logContainer) {
        logContainer.classList.add('animating-out');
        setTimeout(() => {
          showLogs = false;
          if (resultContainer) {
            resultContainer.classList.add('animating-in');
            setTimeout(() => {
              resultContainer.classList.remove('animating-in');
            }, 500);
          }
        }, 500);
      }
    }
  }, 1200);
}
  
  // Auto-scroll to bottom of log container
  $: if (logs.length) {
    // Increased from 50ms to 100ms
    setTimeout(() => {
      const logContainer = document.querySelector('.log-container');
      if (logContainer && showLogs) {
        logContainer.scrollTo({
          top: logContainer.scrollHeight,
          behavior: 'smooth'
        });
      }
    }, 100);
  }
  
  // Add function to handle input submission
  async function submitUserInput() {
    if (!currentInputRequest || !waitingForInput) return;
    
    try {
      // Add user's response to logs
      logs = [...logs, { 
        type: 'user_response', 
        message: `Your response: ${userResponse}`, 
        raw: userResponse 
      }];
      
      // Send the response to the server
      const response = await fetch(`/api/crew/${crewName}/input`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          id: currentInputRequest.id,
          input: userResponse
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to send your response');
      }
      
      // Reset input state
      waitingForInput = false;
      currentInputRequest = null;
      userResponse = '';
      
    } catch (err) {
      error = err.message;
      console.error('Error sending response:', err);
      logs = [...logs, { type: 'error', message: `Error sending response: ${err.message}` }];
    }
  }
  
  // Add a function to copy result to clipboard
  async function copyResultToClipboard() {
    if (!finalResult) return;
    
    try {
      await navigator.clipboard.writeText(finalResult);
      
      // Show a temporary success message
      const copyButton = document.querySelector('.copy-button');
      if (copyButton) {
        const originalText = copyButton.innerHTML;
        copyButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg> Copied!';
        
        setTimeout(() => {
          copyButton.innerHTML = originalText;
        }, 2000);
      }
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  }
  
  onMount(() => {
    fetchInputVariables();
    
    // Clean up any timers on unmount
    return () => {
      if (timerInterval) clearInterval(timerInterval);
    };
  });
</script>

<main class="container">
  <header class="process-header">
    <div class="title-section">
      <h1>Crew Runtime</h1>
      <div class="process-crew">
        For crew: <a href="/crew/{crewName}">{crewName}</a>
      </div>
    </div>
    <div class="actions">
      <a href="/" class="back-link">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        Back to Crews
      </a>
      <a href="/crew/{crewName}" class="back-link">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 20h9"></path>
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
        </svg>
        Edit Crew
      </a>
    </div>
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
      <p>Loading input variables...</p>
    </div>
  {:else}
    <div class="chat-interface">
      <!-- Input configuration panel -->
      <div class="input-panel">
        <div class="panel-header">
          <h2>Input Variables</h2>
          <div class="panel-description">
            Set the values for input variables used in task descriptions
          </div>
        </div>
        
        <form on:submit|preventDefault={runCrew} class="input-form">
          {#if Object.keys(inputVariables).length === 0}
            <div class="empty-inputs">No input variables found in task descriptions.</div>
          {:else}
            <div class="input-variables-list">
              {#each Object.entries(inputVariables) as [varName, value]}
                <div class="input-item">
                  <label for={`input-${varName}`}>{varName}</label>
                  <textarea 
                    id={`input-${varName}`} 
                    bind:value={inputVariables[varName]} 
                    placeholder="Enter value..."
                    rows="3"
                  ></textarea>
                </div>
              {/each}
            </div>
          {/if}
          
          <div class="input-actions">
            <button type="submit" class="run-btn" disabled={isRunning || Object.keys(inputVariables).length === 0}>
              {#if isRunning}
                <div class="button-spinner"></div>
                Running...
              {:else}
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
                Run Crew
              {/if}
            </button>
          </div>
        </form>
      </div>
      
      <!-- Log output panel -->
      <div class="output-panel">
        {#if finalResult}
          <div class="logs-toggle-bar" on:click={toggleLogs}>
            <div class="toggle-button">
              {#if showLogs}
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="18 15 12 9 6 15"></polyline>
                </svg>
                Hide Logs
              {:else}
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
                Show Logs
              {/if}
            </div>
            <div class="log-summary">
              {logs.length} log entries
            </div>
          </div>
        {/if}
        
        <!-- Log container with animation classes -->
        {#if !finalResult || (finalResult && showLogs)}
          <div class="log-container {finalResult && !showLogs ? 'hidden' : ''}">
            <!-- Add the thinking animation when running -->
            {#if isRunning}
              <div class="thinking-bar">
                <div class="thinking-animation">
                  <span class="dot"></span>
                  <span class="dot"></span>
                  <span class="dot"></span>
                </div>
                <div class="thinking-text">Thinking</div>
                <div class="elapsed-time">{elapsedSeconds}s</div>
              </div>
            {/if}
            
            {#if logs.length === 0}
              <div class="empty-logs">
                No logs yet. Set input variables and run the crew to see execution logs here.
              </div>
            {:else}
              {#each logs as log}
                <div class="log-entry {log.type}">
                  {#if log.type === 'system'}
                    <div class="log-prefix system-prefix">SYSTEM</div>
                  {:else if log.type === 'error'}
                    <div class="log-prefix error-prefix">ERROR</div>
                  {:else if log.type === 'input_request'}
                    <div class="log-prefix input-prefix">INPUT</div>
                  {:else if log.type === 'user_response'}
                    <div class="log-prefix user-prefix">USER</div>
                  {:else}
                    <div class="log-prefix">LOG</div>
                  {/if}
                  <div class="log-message">
                    {@html ansiToHtml(log.message)}
                  </div>
                </div>
              {/each}
              
              <!-- Human input form -->
              {#if waitingForInput && currentInputRequest}
                <div class="human-input-container">
                  <form on:submit|preventDefault={submitUserInput} class="human-input-form">
                    <div class="input-prompt">{currentInputRequest.prompt}</div>
                    <div class="input-field-container">
                      <textarea 
                        bind:value={userResponse}
                        placeholder="Type your response here..."
                        rows="3"
                        autofocus
                      ></textarea>
                      <button type="submit" class="send-response-btn">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <line x1="22" y1="2" x2="11" y2="13"></line>
                          <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                        </svg>
                        Send
                      </button>
                    </div>
                  </form>
                </div>
              {/if}
            {/if}
          </div>
        {/if}
        
        <!-- Result container with animation classes -->
        {#if finalResult}
          <div class="result-container {showLogs ? 'hidden' : 'expanded'}">
            <div class="result-header">
              <h3>Final Result</h3>
              <button class="copy-button" on:click={copyResultToClipboard}>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
                Copy
              </button>
            </div>
            <div class="result-content">
              <div class="markdown-result">
                {@html markdownToHtml(finalResult)}
              </div>
            </div>
          </div>
        {/if}
      </div>
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
  
  .process-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 2.5rem;
  }
  
  .title-section {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .actions {
    display: flex;
    gap: 1rem;
    align-items: center;
  }
  
  h1 {
    font-size: 2.5rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.025em;
    margin: 0;
  }
  
  h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #0f172a;
    margin: 0;
  }
  
  h3 {
    font-size: 1.2rem;
    font-weight: 600;
    color: #0f172a;
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
  }
  
  .back-link:hover {
    color: #3b82f6;
    border-color: #bfdbfe;
    background-color: #f8fafc;
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
  
  .button-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    animation: spin 1s ease-in-out infinite;
    margin-right: 0.5rem;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  /* Chat interface layout */
  .chat-interface {
    display: grid;
    grid-template-columns: 350px 1fr;
    gap: 1.5rem;
    height: calc(100vh - 180px);
    min-height: 500px;
  }
  
  /* Input panel */
  .input-panel {
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    display: flex;
    flex-direction: column;
    border-top: 4px solid #3b82f6;
    overflow: hidden;
  }
  
  .panel-header {
    padding: 1.5rem;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .panel-description {
    margin-top: 0.5rem;
    font-size: 0.85rem;
    color: #64748b;
  }
  
  .input-form {
    display: flex;
    flex-direction: column;
    flex: 1;
    overflow: hidden;
  }
  
  .input-variables-list {
    padding: 1.5rem;
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }
  
  .empty-inputs {
    padding: 2rem 1.5rem;
    color: #94a3b8;
    text-align: center;
    font-style: italic;
  }
  
  .input-item {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .input-item label {
    font-weight: 600;
    font-size: 0.9rem;
    color: #334155;
  }
  
  .input-item textarea {
    padding: 0.75rem;
    border-radius: 6px;
    border: 1px solid #cbd5e1;
    background-color: #f8fafc;
    font-family: inherit;
    font-size: 0.95rem;
    resize: vertical;
    min-height: 80px;
  }
  
  .input-item textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  }
  
  .input-actions {
    padding: 1.25rem;
    border-top: 1px solid #e2e8f0;
    display: flex;
    justify-content: flex-end;
  }
  
  .run-btn {
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
  
  .run-btn:hover {
    background-color: #2563eb;
  }
  
  .run-btn:disabled {
    background-color: #94a3b8;
    cursor: not-allowed;
    box-shadow: none;
  }
  
  /* Output panel */
  .output-panel {
    position: relative;
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    display: flex;
    flex-direction: column;
    border-top: 4px solid #3b82f6;
    overflow: hidden;
  }
  
  /* Log toggle bar animations */
  .logs-toggle-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1.5rem;
    background-color: #f1f5f9;
    cursor: pointer;
    border-bottom: 1px solid #e2e8f0;
    user-select: none;
    transition: background-color 0.2s;
    z-index: 5;
  }
  
  .logs-toggle-bar:hover {
    background-color: #e2e8f0;
  }
  
  .toggle-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 500;
    color: #334155;
  }
  
  .log-summary {
    font-size: 0.85rem;
    color: #64748b;
  }
  
  /* Log container with animations */
  .log-container {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    font-family: "Menlo", "Monaco", "Courier New", monospace;
    font-size: 0.85rem;
    background-color: #0f172a;
    color: #e2e8f0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    opacity: 1;
    transform: translateY(0);
    transition: opacity 0.4s ease, transform 0.4s ease;
  }
  
  .log-container.animating-out {
    opacity: 0;
    transform: translateY(-20px);
  }
  
  .log-container.animating-in {
    opacity: 0;
    transform: translateY(20px);
    animation: fade-slide-down 0.3s forwards;
  }
  
  .log-container.hidden {
    display: none;
  }
  
  .empty-logs {
    padding: 2rem;
    text-align: center;
    color: #94a3b8;
    font-style: italic;
    font-family: inherit;
  }
  
  .log-entry {
    display: flex;
    gap: 0.75rem;
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    line-height: 1.5;
  }
  
  .log-prefix {
    font-weight: bold;
    color: #3b82f6;
    min-width: 60px;
  }
  
  .system-prefix {
    color: #a3e635;
  }
  
  .error-prefix {
    color: #ef4444;
  }
  
  .log-entry.error {
    background-color: rgba(239, 68, 68, 0.1);
    border-left: 3px solid #ef4444;
  }
  
  .log-entry.system {
    background-color: rgba(163, 230, 53, 0.1);
    border-left: 3px solid #a3e635;
  }
  
  .log-message {
    white-space: pre-wrap;
    word-break: break-word;
    flex: 1;
  }
  
  /* Result container with animations */
  .result-container {
    border-top: 1px solid #e2e8f0;
    display: flex;
    flex-direction: column;
    opacity: 1;
    transform: translateY(0);
    transition: opacity 0.4s ease, transform 0.4s ease;
  }
  
  .result-container.animating-out {
    opacity: 0;
    transform: translateY(-20px);
  }
  
  .result-container.animating-in {
    opacity: 0;
    transform: translateY(20px);
    animation: fade-slide-up 0.3s forwards;
  }
  
  .result-container.hidden {
    display: none;
  }
  
  .result-container.expanded .result-content {
    max-height: calc(100vh - 280px);
    flex: 1;
    overflow-y: auto;
  }
  
  .result-container.expanded .result-content {
    max-height: calc(100vh - 280px);
    flex: 1;
  }
  
  .result-content {
    padding: 1.5rem;
    max-height: 300px;
    overflow-y: auto;
    background-color: #f8fafc;
    transition: max-height 0.3s ease;
  }
  
  .result-header {
    padding: 1rem 1.5rem;
    background-color: #f1f5f9;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .result-content {
    padding: 1.5rem;
    max-height: 300px;
    overflow-y: auto;
    background-color: #f8fafc;
    transition: max-height 0.3s ease;
  }
  
  .result-content pre {
    margin: 0;
    font-family: "Menlo", "Monaco", "Courier New", monospace;
    font-size: 0.9rem;
    white-space: pre-wrap;
    word-break: break-word;
    line-height: 1.6;
    background-color: #f1f5f9;
    padding: 1rem;
    border-radius: 6px;
  }
  
  .markdown-result {
    line-height: 1.6;
    color: #334155;
  }
  
  .markdown-result h1, 
  .markdown-result h2, 
  .markdown-result h3 {
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
  }
  
  .markdown-result h1 {
    font-size: 1.8rem;
  }
  
  .markdown-result h2 {
    font-size: 1.5rem;
  }
  
  .markdown-result h3 {
    font-size: 1.2rem;
  }
  
  .markdown-result ul, 
  .markdown-result ol {
    padding-left: 1.5rem;
    margin: 1rem 0;
  }
  
  .markdown-result li {
    margin-bottom: 0.5rem;
  }
  
  .markdown-result a {
    color: #3b82f6;
    text-decoration: none;
  }
  
  .markdown-result a:hover {
    text-decoration: underline;
  }
  
  .markdown-result code {
    font-family: "Menlo", "Monaco", "Courier New", monospace;
    background-color: #f1f5f9;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-size: 0.85em;
  }
  
  @media (max-width: 768px) {
    .container {
      padding: 1rem;
    }
    
    .chat-interface {
      grid-template-columns: 1fr;
      height: auto;
    }
    
    .process-header {
      flex-direction: column;
      gap: 1rem;
    }
    
    .actions {
      width: 100%;
      justify-content: flex-end;
    }
    
    .log-container, .result-content {
      max-height: 350px;
    }
  }
  
  /* ANSI color styles */
  .ansi-bold {
    font-weight: bold;
  }
  
  .ansi-black { color: #000000; }
  .ansi-red { color: #e74c3c; }
  .ansi-green { color: #2ecc71; }
  .ansi-yellow { color: #f1c40f; }
  .ansi-blue { color: #3498db; }
  .ansi-magenta { color: #9b59b6; }
  .ansi-cyan { color: #1abc9c; }
  .ansi-white { color: #ecf0f1; }
  
  .ansi-bg-black { background-color: #000000; }
  .ansi-bg-red { background-color: rgba(231, 76, 60, 0.2); }
  .ansi-bg-green { background-color: rgba(46, 204, 113, 0.2); }
  .ansi-bg-yellow { background-color: rgba(241, 196, 15, 0.2); }
  .ansi-bg-blue { background-color: rgba(52, 152, 219, 0.2); }
  
  /* Animation keyframes */
  @keyframes fade-slide-up {
    0% {
      opacity: 0;
      transform: translateY(20px);
    }
    100% {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  @keyframes fade-slide-down {
    0% {
      opacity: 0;
      transform: translateY(-20px);
    }
    100% {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  /* Thinking animation styles */
  .thinking-bar {
    position: sticky;
    top: 0;
    background-color: #1a2234;
    padding: 0.75rem 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: 6px;
    margin-bottom: 0.75rem;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
    z-index: 10;
  }
  
  .thinking-animation {
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }
  
  .dot {
    width: 8px;
    height: 8px;
    background-color: #60a5fa;
    border-radius: 50%;
    animation: pulse 1.5s infinite ease-in-out;
  }
  
  .dot:nth-child(2) {
    animation-delay: 0.3s;
  }
  
  .dot:nth-child(3) {
    animation-delay: 0.6s;
  }
  
  .thinking-text {
    font-weight: 600;
    color: #a3e635;
    margin-left: 0.75rem;
  }
  
  .elapsed-time {
    color: #94a3b8;
    font-family: "Menlo", "Monaco", "Courier New", monospace;
    font-size: 0.8rem;
    background-color: rgba(15, 23, 42, 0.5);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
  }
  
  @keyframes pulse {
    0%, 100% {
      transform: scale(1);
      opacity: 0.5;
    }
    50% {
      transform: scale(1.3);
      opacity: 1;
    }
  }
  
  /* Human Input styles */
  .log-entry.input_request {
    background-color: rgba(14, 165, 233, 0.1);
    border-left: 3px solid #0ea5e9;
  }
  
  .log-entry.user_response {
    background-color: rgba(168, 85, 247, 0.1);
    border-left: 3px solid #a855f7;
  }
  
  .input-prefix {
    color: #0ea5e9;
  }
  
  .user-prefix {
    color: #a855f7;
  }
  
  .human-input-container {
    margin: 1rem 0;
    padding: 1rem;
    background-color: #1e293b;
    border-radius: 8px;
    border: 1px solid #475569;
  }
  
  .human-input-form {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .input-prompt {
    font-weight: 500;
    color: #f1f5f9;
    border-left: 3px solid #0ea5e9;
    padding-left: 0.75rem;
  }
  
  .input-field-container {
    display: flex;
    gap: 0.5rem;
  }
  
  .human-input-form textarea {
    flex: 1;
    padding: 0.75rem;
    border-radius: 6px;
    border: 1px solid #475569;
    background-color: #0f172a;
    color: #f1f5f9;
    font-family: inherit;
    font-size: 0.95rem;
    resize: vertical;
    min-height: 60px;
  }
  
  .human-input-form textarea:focus {
    outline: none;
    border-color: #38bdf8;
    box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
  }
  
  .send-response-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background-color: #0ea5e9;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.9rem;
    cursor: pointer;
    transition: background-color 0.2s;
    align-self: flex-end;
  }
  
  .send-response-btn:hover {
    background-color: #0284c7;
  }
  
  /* Add styling for the copy button */
  .copy-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
    background-color: #f8fafc;
    color: #475569;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .copy-button:hover {
    background-color: #f1f5f9;
    border-color: #94a3b8;
    color: #334155;
  }
  
  .copy-button:active {
    transform: translateY(1px);
  }
</style>
