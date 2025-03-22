from crewai.tools import BaseTool
import uuid
from queue import Queue
from pydantic import Extra

# Global dictionary to store input queues, accessible across threads
input_queues = {}

class HumanInputTool(BaseTool):
    name: str = "HumanInputTool"
    description: str = "Prompts the user for additional input during crew execution."

    class Config:
        extra = Extra.allow

    def __init__(self, log_queue: Queue):
        """Initialize the tool."""
        super().__init__()
        self.log_queue = log_queue


    def _run(self, prompt: str) -> str:
        """Request input from the client and wait for the response."""
        
        # Generate a unique ID for this input request
        unique_id = str(uuid.uuid4())

        # Send a message to the client via the log_queue
        self.log_queue.put({
            "type": "input_required",
            "id": unique_id,
            "prompt": prompt
        })
        
        # Create a queue to receive the user's input
        input_queue = Queue()
        input_queues[unique_id] = input_queue

        # Wait for the client to provide input (blocks until input is received)
        user_input = input_queue.get()
        
        # Clean up the input queue entry
        del input_queues[unique_id]
        
        return user_input