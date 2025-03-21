<script>
  import { onMount } from 'svelte';
  
  let crews = [];
  let newCrewName = '';
  let loading = true;
  let error = null;
  let errorTimeout;
  
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
  
  // Fetch the list of crews from the API
  async function fetchCrews() {
    loading = true;
    setError(null);
    try {
      const response = await fetch('/api/list-crews');
      if (!response.ok) throw new Error('Failed to fetch crews');
      crews = await response.json();
    } catch (err) {
      setError(err.message);
      console.error('Error fetching crews:', err);
    } finally {
      loading = false;
    }
  }
  
  // Create a new crew
  async function createCrew() {
    if (!newCrewName.trim()) return;
    
    // Validate crew name format - only allow letters, numbers, and underscores
    if (!/^[a-zA-Z0-9_]+$/.test(newCrewName)) {
      setError("Crew name can only contain letters, numbers, and underscores (_)");
      return;
    }
    
    try {
      const response = await fetch(`/api/crew/${newCrewName}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to create crew');
      }
      
      // Refresh the crew list
      await fetchCrews();
      newCrewName = '';
    } catch (err) {
      setError(err.message);
      console.error('Error creating crew:', err);
    }
  }
  
  // Delete a crew
  async function deleteCrew(crewName) {
    if (!confirm(`Are you sure you want to delete "${crewName}"?`)) return;
    
    try {
      const response = await fetch(`/api/crew/${crewName}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to delete crew');
      }
      
      // Refresh the crew list
      await fetchCrews();
    } catch (err) {
      setError(err.message);
      console.error('Error deleting crew:', err);
    }
  }
  
  // Load crews when the component mounts and cleanup on destroy
  onMount(() => {
    fetchCrews();
    
    // Cleanup function
    return () => {
      clearTimeout(errorTimeout);
    };
  });
</script>

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

<main class="container">
  <h1>Crew Management</h1>
  
  <section class="create-crew-section">
    <h2>Create New Crew</h2>
    <div class="form-group">
      <input 
        type="text" 
        bind:value={newCrewName} 
        placeholder="Enter crew name" 
        on:keydown={(e) => e.key === 'Enter' && createCrew()}
      />
      <button class="primary-button" on:click={createCrew}>
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        Create
      </button>
    </div>
  </section>
  
  <section class="crew-list-section">
    <h2>Your Teams</h2>
    
    {#if loading}
      <div class="loading-container">
        <div class="loading-spinner"></div>
        <p>Loading teams...</p>
      </div>
    {:else if crews.length === 0}
      <div class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <p>No teams found. Create your first team above!</p>
      </div>
    {:else}
      <ul class="crew-grid">
        {#each crews as crew}
          <li class="crew-card">
            <a href="/crew/{crew}/runtime" class="crew-card-link">
              <div class="crew-card-content">
                <div class="crew-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                    <circle cx="9" cy="7" r="4"></circle>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                  </svg>
                </div>
                <div class="crew-name">{crew}</div>
              </div>
            </a>
            <div class="crew-actions">
              <a href="/crew/{crew}" class="edit-button">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
                <span>Edit</span>
              </a>
            </div>
          </li>
        {/each}
      </ul>
    {/if}
  </section>
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
  
  h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 2.5rem;
    color: #0f172a;
    text-align: center;
    letter-spacing: -0.025em;
  }
  
  h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1.25rem;
    color: #0f172a;
    letter-spacing: -0.015em;
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
    border-left: none;
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
  
  .create-crew-section {
    border-top: 4px solid #3b82f6;
  }
  
  .form-group {
    display: flex;
    gap: 0.75rem;
  }
  
  input {
    flex: 1;
    padding: 0.75rem 1rem;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 1rem;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  }
  
  input:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  }
  
  .primary-button {
    padding: 0.75rem 1.5rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: background-color 0.2s, transform 0.1s;
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
  }
  
  .primary-button:hover {
    background-color: #2563eb;
  }
  
  .primary-button:active {
    transform: translateY(1px);
  }
  
  .delete-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background-color: rgba(239, 68, 68, 0.1);
    color: #ef4444;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    transition: background-color 0.2s;
  }
  
  .delete-button:hover {
    background-color: rgba(239, 68, 68, 0.15);
  }
  
  .crew-grid {
    list-style-type: none;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1.5rem;
  }
  
  .crew-card {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background-color: #ffffff;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.04);
    transition: transform 0.2s, box-shadow 0.2s;
    border: 1px solid #e2e8f0;
    height: 100%;
  }
  
  .crew-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  }
  
  .crew-card-content {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    flex-grow: 1;
  }
  
  .crew-icon {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background-color: #eef2ff;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1rem;
    color: #4f46e5;
  }
  
  .crew-name {
    font-size: 1.25rem;
    color: #0f172a;
    text-decoration: none;
    font-weight: 600;
    margin-top: 0.5rem;
    transition: color 0.2s;
  }
  
  .crew-name:hover {
    color: #3b82f6;
  }
  
  .crew-actions {
    padding: 1rem;
    border-top: 1px solid #e2e8f0;
    display: flex;
    justify-content: flex-end;
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
    padding: 3rem 0;
    color: #64748b;
  }
  
  .empty-state svg {
    color: #94a3b8;
    margin-bottom: 1rem;
  }
  
  @media (max-width: 768px) {
    .crew-grid {
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    }
    
    .container {
      padding: 1.5rem;
    }
  }
  
  @media (max-width: 480px) {
    .crew-grid {
      grid-template-columns: 1fr;
    }
    
    h1 {
      font-size: 2rem;
    }
    
    .form-group {
      flex-direction: column;
    }
    
    .primary-button {
      width: 100%;
      justify-content: center;
    }
  }
  
  .crew-card-link {
    display: block;
    text-decoration: none;
    flex-grow: 1;
  }
  
  .edit-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background-color: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    transition: background-color 0.2s;
    text-decoration: none;
  }
  
  .edit-button:hover {
    background-color: rgba(59, 130, 246, 0.15);
  }
</style>
