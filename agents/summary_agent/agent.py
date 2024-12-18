from typing import Dict, Optional, Callable, Tuple
import os
import json
from lib.debug import debug
from lib.base import Agent

class SummaryAgent(Agent):
    """An agent specialized for summarizing large amounts of text that exceed context windows.

    This agent receives text input that's too large for a single context window and breaks it down
    into manageable chunks, summarizing each chunk and then creating a final synthesized summary.

    Args:
        manifesto: Custom instructions for the agent
        memory: Initial memory/context for the conversation
        chunk_size: Optional size of text chunks to process at once (in characters)
        text: Optional text to summarize (for testing). If not provided, loads from input_text.json
    """

    def __init__(self,
                 manifesto: str,
                 memory: str = "",
                 chunk_size: int = 8000,  # Default chunk size set to 8000 chars
                 text: Optional[str] = None):  # Optional text parameter for testing

        if manifesto is None:
            raise ValueError("Manifesto must be provided")

        model_name = "claude-3-5-sonnet-20240620"

        # Use provided text or load from JSON
        if text is None:
            variables_dir = os.path.join(os.path.dirname(__file__), "variables")
            with open(os.path.join(variables_dir, "input_text.json"), 'r') as f:
                self.text = json.load(f)["text"]
        else:
            self.text = text

        self.chunk_size = chunk_size
        self.current_chunk_index = 0
        self.chunks = self._split_into_chunks(self.text)

        # Initialize base agent
        super().__init__(
            model_name=model_name,
            tools={'GET_NEXT_CHUNK': lambda _: self._get_next_chunk()},
            tool_detection=self._detect_tool,
            end_detection=self._end_detection,
            manifesto=manifesto,
            memory=memory
        )

    def _split_into_chunks(self, text: str) -> list[str]:
        """Split the input text into chunks of approximately chunk_size characters.
        Tries to split at sentence boundaries where possible."""
        chunks = []
        current_chunk = ""
        sentences = text.split(". ")  # Simple sentence splitting

        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.chunk_size:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += sentence + ". "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _get_next_chunk(self) -> str:
        """Return the next chunk of text to be summarized."""
        if self.current_chunk_index >= len(self.chunks):
            return "<NO_MORE_CHUNKS>"
        
        chunk = self.chunks[self.current_chunk_index]
        self.current_chunk_index += 1
        return f"CHUNK {self.current_chunk_index}/{len(self.chunks)}:\n{chunk}"

    @debug()
    def _end_detection(self, manifesto: str, memory: str) -> bool:
        """End when we see the final summary marker."""
        return "<FINAL_SUMMARY_COMPLETE>" in memory

    @debug()
    def _detect_tool(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Detect if we need to get the next chunk of text."""
        if "<REQUEST_NEXT_CHUNK>" in text:
            return "GET_NEXT_CHUNK", ""
        return None, None
