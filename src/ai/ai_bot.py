# Apache License
# Version 2.0, January 2004
# Author: Jonathan Tiritilli

from abc import ABC, abstractmethod


class AiBot(ABC):
    """Base class for AI-powered bots"""

    @abstractmethod
    def ai_request_diffs(self, code, diffs) -> str:
        """
        Abstract method for AI requests - maintained for compatibility.

        Args:
            code (str): Input content
            diffs (str): Additional context

        Returns:
            str: AI response
        """
        pass
