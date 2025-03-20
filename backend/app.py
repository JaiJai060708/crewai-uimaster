from flask import Flask, jsonify, request
import os
import yaml
from crewai_helpers import run_crewai

app = Flask(__name__)

@app.route('/api', strict_slashes=False)
def home():
    return jsonify({"message": "Hello from Flask!"})

@app.route('/api/list-crews', methods=['GET'], strict_slashes=False)
def list_crews():
    try:
        crews_path = os.path.join(os.path.dirname(__file__), 'crews')
        crews = [d for d in os.listdir(crews_path) if os.path.isdir(os.path.join(crews_path, d))]
        return jsonify(crews)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/crew/<crew_name>/agents', methods=['GET', 'PUT'], strict_slashes=False)
def crew_agents(crew_name):
    agents_file = os.path.join(os.path.dirname(__file__), 'crews', crew_name, 'agents.yaml')
    
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
            crew_dir = os.path.join(os.path.dirname(__file__), 'crews', crew_name)
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
    tasks_file = os.path.join(os.path.dirname(__file__), 'crews', crew_name, 'tasks.yaml')
    
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
            crew_dir = os.path.join(os.path.dirname(__file__), 'crews', crew_name)
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
    process_file = os.path.join(os.path.dirname(__file__), 'crews', crew_name, 'process.yaml')
    
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
            crew_dir = os.path.join(os.path.dirname(__file__), 'crews', crew_name)
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
    crew_dir = os.path.join(os.path.dirname(__file__), 'crews', crew_name)
    
    if request.method == 'POST':
        try:
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
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
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
    crew_dir = os.path.join(os.path.dirname(__file__), 'crews', crew_name)
    
    if request.method == 'POST':
        try:
            # Read the process.yaml file
            process_file = os.path.join(crew_dir, 'process.yaml')
            if not os.path.exists(process_file):
                return jsonify({"error": f"Process file not found for crew '{crew_name}'"}), 404
                
            with open(process_file, 'r') as f:
                process_data = yaml.safe_load(f)

            # Read the agents.yaml file
            agents_file = os.path.join(crew_dir, 'agents.yaml')
            if not os.path.exists(agents_file):
                return jsonify({"error": f"Agents file not found for crew '{crew_name}'"}), 404
                
            with open(agents_file, 'r') as f:
                agents_data = yaml.safe_load(f)

            # Read the tasks.yaml file
            tasks_file = os.path.join(crew_dir, 'tasks.yaml')
            if not os.path.exists(tasks_file):
                return jsonify({"error": f"Tasks file not found for crew '{crew_name}'"}), 404
                
            with open(tasks_file, 'r') as f:
                tasks_data = yaml.safe_load(f)

            # Get the input arguments from the request
            input_args = request.json
            print(input_args)

            return run_crewai(process_data, agents_data, tasks_data, input_args)

        except Exception as e:
            return jsonify({"error": str(e)}), 500
                
                
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=5000)
