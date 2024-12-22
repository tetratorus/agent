import os
import json
from ..agent import ResearchAgent

def main():
    # Read from JSON files in variables directory
    variables_dir = os.path.join(os.path.dirname(__file__), "../variables")

    with open(os.path.join(variables_dir, "research_topic.json")) as f:
        research_topic = json.load(f)[0]

    with open(os.path.join(variables_dir, "manifesto.json")) as f:
        manifesto = json.load(f)[0]

    with open(os.path.join(variables_dir, "memory.json")) as f:
        memory = json.load(f)[0]

    # Initialize and run the agent
    agent = ResearchAgent(
        research_topic=research_topic,
        manifesto=manifesto,
        memory=memory
    )
    result = agent.run()
    print("Final Result:", result)

if __name__ == "__main__":
    main()
