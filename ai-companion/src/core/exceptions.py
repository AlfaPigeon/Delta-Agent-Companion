"""
Custom exceptions for AI Companion.
"""


class CompanionError(Exception):
    """Base exception for AI Companion."""
    pass


class ConfigurationError(CompanionError):
    """Raised when there's a configuration issue."""
    pass


class MemoryError(CompanionError):
    """Raised when there's a memory system issue."""
    pass


class BehaviorTreeError(CompanionError):
    """Raised when there's a behavior tree issue."""
    pass


class LLMError(CompanionError):
    """Raised when there's an LLM processing issue."""
    pass


class ToolExecutionError(CompanionError):
    """Raised when tool execution fails."""
    pass


class SecurityError(CompanionError):
    """Raised when there's a security issue."""
    pass


class ValidationError(CompanionError):
    """Raised when validation fails."""
    pass
