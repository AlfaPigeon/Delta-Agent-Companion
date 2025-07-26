"""
Core module for AI Companion.
Provides base classes and utilities used throughout the system.
"""

from .logging import CompanionLogger, get_logger, setup_logging, time_operation
from .exceptions import *

__all__ = [
    'CompanionLogger',
    'get_logger', 
    'setup_logging',
    'time_operation',
    'CompanionError',
    'ConfigurationError',
    'MemoryError',
    'BehaviorTreeError',
    'LLMError',
    'ToolExecutionError'
]
