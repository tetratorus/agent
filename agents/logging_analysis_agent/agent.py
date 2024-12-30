from typing import Dict, Optional, Callable, Tuple
import os
import json
from lib.base import Agent

class LoggingAnalysisAgent(Agent):
    """An agent specialized for analyzing debug logs from agent runs.

    This agent processes raw debug logs that may be too large for a single context window,
    breaking them down into manageable chunks and analyzing them for patterns, errors,
    and important events to provide actionable feedback.

    Args:
        manifesto: Custom instructions for the agent
        chunk_size: Optional size of log chunks to process at once (in characters)
        memory: Initial memory/context for the conversation
    """

    def __init__(self,
                 manifesto: str,
                 chunk_size: int = 8000,
                 memory: str = "",
    ):
        if manifesto is None:
            raise ValueError("Manifesto must be provided")

        self.current_chunk_index = None
        self.chunks = None
        self.chunk_size = chunk_size

        # Initialize with a model that has strong text analysis capabilities
        model_name = "gpt-4o"

        # Initialize base agent with tools for log analysis
        super().__init__(
            model_name=model_name,
            tools={
                'GET_NEXT_LOG_CHUNK': lambda _: self._get_next_chunk(),
                'MARK_ANALYSIS_COMPLETE': lambda _: self._mark_analysis_complete()
            },
            tool_detection=self._detect_tool,
            end_detection=self._end_detection,
            manifesto=manifesto,
            memory=memory
        )

    def _split_into_chunks(self, logs: str, chunk_size: int) -> list[str]:
        """Split the input logs into chunks of approximately chunk_size characters.
        Tries to split at newlines where possible to preserve log entry integrity."""
        chunks = []
        current_chunk = ""
        lines = logs.split("\n")

        for line in lines:
            if len(current_chunk) + len(line) > chunk_size:
                chunks.append(current_chunk.strip())
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _get_next_chunk(self) -> str:
        """Return the next chunk of logs to be analyzed."""
        if self.chunks is None:
            # First time getting logs, ask user for them
            logs = self.ask_user("Please provide the logs to analyze")
            self.chunks = self._split_into_chunks(logs, self.chunk_size)
            self.current_chunk_index = 0

        if self.current_chunk_index >= len(self.chunks):
            return "<NO_MORE_CHUNKS>"

        chunk = self.chunks[self.current_chunk_index]
        self.current_chunk_index += 1
        return f"LOG_CHUNK {self.current_chunk_index}/{len(self.chunks)}:\n{chunk}"

    def _mark_analysis_complete(self) -> str:
        """Mark that the agent has completed its analysis of all chunks."""
        return "<ANALYSIS_COMPLETE>"

    def _detect_tool(self, text: str) -> Optional[Tuple[str, str]]:
        """Detect if a tool needs to be called based on the agent's response.
        Returns a tuple of (tool_name, tool_input) if a tool should be called,
        or (None, None) if no tool needs to be called."""
        # Check for next chunk request
        if "GET_NEXT_LOG_CHUNK" in text:
            return "GET_NEXT_LOG_CHUNK", ""

        # Check for analysis complete marker
        if "MARK_ANALYSIS_COMPLETE" in text:
            return "MARK_ANALYSIS_COMPLETE", ""

        return None, None

    def _end_detection(self, manifesto: str, memory: str) -> bool:
        """End when we see the analysis complete marker."""
        return "<ANALYSIS_COMPLETE>" in memory
