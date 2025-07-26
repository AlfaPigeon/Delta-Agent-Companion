"""
Structured logging system for AI Companion.
Provides multiple log levels, performance metrics, and error tracking.
"""

import logging
import structlog
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime
import json


class CompanionLogger:
    """Enhanced logging system for AI Companion."""
    
    def __init__(self, log_level: str = "INFO", log_dir: str = "./logs", debug_mode: bool = False):
        self.log_level = log_level.upper()
        self.log_dir = Path(log_dir)
        self.debug_mode = debug_mode
        self.metrics = {}
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure structlog
        self._configure_logging()
        
        # Create logger instances
        self.logger = structlog.get_logger("ai_companion")
        self.performance_logger = structlog.get_logger("performance")
        self.security_logger = structlog.get_logger("security")
        self.memory_logger = structlog.get_logger("memory")
        self.behavior_logger = structlog.get_logger("behavior_tree")
        self.llm_logger = structlog.get_logger("llm")
        self.tool_logger = structlog.get_logger("tools")
    
    def _configure_logging(self):
        """Configure structured logging."""
        # Configure standard logging
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=getattr(logging, self.log_level)
        )
        
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                self._json_processor if not self.debug_mode else structlog.dev.ConsoleRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    def _json_processor(self, logger, method_name, event_dict):
        """Custom JSON processor for log formatting."""
        # Add timestamp if not present
        if 'timestamp' not in event_dict:
            event_dict['timestamp'] = datetime.utcnow().isoformat()
        
        # Format for file output
        return json.dumps(event_dict, default=str)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(message, **kwargs)
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics."""
        self.performance_logger.info(
            "performance_metric",
            operation=operation,
            duration_ms=duration * 1000,
            **kwargs
        )
        
        # Update metrics
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(duration)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-related events."""
        self.security_logger.warning(
            "security_event",
            event_type=event_type,
            **details
        )
    
    def log_memory_operation(self, operation: str, memory_count: int, **kwargs):
        """Log memory system operations."""
        self.memory_logger.info(
            "memory_operation",
            operation=operation,
            memory_count=memory_count,
            **kwargs
        )
    
    def log_behavior_tree_modification(self, modification_type: str, state_id: str, **kwargs):
        """Log behavior tree modifications."""
        self.behavior_logger.info(
            "behavior_tree_modification",
            modification_type=modification_type,
            state_id=state_id,
            **kwargs
        )
    
    def log_llm_request(self, provider: str, model: str, tokens_used: int, duration: float, **kwargs):
        """Log LLM API requests."""
        self.llm_logger.info(
            "llm_request",
            provider=provider,
            model=model,
            tokens_used=tokens_used,
            duration_ms=duration * 1000,
            **kwargs
        )
    
    def log_tool_execution(self, tool_name: str, success: bool, duration: float, **kwargs):
        """Log tool execution."""
        self.tool_logger.info(
            "tool_execution",
            tool_name=tool_name,
            success=success,
            duration_ms=duration * 1000,
            **kwargs
        )
    
    def get_performance_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics summary."""
        summary = {}
        for operation, durations in self.metrics.items():
            if durations:
                summary[operation] = {
                    'count': len(durations),
                    'avg_duration': sum(durations) / len(durations),
                    'min_duration': min(durations),
                    'max_duration': max(durations)
                }
        return summary
    
    def reset_metrics(self):
        """Reset performance metrics."""
        self.metrics.clear()


class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, logger: CompanionLogger, operation: str, **kwargs):
        self.logger = logger
        self.operation = operation
        self.kwargs = kwargs
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            self.logger.log_performance(self.operation, duration, **self.kwargs)


# Global logger instance
_logger: Optional[CompanionLogger] = None


def get_logger() -> CompanionLogger:
    """Get the global logger instance."""
    global _logger
    if _logger is None:
        _logger = CompanionLogger()
    return _logger


def setup_logging(log_level: str = "INFO", log_dir: str = "./logs", debug_mode: bool = False):
    """Setup global logging configuration."""
    global _logger
    _logger = CompanionLogger(log_level, log_dir, debug_mode)
    return _logger


def time_operation(operation: str, **kwargs):
    """Decorator for timing operations."""
    def decorator(func):
        def wrapper(*args, **func_kwargs):
            logger = get_logger()
            with PerformanceTimer(logger, operation, **kwargs):
                return func(*args, **func_kwargs)
        return wrapper
    return decorator
