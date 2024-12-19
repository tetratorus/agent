import os
import json
from ..agent import TextSummaryAgent

def main():
    # Read from JSON files in variables directory
    variables_dir = os.path.join(os.path.dirname(__file__), "../variables")

    with open(os.path.join(variables_dir, "text.json")) as f:
        text = json.load(f)["text"]

    with open(os.path.join(variables_dir, "manifesto.json")) as f:
        manifesto = json.load(f)["manifesto"]

    # Initialize and run the agent
    agent = TextSummaryAgent(
        manifesto=manifesto,
        memory="",
        text=text,
        target_length=1000
    )
    result = agent.run()
    print("Final Result:", result)

if __name__ == "__main__":
    main()
