from typing import Any, Dict, Optional, List
import logging

class BaseAgent:
    """
    Abstract base class for all agents in the multi-agent system.
    Provides a standard interface and hooks for logging, validation, and error handling.
    """

    # Subclasses can specify required context keys for validation
    required_context_keys: List[str] = []

    def __init__(self, name: Optional[str] = None, logger: Optional[logging.Logger] = None):
        self.name = name or self.__class__.__name__
        self.logger = logger or logging.getLogger(self.name)
        self.logger.propagate = True

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method to be implemented by all agents.
        Should process the context and return a dictionary of results to be merged into the context.
        """
        raise NotImplementedError("Each agent must implement the run(context) method.")

    def validate_context(self, context: Dict[str, Any]) -> bool:
        """
        Validate if the context contains all required keys for this agent.
        Returns True if valid, False otherwise.
        """
        missing = [k for k in self.required_context_keys if k not in context]
        if missing:
            self.log(f"Missing required context keys: {missing}", level="warning")
            return False
        return True

    def log(self, message: str, level: str = "info"):
        """
        Unified logging for agents. Uses Python's logging module.
        """
        msg = f"[{self.name}] {message}"
        if level == "debug":
            self.logger.debug(msg)
        elif level == "warning":
            self.logger.warning(msg)
        elif level == "error":
            self.logger.error(msg)
        else:
            self.logger.info(msg)

    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Custom error handling for agents.
        Returns a dict with error details to be merged into the context.
        """
        self.log(f"Error: {str(error)}", level="error")
        return {"error": str(error)}