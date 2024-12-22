import os
import sys
import json
import time
import datetime
from typing import Dict, Any, TextIO

from ...agent import ResearchAgent

class StreamingLogger:
    """Logger that writes to both file and stdout in real-time."""
    def __init__(self, log_file: TextIO):
        self.terminal = sys.stdout
        self.log_file = log_file
    
    def write(self, message: str):
        self.terminal.write(message)
        self.log_file.write(message)
        # Flush both to ensure real-time output
        self.terminal.flush()
        self.log_file.flush()
    
    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

def create_run_folder() -> str:
    """Create a timestamped folder for this run."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(os.path.dirname(__file__), "logs", f"run_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    return run_dir

def load_variables() -> Dict[str, Any]:
    """Load variables from JSON files."""
    var_dir = os.path.join(os.path.dirname(__file__), "..", "variables")
    variables = {}
    
    for filename in os.listdir(var_dir):
        if filename.endswith('.json'):
            var_name = filename[:-5]  # Remove .json
            with open(os.path.join(var_dir, filename)) as f:
                variables[var_name] = json.load(f)[0]  # Take first element for now
    
    return variables

def run_agent(variables: Dict[str, Any], run_dir: str) -> None:
    """Run the agent and capture all output."""
    # Open log file for streaming
    with open(os.path.join(run_dir, "debug.log"), "w") as log_file:
        # Redirect stdout to our streaming logger
        sys.stdout = StreamingLogger(log_file)
        
        try:
            agent = ResearchAgent(
                manifesto=variables["manifesto"],
                memory=variables["memory"]
            )
            result = agent.run()
            
            # Save variables used
            with open(os.path.join(run_dir, "variables.json"), "w") as f:
                json.dump(variables, f, indent=2)
            
            # Save result
            with open(os.path.join(run_dir, "result.json"), "w") as f:
                json.dump({"result": result}, f, indent=2)
                
        finally:
            # Restore stdout
            sys.stdout = sys.__stdout__

def main():
    # Create run folder
    run_dir = create_run_folder()
    
    # Load variables
    variables = load_variables()
    
    # Run agent
    run_agent(variables, run_dir)
    
    print(f"Run completed. Logs saved to: {run_dir}")

if __name__ == "__main__":
    main()
