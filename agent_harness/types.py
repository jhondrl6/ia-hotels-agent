"""Type definitions for Agent Harness.

These dataclasses define the contract between the Harness and its consumers.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime, timezone


@dataclass
class TaskContext:
    """Context injected into task execution based on historical memory.
    
    Attributes:
        previous_runs: Number of times this task/target combination ran before.
        last_outcome: Outcome of the most recent run ('success', 'error', 'partial_failure').
        last_error_type: If last run failed, the error type (e.g., 'TimeoutError').
        suggestions: List of suggested parameter adjustments based on history.
        harness: Optional reference to the AgentHarness instance for delegation.
    """
    previous_runs: int = 0
    last_outcome: Optional[str] = None
    last_error_type: Optional[str] = None
    suggestions: list = field(default_factory=list)
    harness: Optional[Any] = None


@dataclass
class AgentTask:
    """Represents a task to be executed by the Harness.
    
    Attributes:
        name: Task identifier (e.g., 'spark', 'audit', 'execute').
        payload: Dictionary with task-specific parameters (e.g., url, package).
        metadata: Additional info (e.g., requester, priority).
    """
    name: str
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def target_id(self) -> str:
        """Generate a unique identifier for this task's target.
        
        Used for memory lookup (e.g., the URL being analyzed).
        """
        return self.payload.get("url", self.payload.get("target", f"task:{self.name}"))


@dataclass
class AgentResult:
    """Result of a task execution.
    
    Attributes:
        success: True if task completed without critical errors.
        outcome: More granular status ('success', 'error', 'partial_failure').
        data: The actual result data from task execution.
        quality_metrics: Validation metrics (e.g., fields_populated, score_valid).
        error: Error message if task failed.
        error_type: Classification of error for learning.
        duration_seconds: Execution time.
        background_tasks: Info about tasks launched in background.
    """
    success: bool
    outcome: str  # 'success', 'error', 'partial_failure'
    data: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    error_type: Optional[str] = None
    duration_seconds: float = 0.0
    background_tasks: list = field(default_factory=list)
    
    def to_log_entry(self, task: AgentTask, context: TaskContext) -> Dict[str, Any]:
        """Convert result to a log entry for execution_history.jsonl."""
        return {
            "session_id": self.data.get("session_id", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task_name": task.name,
            "target_id": task.target_id,
            "duration_seconds": round(self.duration_seconds, 2),
            "outcome": self.outcome,
            "error_type": self.error_type,
            "quality_metrics": self.quality_metrics,
            "background_tasks_count": len(self.background_tasks),
            "context_used": {
                "previous_runs": context.previous_runs,
                "suggestions_applied": len(context.suggestions),
            },
        }
