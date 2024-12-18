from typing import Dict, Optional, Callable, Tuple
from lib.debug import debug
from lib.base import Agent

class SentimentAnalysisAgent(Agent):
    """An agent specialized for analyzing sentiment in text.

    This agent receives text input and analyzes its sentiment, providing detailed analysis
    of the emotional tone, key phrases, and overall sentiment score.

    Args:
        text: The text to analyze for sentiment
        manifesto: Custom instructions for the agent
        memory: Initial memory/context for the conversation
    """

    def __init__(self,
                 text: str,
                 manifesto: str,
                 memory: str = ""):

        if text is None:
            raise ValueError("Text must be provided")

        if manifesto is None:
            raise ValueError("Manifesto must be provided")

        model_name = "claude-3-5-sonnet-20240620"

        # Initialize base agent
        super().__init__(
            model_name=model_name,
            tools=None,  # No external tools needed for sentiment analysis
            tool_detection=self._detect_tool,
            end_detection=self._end_detection,
            manifesto=manifesto,
            memory="\nText to analyze: " + text + "\n" + memory
        )

    @debug()
    def _end_detection(self, manifesto: str, memory: str) -> bool:
        if "<TASK_COMPLETED>" in memory:
            return True
        else:
            return False

    @debug()
    def _detect_tool(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """No tools needed for sentiment analysis."""
        return None, None
