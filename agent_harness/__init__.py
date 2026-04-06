"""Agent Harness Core Module.

Provides infrastructure for task execution with active memory, context injection,
self-healing capabilities, and skill routing.

v3.2: Added BackgroundTaskInfo, TaskValidator, SkillMetrics, SkillMetricsCollector,
ErrorLearner, and lifecycle-aware background task management.
"""

from agent_harness.core import AgentHarness
from agent_harness.types import AgentTask, AgentResult, TaskContext
from agent_harness.types import BackgroundTaskInfo, TaskValidator, SkillMetrics
from agent_harness.memory import MemoryManager
from agent_harness.observer import Observer, ExecutionMetrics, observe
from agent_harness.self_healer import SelfHealer, ErrorMatch, RecoveryStrategy, ErrorLearner
from agent_harness.skill_router import SkillRouter, SkillDefinition
from agent_harness.skill_executor import SkillExecutor, WorkflowStep, ExecutionResult
from agent_harness.skill_executor import SkillMetricsCollector

__all__ = [
    "AgentHarness",
    "AgentTask",
    "AgentResult",
    "TaskContext",
    "BackgroundTaskInfo",
    "TaskValidator",
    "SkillMetrics",
    "MemoryManager",
    "Observer",
    "ExecutionMetrics",
    "observe",
    "SelfHealer",
    "ErrorMatch",
    "RecoveryStrategy",
    "ErrorLearner",
    "SkillRouter",
    "SkillDefinition",
    "SkillExecutor",
    "WorkflowStep",
    "ExecutionResult",
    "SkillMetricsCollector",
]
__version__ = "3.2.0"
