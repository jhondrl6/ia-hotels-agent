"""Agent Harness Core - API-First Task Executor.

This module provides the main entry point for executing tasks with
active memory and context injection.

v3.2: Fixed recursive delegation, added timeout support, background task
lifecycle management, per-task validators, and thread-safe memory calls.
"""

import inspect
import threading
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from agent_harness.types import (
    AgentTask, AgentResult, TaskContext,
    BackgroundTaskInfo, SkillMetrics,
)
from agent_harness.memory import MemoryManager


class AgentHarness:
    """Main orchestrator for task execution with memory.
    
    Wraps business logic functions and provides:
    - Context injection from historical memory
    - Result validation (quality gates) with per-task validators
    - Automatic logging of executions
    - Background task lifecycle tracking
    - Timeout protection for hanging handlers
    - Recursive task delegation via skill execution
    """
    
    def __init__(
        self,
        memory_manager: Optional[MemoryManager] = None,
        verbose: bool = True,
        default_task_timeout: Optional[float] = None,
    ):
        """Initialize the AgentHarness.
        
        Args:
            memory_manager: Optional custom MemoryManager instance.
            verbose: If True, print context injection info.
            default_task_timeout: Default timeout in seconds for task execution.
                None means no timeout (previous behavior).
        """
        from agent_harness.skill_router import SkillRouter
        from agent_harness.skill_executor import SkillExecutor

        self.memory = memory_manager or MemoryManager()
        self.verbose = verbose
        self._task_handlers: Dict[str, Callable] = {}
        self._task_validators: Dict[str, Callable] = {}
        self.default_task_timeout = default_task_timeout
        
        # Background tasks with proper lifecycle
        self._background_tasks: Dict[str, BackgroundTaskInfo] = {}
        self._bg_tasks_lock = threading.Lock()
        
        # New Skill System (Blueprint v3.2)
        self.router = SkillRouter(verbose=self.verbose)
        self.executor = SkillExecutor(
            command_runner=self._skill_command_runner,
            verbose=self.verbose, 
            auto_turbo=True
        )

    def register_handler(self, task_name: str, handler: Callable) -> None:
        """Register a handler function for a task type.
        
        Args:
            task_name: Name of the task (e.g., 'spark', 'audit').
            handler: Callable that takes (payload: dict, context: TaskContext) -> dict.
        """
        self._task_handlers[task_name] = handler

    def register_validator(self, task_name: str, validator: Callable) -> None:
        """Register a quality validator for a specific task type.
        
        Args:
            task_name: Name of the task that this validator applies to.
            validator: Callable that takes (data: dict) -> metrics_dict.
                Returns a dict with 'is_valid' (bool) and diagnostics.
        """
        self._task_validators[task_name] = validator
    
    def _get_ui_colors(self):
        """Get UIColors class with graceful fallback.
        
        Avoids hard dependency on modules.utils.ui_colors which may
        not exist in all environments.
        """
        try:
            from modules.utils.ui_colors import UIColors
            return UIColors
        except ImportError:
            # Fallback: no colors, just return text
            class _NoColors:
                @staticmethod
                def success(t): return f"[OK] {t}"
                @staticmethod
                def error(t): return f"[ERR] {t}"
                @staticmethod
                def warning(t): return f"[WARN] {t}"
                @staticmethod
                def info(t): return f"[INFO] {t}"
                @staticmethod
                def colorize(t, _c): return t
                GREEN = "green"
                YELLOW = "yellow"
                RED = "red"
            return _NoColors

    def _skill_command_runner(self, command: str, is_background: bool = False) -> tuple:
        """Command runner that supports shell commands and recursive task calls."""
        import shlex
        import json
        import subprocess

        processed_cmd = command
        
        # 1. Check if it's a task call (e.g., 'geo_stage --url ...')
        tokens = shlex.split(command)
        if not tokens:
            return 0, ""
            
        task_name = tokens[0]
        
        # If the first token is a registered task or a known skill
        if task_name in self._task_handlers or self.router.skill_exists(task_name):
            if self.verbose:
                UIColors = self._get_ui_colors()
                print(f"[HARNESS] Delegacion recursiva detectada: {task_name}")
            
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

        # 2. Fallback to standard shell execution
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
    
    def get_active_background_tasks(self) -> List[BackgroundTaskInfo]:
        """Get list of background tasks with their current status."""
        with self._bg_tasks_lock:
            return list(self._background_tasks.values())
    
    def get_background_tasks_by_status(self, status: str) -> List[BackgroundTaskInfo]:
        """Get background tasks filtered by status.
        
        Args:
            status: One of 'running', 'completed', 'failed', 'timeout'.
            
        Returns:
            List of matching background tasks.
        """
        with self._bg_tasks_lock:
            return [t for t in self._background_tasks.values() if t.status == status]
    
    def _poll_background_tasks(self) -> Dict[str, Any]:
        """Poll running background tasks and update their status.
        
        Checks OS-level process status where possible.
        
        Returns:
            Summary of status changes.
        """
        import subprocess
        
        changed = {"completed": 0, "failed": 0, "timed_out": 0}
        now = datetime.utcnow()
        
        with self._bg_tasks_lock:
            tasks_to_remove = []
            
            for task_id, task in self._background_tasks.items():
                if task.status != "running":
                    continue
                
                if task.process_id is not None:
                    # Check if process is still running
                    try:
                        # On Windows WSL, use /proc
                        proc_path = f"/proc/{task.process_id}"
                        import os
                        if not os.path.exists(proc_path):
                            task.status = "completed"
                            task.exit_code = 0
                            changed["completed"] += 1
                    except (OSError, IOError):
                        task.status = "failed"
                        task.error = "Process not found"
                        changed["failed"] += 1
                
                # Check for timeout (5 minutes default for background tasks)
                try:
                    started = datetime.fromisoformat(task.started_at)
                    elapsed = (now - started).total_seconds()
                    if elapsed > 300:  # 5 min timeout
                        task.status = "timeout"
                        task.error = "Background task timed out (300s)"
                        changed["timed_out"] += 1
                except (ValueError, TypeError):
                    pass
            
            # Clean up old completed/failed tasks (keep only last hour)
            cutoff = now.replace(minute=max(0, now.minute - 60))
            for task_id, task in self._background_tasks.items():
                if task.status in ("completed", "failed", "timeout"):
                    try:
                        started = datetime.fromisoformat(task.started_at)
                        if started < cutoff:
                            tasks_to_remove.append(task_id)
                    except (ValueError, TypeError):
                        tasks_to_remove.append(task_id)
            
            for tid in tasks_to_remove:
                del self._background_tasks[tid]
        
        return changed
    
    def _register_background_task(self, info: Dict[str, Any], process_id: Optional[int] = None) -> str:
        """Register a new background task with full tracking info.
        
        Args:
            info: Dict with at least 'step_number', 'title', 'command', 'output'.
            process_id: Optional OS process ID.
            
        Returns:
            The task_id assigned to this background task.
        """
        bg = BackgroundTaskInfo(
            step_number=info.get("step_number", 0),
            title=info.get("title", ""),
            command=info.get("command", ""),
            process_id=process_id,
            output=info.get("output", ""),
        )
        with self._bg_tasks_lock:
            self._background_tasks[bg.task_id] = bg
        return bg.task_id
    
    def _execute_with_timeout(
        self, func: Callable, args: tuple = (), kwargs: Optional[dict] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """Execute a function with a timeout guard.
        
        Uses threading.Timer to detect timeouts in a cross-platform way.
        The timeout does NOT kill the thread (Python limitation), but
        returns a TimeoutError so the harness can handle it gracefully.
        
        Args:
            func: Function to execute.
            args: Positional arguments for the function.
            kwargs: Keyword arguments for the function.
            timeout: Timeout in seconds. None = no timeout (uses default).
            
        Returns:
            The return value of func().
            
        Raises:
            TimeoutError: If execution exceeds the timeout.
        """
        if timeout is None:
            timeout = self.default_task_timeout
        
        if timeout is None:
            # No timeout configured -- execute directly
            return func(*args, **(kwargs or {}))
        
        result_container = {"value": None, "exception": None, "completed": False}
        
        def _target():
            try:
                result_container["value"] = func(*args, **(kwargs or {}))
            except Exception as e:
                result_container["exception"] = e
            finally:
                result_container["completed"] = True
        
        thread = threading.Thread(target=_target, daemon=True)
        thread.start()
        thread.join(timeout=timeout)
        
        if not result_container["completed"]:
            raise TimeoutError(
                f"Task execution timed out after {timeout}s. "
                f"Handler is still running in background but result was discarded."
            )
        
        if result_container["exception"] is not None:
            raise result_container["exception"]
        
        return result_container["value"]
    
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
        context.harness = self  # Inject self reference for delegation
        
        UIColors = self._get_ui_colors()
        
        if self.verbose and context.previous_runs > 0:
            print(f"[HARNESS] " + UIColors.info(f"Contexto inyectado: {context.previous_runs} ejecucion(es) previa(s) encontrada(s)."))
            if context.last_outcome == "error":
                print(f"[HARNESS] " + UIColors.warning(f"Ultima ejecucion fallo ({context.last_error_type})."))
            for suggestion in context.suggestions:
                print(f"[HARNESS] {suggestion}")
        
        # Step 2: Get handler or skill
        handler = self._task_handlers.get(task.name)
        bg_tasks = []
        
        try:
            result_data = {}
            if handler:
                result_data = self._execute_with_timeout(
                    handler, args=(task.payload, context)
                )
            else:
                # 1. Exact Name match fallback
                skill = None
                if self.router.skill_exists(task.name):
                    skill = self.router.get_skill(task.name)
                
                # 2. Trigger parsing (Meta-Architecture Semantic Routing)
                if not skill:
                    # Basic semantic match: if the task name is somewhere in a trigger
                    all_skills = self.router.list_skills()
                    for s in all_skills:
                        if s.trigger and task.name.lower() in s.trigger.lower():
                            skill = s
                            break

                if skill:
                    if self.verbose:
                        print(f"[HARNESS] Enrutando semanticamente '{task.name}' a Meta-Skill: {skill.path.name}")
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
                    for bg_info in bg_tasks:
                        bg_info["task_name"] = task.name
                        bg_info["target_id"] = task.target_id
                        bg_info["started_at"] = datetime.utcnow().isoformat()
                        # Register in lifecycle tracker
                        task_id = self._register_background_task(bg_info)
                        bg_info["task_id"] = task_id
                    self._active_background_tasks = bg_tasks  # Backwards compat
            
            duration = time.time() - start_time
            
            # Step 4: Validate quality (with per-task validators)
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
            
        except TimeoutError as e:
            duration = time.time() - start_time
            result = AgentResult(
                success=False,
                outcome="error",
                error=str(e),
                error_type="TimeoutError",
                duration_seconds=duration,
                data={"session_id": session_id},
            )
            if self.verbose:
                print(f"[HARNESS] " + UIColors.error(f"Tarea agoto el tiempo de espera: {e}"))
            
        except Exception as e:
            duration = time.time() - start_time
            error_type = type(e).__name__
            
            # Attempt self-healing
            match = healer.match_error(e)
            if match.matched and healer.should_retry(match, _retry_count):
                print(f"[HARNESS] " + UIColors.warning(f"Error detectado. Aplicando Auto-Sanacion (intento {_retry_count + 1})..."))
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
                print(f"[HARNESS] " + UIColors.error(f"Tarea fallo: {error_type} - {e}"))
        
        # Step 5: Log execution
        log_entry = result.to_log_entry(task, context)
        log_entry["retries"] = _retry_count
        self.memory.append_log(log_entry)
        
        if self.verbose:
            status_icon = UIColors.success("OK") if result.success else UIColors.error("ERR")
            if bg_tasks:
                print(f"[HARNESS] " + UIColors.info(f"{len(bg_tasks)} tareas iniciadas en SEGUNDO PLANO."))
            
            outcome_color = UIColors.GREEN if result.outcome == "success" else UIColors.YELLOW if result.outcome == "partial_failure" else UIColors.RED
            print(f"[HARNESS] {status_icon} Ejecutado en {result.duration_seconds:.2f}s - Outcome: " + UIColors.colorize(result.outcome, outcome_color))
        
        # Background tasks: poll and report changes
        bg_summary = self._poll_background_tasks()
        if self.verbose and any(v > 0 for v in bg_summary.values()):
            print(f"[HARNESS] Background: {bg_summary['completed']} completed, "
                  f"{bg_summary['failed']} failed, {bg_summary['timed_out']} timed out")
        
        return result
    
    def _validate_result(self, task_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate result quality. Uses per-task validators if registered,
        otherwise falls back to a generic empty-result check.
        
        Args:
            task_name: Name of the executed task.
            data: Result data dictionary from the handler or skill.
            
        Returns:
            Metrics dict with 'is_valid' (bool) and diagnostics.
        """
        # Check for task-specific validator first
        validator = self._task_validators.get(task_name)
        if validator:
            try:
                metrics = validator(data)
                if "is_valid" not in metrics:
                    metrics["is_valid"] = True  # Default if validator forgets
                metrics["checks_passed"] = metrics.get("checks_passed", [])
                metrics["checks_failed"] = metrics.get("checks_failed", [])
                metrics["validator_used"] = task_name
                return metrics
            except Exception as e:
                return {
                    "is_valid": False,
                    "error": f"Validator for '{task_name}' crashed: {e}",
                    "checks_passed": [],
                    "checks_failed": ["validator_crash"],
                    "validator_used": task_name,
                }
        
        # Generic fallback validation
        metrics = {
            "is_valid": True,
            "checks_passed": [],
            "checks_failed": [],
            "validator_used": "generic",
        }
        
        if not data or (isinstance(data, dict) and len(data) == 1 and "session_id" in data):
            metrics["is_valid"] = False
            metrics["checks_failed"].append("result_empty")
            return metrics
        
        metrics["checks_passed"].append("result_not_empty")
        return metrics
    
    def get_skill_metrics(self, skill_name: Optional[str] = None) -> Dict[str, Any]:
        """Get skill usage metrics.
        
        Args:
            skill_name: If provided, return metrics for a specific skill.
                If None, return all metrics.
                
        Returns:
            Dictionary with skill metrics.
        """
        if skill_name:
            m = self.executor.metrics.get(skill_name)
            if m:
                return {
                    "name": m.name,
                    "invocations": m.invocations,
                    "success_rate": round(m.success_rate, 3),
                    "avg_duration": round(m.avg_duration, 3),
                    "last_used": m.last_used,
                    "last_error": m.last_error,
                }
            return {}
        
        all_metrics = self.executor.metrics.get_all()
        result = {}
        for name, m in all_metrics.items():
            result[name] = {
                "invocations": m.invocations,
                "success_rate": round(m.success_rate, 3),
                "avg_duration": round(m.avg_duration, 3),
            }
        return result
    
    def get_error_learning_report(self) -> Dict[str, Any]:
        """Get report of unknown errors that could be added to the catalog."""
        from agent_harness.self_healer import SelfHealer
        healer = SelfHealer(verbose=False)
        return healer.get_learning_report()
