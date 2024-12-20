import os
import json
from ..agent import ToolGenerationAgent

def main():
    # Read manifesto from variables directory
    variables_dir = os.path.join(os.path.dirname(__file__), "../variables")

    with open(os.path.join(variables_dir, "manifesto.json")) as f:
        manifesto = json.load(f)[0]

    # Initialize and run the agent
    agent = ToolGenerationAgent(
        manifesto=manifesto,
        memory=""
    )
    result = agent.run()
    print("Final Result:", result)

if __name__ == "__main__":
    main()
