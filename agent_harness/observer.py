"""Observer Module for Agent Harness.

Provides decorators and utilities for monitoring task execution,
capturing metrics, and enabling observability.
"""

import functools
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ExecutionMetrics:
    """Metrics captured during task execution.
    
    Attributes:
        start_time: Unix timestamp when execution started.
        end_time: Unix timestamp when execution ended.
        duration_seconds: Total execution time.
        stages_completed: List of stages/phases completed.
        exception_type: Type of exception if one occurred.
        exception_message: Error message if exception occurred.
        retries: Number of retry attempts made.
    """
    start_time: float = 0.0
    end_time: float = 0.0
    duration_seconds: float = 0.0
    stages_completed: List[str] = field(default_factory=list)
    exception_type: Optional[str] = None
    exception_message: Optional[str] = None
    retries: int = 0
    
    def mark_stage(self, stage_name: str) -> None:
        """Mark a stage as completed."""
        if stage_name not in self.stages_completed:
            self.stages_completed.append(stage_name)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for logging."""
        return {
            "duration_seconds": round(self.duration_seconds, 3),
            "stages_completed": self.stages_completed,
            "exception_type": self.exception_type,
            "retries": self.retries,
        }


class Observer:
    """Observer that wraps function execution with metrics capture.
    
    Can be used as a decorator or context manager.
    """
    
    def __init__(self, verbose: bool = True):
        """Initialize observer.
        
        Args:
            verbose: If True, print observation logs.
        """
        self.verbose = verbose
        self.current_metrics: Optional[ExecutionMetrics] = None
    
    def observe(self, func: Callable) -> Callable:
        """Decorator to observe a function's execution.
        
        Args:
            func: Function to observe.
            
        Returns:
            Wrapped function with observation.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            metrics = ExecutionMetrics()
            metrics.start_time = time.time()
            self.current_metrics = metrics
            
            try:
                result = func(*args, **kwargs)
                metrics.end_time = time.time()
                metrics.duration_seconds = metrics.end_time - metrics.start_time
                
                if self.verbose:
                    print(f"[OBSERVER] ✓ {func.__name__} completed in {metrics.duration_seconds:.2f}s")
                
                return result, metrics
                
            except Exception as e:
                metrics.end_time = time.time()
                metrics.duration_seconds = metrics.end_time - metrics.start_time
                metrics.exception_type = type(e).__name__
                metrics.exception_message = str(e)
                
                if self.verbose:
                    print(f"[OBSERVER] ✗ {func.__name__} failed: {metrics.exception_type}")
                
                raise
            finally:
                self.current_metrics = None
        
        return wrapper
    
    def mark_stage(self, stage_name: str) -> None:
        """Mark a stage as completed in current observation.
        
        Args:
            stage_name: Name of the completed stage.
        """
        if self.current_metrics:
            self.current_metrics.mark_stage(stage_name)


def observe(func: Callable = None, *, verbose: bool = True) -> Callable:
    """Decorator factory for observing function execution.
    
    Can be used as:
        @observe
        def my_func(): ...
        
    Or:
        @observe(verbose=False)
        def my_func(): ...
    
    Args:
        func: Function to decorate (when used without parentheses).
        verbose: Whether to print observation logs.
        
    Returns:
        Decorated function or decorator.
    """
    observer = Observer(verbose=verbose)
    
    if func is not None:
        # Called as @observe without parentheses
        return observer.observe(func)
    
    # Called as @observe(...) with arguments
    return observer.observe
