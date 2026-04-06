"""Type definitions for Agent Harness.

These dataclasses define the contract between the Harness and its consumers.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Protocol
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


@dataclass
class BackgroundTaskInfo:
    """Tracks a background task with its lifecycle state.
    
    Attributes:
        task_id: Unique identifier for the background task.
        step_number: Step number that spawned it (if from a skill workflow).
        title: Human-readable title.
        command: The command executed.
        process_id: OS process ID if applicable.
        started_at: ISO timestamp when the task started.
        status: One of 'running', 'completed', 'failed', 'timeout'.
        exit_code: Process exit code when completed.
        output: Captured output when available.
        error: Error message if failed.
    """
    task_id: str = field(default_factory=lambda: f"bg_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}")
    step_number: int = 0
    title: str = ""
    command: str = ""
    process_id: Optional[int] = None
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "running"
    exit_code: Optional[int] = None
    output: str = ""
    error: Optional[str] = None


class TaskValidator(Protocol):
    """Protocol for per-task validators.
    
    A validator receives the result data and returns a dict of quality metrics.
    """
    def __call__(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate task result data and return metrics."""
        ...


@dataclass
class SkillMetrics:
    """Persistent metrics for a skill's usage and performance.
    
    Attributes:
        name: Skill name.
        invocations: Total number of times the skill was called.
        successes: Number of successful executions.
        failures: Number of failed executions.
        total_duration_seconds: Cumulative execution time.
        last_used: ISO timestamp of the most recent use.
        last_error: Most recent error message, if any.
    """
    name: str = ""
    invocations: int = 0
    successes: int = 0
    failures: int = 0
    total_duration_seconds: float = 0.0
    last_used: Optional[str] = None
    last_error: Optional[str] = None

    @property
    def success_rate(self) -> float:
        """Return success rate as a float between 0.0 and 1.0."""
        if self.invocations == 0:
            return 0.0
        return self.successes / self.invocations

    @property
    def avg_duration(self) -> float:
        """Return average execution time per invocation."""
        if self.invocations == 0:
            return 0.0
        return self.total_duration_seconds / self.invocations

    def record(self, duration: float, success: bool, error: Optional[str] = None) -> None:
        """Record a single skill execution result."""
        self.invocations += 1
        self.total_duration_seconds += duration
        self.last_used = datetime.now(timezone.utc).isoformat()
        if success:
            self.successes += 1
        else:
            self.failures += 1
            if error:
                self.last_error = error
