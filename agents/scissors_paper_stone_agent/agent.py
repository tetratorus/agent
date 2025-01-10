from lib.base import Agent
import random

class RockPaperScissorsAgent(Agent):
    def __init__(self, manifesto: str, memory: str):
        super().__init__(manifesto, memory)
        self.history = []
        self.tools.update({
            "STORE_MOVE": self.store_move,
            "RETRIEVE_MOVE": self.retrieve_move,
        })
        self.current_move = None

    def store_move(self, move: str) -> str:
        self.current_move = move
        return "Move stored."

    def retrieve_move(self, _: str) -> str:
        return self.current_move

    def tool_method_name(self, input: str) -> str:
        pass  # Placeholder for future tool methods if needed
