"""Agent Harness Core Module.

Provides infrastructure for task execution with active memory, context injection,
self-healing capabilities, and skill routing.
"""

from agent_harness.core import AgentHarness
from agent_harness.types import AgentTask, AgentResult, TaskContext
from agent_harness.memory import MemoryManager
from agent_harness.observer import Observer, ExecutionMetrics, observe
from agent_harness.self_healer import SelfHealer, ErrorMatch, RecoveryStrategy
from agent_harness.skill_router import SkillRouter, SkillDefinition
from agent_harness.skill_executor import SkillExecutor, WorkflowStep, ExecutionResult

__all__ = [
    "AgentHarness",
    "AgentTask",
    "AgentResult",
    "TaskContext",
    "MemoryManager",
    "Observer",
    "ExecutionMetrics",
    "observe",
    "SelfHealer",
    "ErrorMatch",
    "RecoveryStrategy",
    "SkillRouter",
    "SkillDefinition",
    "SkillExecutor",
    "WorkflowStep",
    "ExecutionResult",
]
__version__ = "0.3.0"
