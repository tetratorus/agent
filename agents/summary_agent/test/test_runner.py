import os
import json
from ..agent import SummaryAgent

def load_manifest():
    manifest_path = os.path.join(os.path.dirname(__file__), "../variables/manifest.json")
    with open(manifest_path, 'r') as f:
        return json.load(f)["manifesto"]

def load_input_text():
    input_path = os.path.join(os.path.dirname(__file__), "../variables/input_text.json")
    with open(input_path, 'r') as f:
        return json.load(f)["text"]

def main():
    # Read manifest from JSON file
    manifest = load_manifest()

    # Initialize and run the agent
    agent = SummaryAgent(
        manifesto=manifest,
        memory=""
    )
    result = agent.run()
    print("Final Result:", result)

if __name__ == "__main__":
    main()
