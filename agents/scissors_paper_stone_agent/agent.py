# Agent Implementation for Scissors Paper Stone Game

from lib.base import Agent
from lib.tools import list_tools

class ScissorsPaperStoneAgent(Agent):
    def __init__(self, manifesto: str, memory: str):
        super().__init__(manifesto=manifesto, memory=memory, tools={"LIST_TOOLS": list_tools})
        self.past_moves = []

    def update_strategy(self, user_move: str):
        # Analyze past moves and update strategy
        self.past_moves.append(user_move)

    def predict_user_move(self) -> str:
        # Predict user's move based on past moves (simple heuristic for illustration)
        if not self.past_moves:
            return "stone"  # Default move
        last_move = self.past_moves[-1]
        # Simple prediction: if user played 'stone' last, predict 'scissors' next
        return {"stone": "scissors", "scissors": "paper", "paper": "stone"}[last_move]

    def play(self, user_move: str) -> str:
        self.update_strategy(user_move)
        predicted_move = self.predict_user_move()
        return {"scissors": "rock", "paper": "scissors", "rock": "paper"}[predicted_move]

agent = ScissorsPaperStoneAgent(
    manifesto="You are a scissors paper stone agent designed to play the game with the user, aiming to predict and counter the user's moves.",
    memory=""
)

agent.run()
