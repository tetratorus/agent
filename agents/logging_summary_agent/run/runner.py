import os
import json
from ..agent import LoggingSummaryAgent

def main():
    # Read from JSON files in variables directory
    variables_dir = os.path.join(os.path.dirname(__file__), "../variables")

    with open(os.path.join(variables_dir, "logs.json")) as f:
        logs = json.load(f)[0]

    with open(os.path.join(variables_dir, "manifesto.json")) as f:
        manifesto = json.load(f)[0]

    # Initialize and run the agent
    agent = LoggingSummaryAgent(
        manifesto=manifesto,
        memory="",
        logs=logs
    )
    result = agent.run()
    print("Analysis Results:", result)

if __name__ == "__main__":
    main()
