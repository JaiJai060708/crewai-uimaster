import os
import yaml
import queue
import threading
import json
import re

from flask import Flask, jsonify, request, Response
from contextlib import redirect_stdout

from human_input_tool import input_queues
from crewai_helpers import run_crewai

app = Flask(__name__)

CREWS_DIR = "crews_yaml_files"
CONFIG_DIR = "config"

# if the folder crews does not exist, create it
if not os.path.exists(os.path.join(os.path.dirname(__file__), CREWS_DIR)):
    os.makedirs(os.path.join(os.path.dirname(__file__), CREWS_DIR))

@app.route('/api', strict_slashes=False)
def home():
    return jsonify({"message": "Hello from Flask!"})

@app.route('/api/tools', methods=['GET'], strict_slashes=False)
def list_tools():
    try:
        tools_path = os.path.join(os.path.dirname(__file__), CONFIG_DIR, 'crewai_tools_config.json')
        with open(tools_path, 'r') as f:
            tools_data = json.load(f)
        return jsonify(tools_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/models', methods=['GET'], strict_slashes=False)
def list_models():
    try:
        models_path = os.path.join(os.path.dirname(__file__), CONFIG_DIR, 'crewai_models_config.json')
        with open(models_path, 'r') as f:
            models_data = json.load(f)
        return jsonify(models_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/list-crews', methods=['GET'], strict_slashes=False)
def list_crews():
    try:
        crews_path = os.path.join(os.path.dirname(__file__), CREWS_DIR)
        crews = [d for d in os.listdir(crews_path) if os.path.isdir(os.path.join(crews_path, d))]
        return jsonify(crews)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/crew/<crew_name>/agents', methods=['GET', 'PUT'], strict_slashes=False)
def crew_agents(crew_name):
    agents_file = os.path.join(os.path.dirname(__file__), CREWS_DIR, crew_name, 'agents.yaml')
    
    if request.method == 'GET':
        try:
            if not os.path.exists(agents_file):
                return jsonify({"error": f"Agents file not found for crew '{crew_name}'"}), 404
                
            with open(agents_file, 'r') as f:
                agents_data = yaml.safe_load(f)
                
            return jsonify({
                "agents": agents_data
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            # Ensure crew directory exists
            crew_dir = os.path.join(os.path.dirname(__file__), CREWS_DIR, crew_name)
            if not os.path.exists(crew_dir):
                os.makedirs(crew_dir)
                
            # Get the data from request
            agents_data = request.json
            
            if not agents_data or "agents" not in agents_data:
                return jsonify({"error": "Invalid data format. Expected 'agents' field"}), 400
                
            # Write the agents data to the YAML file
            with open(agents_file, 'w') as f:
                yaml.dump(agents_data["agents"], f, default_flow_style=False)
                
            return jsonify({
                "message": f"Agents for crew '{crew_name}' updated successfully",
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/crew/<crew_name>/tasks', methods=['GET', 'PUT'], strict_slashes=False)
def crew_tasks(crew_name):
    tasks_file = os.path.join(os.path.dirname(__file__), CREWS_DIR, crew_name, 'tasks.yaml')
    
    if request.method == 'GET':
        try:
            if not os.path.exists(tasks_file):
                return jsonify({"error": f"Tasks file not found for crew '{crew_name}'"}), 404
                
            with open(tasks_file, 'r') as f:
                tasks_data = yaml.safe_load(f)
                
            return jsonify({
                "tasks": tasks_data
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            # Ensure crew directory exists
            crew_dir = os.path.join(os.path.dirname(__file__), CREWS_DIR, crew_name)
            if not os.path.exists(crew_dir):
                os.makedirs(crew_dir)
                
            # Get the data from request
            tasks_data = request.json
            
            if not tasks_data or "tasks" not in tasks_data:
                return jsonify({"error": "Invalid data format. Expected 'tasks' field"}), 400
                
            # Write the tasks data to the YAML file
            with open(tasks_file, 'w') as f:
                yaml.dump(tasks_data["tasks"], f, default_flow_style=False)
                
            return jsonify({
                "message": f"Tasks for crew '{crew_name}' updated successfully",
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/crew/<crew_name>/process', methods=['GET', 'PUT'], strict_slashes=False)
def crew_process(crew_name):
    process_file = os.path.join(os.path.dirname(__file__), CREWS_DIR, crew_name, 'process.yaml')
    
    if request.method == 'GET':
        try:
            if not os.path.exists(process_file):
                return jsonify({"error": f"Process file not found for crew '{crew_name}'"}), 404
                
            with open(process_file, 'r') as f:
                process_data = yaml.safe_load(f)
                
            return jsonify({
                "name": crew_name,
                "process": process_data
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            # Ensure crew directory exists
            crew_dir = os.path.join(os.path.dirname(__file__), CREWS_DIR, crew_name)
            if not os.path.exists(crew_dir):
                os.makedirs(crew_dir)
                
            # Get the data from request
            process_data = request.json
            
            if not process_data or "process" not in process_data:
                return jsonify({"error": "Invalid data format. Expected 'process' field"}), 400
                
            # Write the process data to the YAML file
            with open(process_file, 'w') as f:
                yaml.dump(process_data["process"], f, default_flow_style=False)
                
            return jsonify({
                "message": f"Process for crew '{crew_name}' updated successfully",
                "name": crew_name
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/crew/<crew_name>', methods=['POST', 'DELETE'], strict_slashes=False)
def manage_crew(crew_name):
    print(f"Managing crew: {crew_name}")
    crew_dir = os.path.join(os.path.dirname(__file__), CREWS_DIR, crew_name)
    
    if request.method == 'POST':
        # Check if the request contains a new name
        data = request.json
        if data and "new_name" in data:
            new_name = data["new_name"]
            new_crew_dir = os.path.join(os.path.dirname(__file__), CREWS_DIR, new_name)

            # Rename the crew directory
            if os.path.exists(crew_dir):
                os.rename(crew_dir, new_crew_dir)
                return jsonify({"message": f"Crew renamed to '{new_name}' successfully"}), 200
            else:
                return jsonify({"error": f"Crew '{crew_name}' not found"}), 404

        # Check if the crew folder already exists
        if os.path.exists(crew_dir):
            return jsonify({"error": f"Crew '{crew_name}' already exists"}), 409
            
        # Create crew directory
        os.makedirs(crew_dir)
        
        # Create empty template files with proper structure
        
        # Create empty process.yaml
        process_data = {
            "crew": {
                "process": "",
                "agents": [],
                "tasks": []
            }
        }
        with open(os.path.join(crew_dir, 'process.yaml'), 'w') as f:
            yaml.dump(process_data, f, default_flow_style=False)
        
        # Create empty agents.yaml
        agents_data = {}
        with open(os.path.join(crew_dir, 'agents.yaml'), 'w') as f:
            yaml.dump(agents_data, f, default_flow_style=False)
        
        # Create empty tasks.yaml
        tasks_data = {}
        with open(os.path.join(crew_dir, 'tasks.yaml'), 'w') as f:
            yaml.dump(tasks_data, f, default_flow_style=False)
            
        return jsonify({
            "message": f"Crew '{crew_name}' created successfully",
            "name": crew_name
        }), 201
    
    elif request.method == 'DELETE':
        try:
            # Check if the crew folder exists
            if not os.path.exists(crew_dir):
                return jsonify({"error": f"Crew '{crew_name}' not found"}), 404
                
            # Delete all files in the crew directory
            for file in os.listdir(crew_dir):
                file_path = os.path.join(crew_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            # Delete the directory itself
            os.rmdir(crew_dir)
                
            return jsonify({
                "message": f"Crew '{crew_name}' deleted successfully"
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        


@app.route('/api/crew/<crew_name>/run', methods=['POST'], strict_slashes=False)
def run_crew(crew_name):
    crew_dir = os.path.join(os.path.dirname(__file__), CREWS_DIR, crew_name)

    try:
        # Load process.yaml, agents.yaml, tasks.yaml as before
        process_file = os.path.join(crew_dir, 'process.yaml')
        if not os.path.exists(process_file):
            return jsonify({"error": f"Process file not found for crew '{crew_name}'"}), 404
        with open(process_file, 'r') as f:
            process_data = yaml.safe_load(f)

        agents_file = os.path.join(crew_dir, 'agents.yaml')
        if not os.path.exists(agents_file):
            return jsonify({"error": f"Agents file not found for crew '{crew_name}'"}), 404
        with open(agents_file, 'r') as f:
            agents_data = yaml.safe_load(f)

        tasks_file = os.path.join(crew_dir, 'tasks.yaml')
        if not os.path.exists(tasks_file):
            return jsonify({"error": f"Tasks file not found for crew '{crew_name}'"}), 404
        with open(tasks_file, 'r') as f:
            tasks_data = yaml.safe_load(f)

        input_args = request.json or {}

        # Create log_queue before calling run_crewai
        log_queue = queue.Queue()


        
        # Pass log_queue to run_crewai
        result = run_crewai(process_data, agents_data, tasks_data, input_args, log_queue)
        if isinstance(result, dict) and "error" in result:
            return jsonify(result), 400
        crew = result

        # LogStream class and kickoff thread setup remain unchanged
        class LogStream:
            def __init__(self, queue):
                self.queue = queue

            def write(self, message):
                if message.strip():
                    self.queue.put({"type": "log", "message": message.strip()})

            def flush(self):
                pass

        log_stream = LogStream(log_queue)

        def run_kickoff():
            with redirect_stdout(log_stream):
                try:
                    result = crew.kickoff(inputs=input_args)
                    log_queue.put({"type": "final_result", "result": str(result)})
                except Exception as e:
                    log_queue.put({"type": "error", "message": str(e)})

        thread = threading.Thread(target=run_kickoff)
        thread.start()

        def generate():
            while thread.is_alive() or not log_queue.empty():
                try:
                    message = log_queue.get(timeout=1)
                    yield json.dumps(message) + "\n"
                except queue.Empty:
                    continue

        return Response(generate(), mimetype='application/x-ndjson')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/crew/<crew_name>/input', methods=['POST'], strict_slashes=False)
def provide_input(crew_name):
    """Endpoint to receive user input from the client."""
    data = request.json
    if not data or "id" not in data or "input" not in data:
        return jsonify({"error": "Invalid request. Expected 'id' and 'input' fields"}), 400
    
    unique_id = data["id"]
    user_input = data["input"]
    
    if unique_id in input_queues:
        input_queues[unique_id].put(user_input)
        return jsonify({"message": "Input received"})
    else:
        return jsonify({"error": "Invalid or expired input ID"}), 404

@app.route('/api/crew/<crew_name>/rename', methods=['POST'], strict_slashes=False)
def rename_crew(crew_name):
    """Endpoint to rename a crew."""
    try:
        data = request.json
        if not data or "new_name" not in data:
            return jsonify({"error": "Missing 'new_name' field"}), 400
            
        new_name = data["new_name"]
        
        # Validate new name
        if not new_name or not new_name.strip():
            return jsonify({"error": "Crew name cannot be empty"}), 400
            
        # Check if name contains only allowed characters
        if not re.match(r'^[a-zA-Z0-9_]+$', new_name):
            return jsonify({"error": "Crew name can only contain letters, numbers, and underscores"}), 400
        
        # Check if new name already exists
        crews_path = os.path.join(os.path.dirname(__file__), CREWS_DIR)
        if os.path.exists(os.path.join(crews_path, new_name)):
            return jsonify({"error": f"A crew named '{new_name}' already exists"}), 409
            
        # Get the paths of the old and new crew directories
        old_crew_dir = os.path.join(crews_path, crew_name)
        new_crew_dir = os.path.join(crews_path, new_name)
        
        # Check if the old crew exists
        if not os.path.exists(old_crew_dir):
            return jsonify({"error": f"Crew '{crew_name}' not found"}), 404
            
        # Rename the crew directory
        os.rename(old_crew_dir, new_crew_dir)
        
        return jsonify({
            "message": f"Crew renamed from '{crew_name}' to '{new_name}' successfully",
            "old_name": crew_name,
            "new_name": new_name
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=3002)