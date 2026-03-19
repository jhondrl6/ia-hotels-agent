"""Agent Harness Core - API-First Task Executor.

This module provides the main entry point for executing tasks with
active memory and context injection.
"""

import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from agent_harness.types import AgentTask, AgentResult, TaskContext
from agent_harness.memory import MemoryManager
from modules.utils.ui_colors import UIColors


class AgentHarness:
    """Main orchestrator for task execution with memory.
    
    Wraps business logic functions and provides:
    - Context injection from historical memory
    - Result validation (quality gates)
    - Automatic logging of executions
    - Background task tracking
    """
    
    def __init__(self, memory_manager: Optional[MemoryManager] = None, verbose: bool = True):
        """Initialize the AgentHarness.
        
        Args:
            memory_manager: Optional custom MemoryManager instance.
            verbose: If True, print context injection info.
        """
        from agent_harness.skill_router import SkillRouter
        from agent_harness.skill_executor import SkillExecutor

        self.memory = memory_manager or MemoryManager()
        self.verbose = verbose
        self._task_handlers: Dict[str, Callable] = {}
        self._active_background_tasks: List[Dict[str, Any]] = []
        
        # New Skill System (Blueprint v3.2)
        self.router = SkillRouter(verbose=self.verbose)
        self.executor = SkillExecutor(
            command_runner=self._skill_command_runner,
            verbose=self.verbose, 
            auto_turbo=True
        )

    def _skill_command_runner(self, command: str, is_background: bool = False) -> tuple[int, str]:
        """Command runner that supports shell commands and recursive task calls."""
        import subprocess
        import shlex
        import json

        # 1. Resolve placeholders from the last task context if available
        # This is a bit of a hack since SkillExecutor doesn't pass the task payload directly
        # but we can try to find the current active task context or payload.
        # In this Level 3 architecture, we assume the harness knows what it's running.
        
        processed_cmd = command
        # Placeholder resolution is usually handled by the executor, but we add it here for tasks
        
        # 2. Check if it's a task call (e.g., 'geo_stage --url ...')
        tokens = shlex.split(processed_cmd)
        if not tokens:
            return 0, ""
            
        task_name = tokens[0]
        
        # If the first token is a registered task or a known skill
        if task_name in self._task_handlers or self.router.skill_exists(task_name):
            if self.verbose:
                print(f"[HARNESS] 🔄 Delegación recursiva detectada: {task_name}")
            
            # Simple argument parsing: --key value
            payload = {}
            i = 1
            while i < len(tokens):
                token = tokens[i]
                if token.startswith("--") and i + 1 < len(tokens):
                    key = token.lstrip("-")
                    value = tokens[i+1]
                    payload[key] = value
                    i += 2
                else:
                    i += 1
            
            # Execute recursively
            task = AgentTask(name=task_name, payload=payload)
            result = self.run_task(task)
            
            if result.success:
                return 0, json.dumps(result.data, ensure_ascii=False)
            else:
                return 1, f"Task {task_name} failed: {result.error}"

        # 3. Fallback to standard shell execution
        try:
            result = subprocess.run(
                processed_cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode, result.stdout + result.stderr
        except Exception as e:
            return 1, str(e)
    
    def register_handler(self, task_name: str, handler: Callable) -> None:
        """Register a handler function for a task type.
        
        Args:
            task_name: Name of the task (e.g., 'spark', 'audit').
            handler: Callable that takes (payload: dict, context: TaskContext) -> dict.
        """
        self._task_handlers[task_name] = handler
    
    def get_active_background_tasks(self) -> List[Dict[str, Any]]:
        """Get list of tasks currently running in background.
        
        Returns:
            List of background task info dictionaries.
        """
        return self._active_background_tasks

    def run_task(self, task: AgentTask, _retry_count: int = 0) -> AgentResult:
        """Execute a task with memory-aware context injection and self-healing.
        
        This is the main API entry point.
        
        Args:
            task: AgentTask instance with name and payload.
            _retry_count: Internal retry counter (do not set manually).
            
        Returns:
            AgentResult with execution outcome and data.
        """
        from agent_harness.self_healer import SelfHealer
        
        start_time = time.time()
        session_id = str(uuid.uuid4())[:8]
        
        # Initialize self-healer
        healer = SelfHealer(verbose=self.verbose)
        
        # Step 1: Build context from memory
        context = self.memory.build_context(task.target_id)
        context.harness = self # Inject self reference for delegation
        
        if self.verbose and context.previous_runs > 0:
            print(f"[HARNESS] 🧠 " + UIColors.info(f"Contexto inyectado: {context.previous_runs} ejecución(es) previa(s) encontrada(s)."))
            if context.last_outcome == "error":
                print(f"[HARNESS] ⚠️  " + UIColors.warning(f"Última ejecución falló ({context.last_error_type})."))
            for suggestion in context.suggestions:
                print(f"[HARNESS] 💡 {suggestion}")
        
        # Step 2: Get handler or skill
        handler = self._task_handlers.get(task.name)
        bg_tasks = []
        
        try:
            result_data = {}
            if handler:
                result_data = handler(task.payload, context)
            else:
                # 1. Exact Name match fallback
                skill = None
                if self.router.skill_exists(task.name):
                    skill = self.router.get_skill(task.name)
                
                # 2. Trigger parsing (Meta-Architecture Semantic Routing)
                if not skill:
                    # Very basic semantic match: if the task name is somewhere in a trigger
                    all_skills = self.router.list_skills()
                    for s in all_skills:
                        if s.trigger and task.name.lower() in s.trigger.lower():
                            skill = s
                            break

                if skill:
                    if self.verbose:
                        print(f"[HARNESS] 🚀 Enrutando semánticamente '{task.name}' a Meta-Skill: {skill.path.name}")
                    
                    execution_result = self.executor.execute_skill(
                        skill, 
                        dry_run=False,
                        context_data=task.payload
                    )
                    if not execution_result.success:
                        return AgentResult(
                            success=False,
                            outcome="error",
                            error=f"Skill execution failed: {execution_result.error}",
                            error_type="SkillExecutionError",
                            duration_seconds=time.time() - start_time,
                        )
                    
                    result_data = {
                        "skill_executed": skill.name,
                        "output": execution_result.output,
                        "target_id": task.target_id,
                        "background_tasks": execution_result.background_tasks,
                        "steps_executed": execution_result.steps_executed
                    }
                else:
                    return AgentResult(
                        success=False,
                        outcome="error",
                        error=f"No Meta-Skill directly matches trigger '{task.name}'",
                        error_type="TaskNotRecognizedError",
                        duration_seconds=time.time() - start_time,
                    )
            
            # Step 3: Post-process result data
            if isinstance(result_data, dict):
                result_data["session_id"] = session_id
                if "background_tasks" in result_data:
                    bg_tasks = result_data["background_tasks"]
                    for bg_task in bg_tasks:
                        bg_task["task_name"] = task.name
                        bg_task["target_id"] = task.target_id
                        bg_task["started_at"] = datetime.utcnow().isoformat()
                        self._active_background_tasks.append(bg_task)
            
            duration = time.time() - start_time
            
            # Step 4: Validate quality
            quality_metrics = self._validate_result(task.name, result_data)
            outcome = "success" if quality_metrics.get("is_valid", False) else "partial_failure"
            
            result = AgentResult(
                success=True,
                outcome=outcome,
                data=result_data,
                quality_metrics=quality_metrics,
                duration_seconds=duration,
                background_tasks=bg_tasks,
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_type = type(e).__name__
            
            # Attempt self-healing
            match = healer.match_error(e)
            if match.matched and healer.should_retry(match, _retry_count):
                print(f"[HARNESS] 🩹 " + UIColors.warning(f"Error detectado. Aplicando Auto-Sanación (intento {_retry_count + 1})..."))
                should_retry, modified_payload, _ = healer.execute_recovery(
                    match, task.payload, _retry_count
                )
                
                if should_retry:
                    retry_task = AgentTask(
                        name=task.name,
                        payload=modified_payload,
                        metadata=task.metadata,
                    )
                    return self.run_task(retry_task, _retry_count + 1)
            
            result = AgentResult(
                success=False,
                outcome="error",
                error=str(e),
                error_type=error_type,
                duration_seconds=duration,
                data={
                    "session_id": session_id,
                    "recovery_attempted": match.matched,
                    "recovery_suggestion": match.recovery.message if match.recovery else None,
                },
            )
            if self.verbose:
                print(f"[HARNESS] ❌ " + UIColors.error(f"Tarea falló: {error_type} - {e}"))
        
        # Step 5: Log execution
        log_entry = result.to_log_entry(task, context)
        log_entry["retries"] = _retry_count
        self.memory.append_log(log_entry)
        
        if self.verbose:
            status_icon = UIColors.success("✅") if result.success else UIColors.error("❌")
            if bg_tasks:
                print(f"[HARNESS] 🔄 " + UIColors.info(f"{len(bg_tasks)} tareas iniciadas en SEGUNDO PLANO."))
            
            outcome_color = UIColors.GREEN if result.outcome == "success" else UIColors.YELLOW if result.outcome == "partial_failure" else UIColors.RED
            print(f"[HARNESS] {status_icon} Ejecutado en {result.duration_seconds:.2f}s - Outcome: " + UIColors.colorize(result.outcome, outcome_color))
        
        return result
    
    def _validate_result(self, task_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate result quality based on task type."""
        metrics = {
            "is_valid": True,
            "checks_passed": [],
            "checks_failed": [],
        }
        
        if not data or (isinstance(data, dict) and len(data) == 1 and "session_id" in data):
            metrics["is_valid"] = False
            metrics["checks_failed"].append("result_empty")
            return metrics
        
        metrics["checks_passed"].append("result_not_empty")
        return metrics
