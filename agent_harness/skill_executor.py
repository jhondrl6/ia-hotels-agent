"""Skill Executor for Agent Harness.

Parses and executes workflow steps from markdown files.
"""

import csv
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from agent_harness.skill_router import SkillDefinition
from agent_harness.types import SkillMetrics


class StepType(Enum):
    """Type of workflow step."""
    COMMAND = "command"      # Shell command to execute
    MANUAL = "manual"        # Manual action (requires human)
    CHECK = "check"          # Prerequisite check


@dataclass
class WorkflowStep:
    """A single step in a workflow.
    
    Attributes:
        number: Step number (1, 2, 3...).
        title: Step title from header.
        description: Explanation text before code block.
        step_type: Type of step (command, manual, check).
        code: Code block content if present.
        validation: Expected validation criteria.
        is_turbo: Whether this step can auto-execute.
        is_background: Whether this step should run in background.
    """
    number: int
    title: str
    description: str = ""
    step_type: StepType = StepType.MANUAL
    code: str = ""
    validation: str = ""
    is_turbo: bool = False
    is_background: bool = False


@dataclass
class ExecutionResult:
    """Result of executing a workflow step or skill.
    
    Attributes:
        success: True if execution completed.
        steps_executed: List of step numbers that were executed.
        steps_skipped: List of step numbers that were skipped (manual).
        output: Combined output from executed commands.
        error: Error message if failed.
        background_tasks: List of dicts with info about background tasks started.
    """
    success: bool
    steps_executed: List[int] = field(default_factory=list)
    steps_skipped: List[int] = field(default_factory=list)
    output: str = ""
    error: Optional[str] = None
    background_tasks: List[Dict[str, Any]] = field(default_factory=list)


class SkillMetricsCollector:
    """Persistent statistics collector for skill invocations.
    
    Writes metrics to a simple CSV file that survives across sessions.
    """
    
    DEFAULT_METRICS_PATH = Path(__file__).parent.parent / ".agent" / "memory" / "skill_metrics.csv"
    
    def __init__(self, metrics_path: Optional[Path] = None):
        self.metrics_path = metrics_path or self.DEFAULT_METRICS_PATH
        self.metrics: Dict[str, SkillMetrics] = {}
        self._load_metrics()
        self._ensure_dir()
    
    def _ensure_dir(self):
        self.metrics_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_metrics(self):
        """Load metrics from CSV file."""
        if not self.metrics_path.exists():
            return
        
        try:
            with open(self.metrics_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    m = SkillMetrics(
                        name=row["name"],
                        invocations=int(row.get("invocations", 0)),
                        successes=int(row.get("successes", 0)),
                        failures=int(row.get("failures", 0)),
                        total_duration_seconds=float(row.get("total_duration_seconds", 0.0)),
                        last_used=row.get("last_used") or None,
                        last_error=row.get("last_error") or None,
                    )
                    if m.name:
                        self.metrics[m.name] = m
        except (IOError, KeyError, ValueError):
            self.metrics = {}
    
    def _save_metrics(self):
        """Persist metrics to CSV."""
        try:
            with open(self.metrics_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "name", "invocations", "successes", "failures",
                    "total_duration_seconds", "last_used", "last_error"
                ])
                for m in self.metrics.values():
                    writer.writerow([
                        m.name, m.invocations, m.successes, m.failures,
                        round(m.total_duration_seconds, 3), m.last_used or "",
                        m.last_error or ""
                    ])
        except IOError:
            pass  # Non-critical
    
    def record(self, skill_name: str, duration: float, success: bool, error: Optional[str] = None) -> SkillMetrics:
        """Record a skill execution and persist."""
        if skill_name not in self.metrics:
            self.metrics[skill_name] = SkillMetrics(name=skill_name)
        
        self.metrics[skill_name].record(duration, success, error)
        self._save_metrics()
        return self.metrics[skill_name]
    
    def get(self, skill_name: str) -> Optional[SkillMetrics]:
        """Get metrics for a skill."""
        return self.metrics.get(skill_name)
    
    def get_all(self) -> Dict[str, SkillMetrics]:
        """Get all skill metrics."""
        return dict(self.metrics)


class SkillExecutor:
    """Parses and executes workflow steps.
    
    Reads workflow markdown files and executes command steps,
    respecting `// turbo` annotations for auto-execution.
    """
    
    def __init__(
        self, 
        command_runner: Optional[Callable[[str], Tuple[int, str]]] = None,
        verbose: bool = True,
        auto_turbo: bool = False,
    ):
        """Initialize SkillExecutor.
        
        Args:
            command_runner: Callable that executes commands and returns (exit_code, output).
            verbose: If True, print execution info.
            auto_turbo: If True, auto-execute turbo-marked steps.
        """
        self.command_runner = command_runner
        self.verbose = verbose
        self.auto_turbo = auto_turbo
        self.metrics = SkillMetricsCollector()
    
    def parse_workflow(self, skill: SkillDefinition) -> List[WorkflowStep]:
        """Parse a workflow file into steps.
        
        Args:
            skill: SkillDefinition with path to parse.
            
        Returns:
            List of WorkflowStep objects.
        """
        try:
            content = skill.path.read_text(encoding="utf-8")
        except IOError as e:
            if self.verbose:
                print(f"[EXECUTOR] Failed to read workflow: {e}")
            return []
        
        # Check for turbo-all annotation
        turbo_all = "// turbo-all" in content
        
        steps: List[WorkflowStep] = []
        
        # Find all step headers (### 1. Title)
        step_pattern = r"(?:// turbo\s*\n)?(?:// background\s*\n)?###\s+(\d+)\.\s+(.+?)(?=\n)"
        step_matches = list(re.finditer(step_pattern, content))
        
        for i, match in enumerate(step_matches):
            step_start = match.start()
            step_end = step_matches[i + 1].start() if i + 1 < len(step_matches) else len(content)
            step_content = content[step_start:step_end]
            
            # Check if this step has annotations (line above)
            pre_match_content = content[max(0, step_start - 40):step_start]
            is_turbo = turbo_all or "// turbo" in pre_match_content or "// turbo" in match.group(0)
            is_background = "// background" in pre_match_content or "// background" in match.group(0)
            
            step_number = int(match.group(1))
            step_title = match.group(2).strip()
            
            # Extract description (text between header and code block)
            desc_match = re.search(r"###.+?\n(.+?)(?=```|\*Validación*|$)", step_content, re.DOTALL)
            desc_text = desc_match.group(1).strip() if desc_match else ""
            # Support reading Constraints/Scope to description
            scope_match = re.search(r"## Fronteras.+?\n(.+?)(?=##|\Z)", content, re.DOTALL)
            scope_text = scope_match.group(1).strip() if scope_match else ""
            description = f"{desc_text}\nScope: {scope_text}".strip()
            
            # Extract code block
            code_match = re.search(r"```(?:bash|powershell|python)?\s*\n(.+?)```", step_content, re.DOTALL)
            code = code_match.group(1).strip() if code_match else ""
            
            # Determine step type
            if code:
                step_type = StepType.COMMAND
            else:
                step_type = StepType.MANUAL
            
            # Extract validation
            validation_match = re.search(r"\*Validación\*:\s*(.+?)(?=\n\n|\n###|$)", step_content, re.DOTALL)
            validation = validation_match.group(1).strip() if validation_match else ""
            
            steps.append(WorkflowStep(
                number=step_number,
                title=step_title,
                description=description,
                step_type=step_type,
                code=code,
                validation=validation,
                is_turbo=is_turbo,
                is_background=is_background,
            ))
        
        return steps
    
    def get_executable_steps(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """Get steps that can be executed programmatically.
        
        Args:
            steps: All workflow steps.
            
        Returns:
            Steps with commands that can be auto-executed.
        """
        return [
            s for s in steps
            if s.step_type == StepType.COMMAND and (s.is_turbo or self.auto_turbo)
        ]
    
    def execute_skill(
        self, 
        skill: SkillDefinition,
        dry_run: bool = False,
        context_data: Optional[Dict[str, Any]] = None,
    ) -> ExecutionResult:
        """Execute a skill workflow.
        
        Args:
            skill: SkillDefinition to execute.
            dry_run: If True, only report what would be executed.
                DRY_RUN defaults to False -- set True to skip actual execution.
            context_data: Optional data for placeholder resolution ({{key}}).
            
        Returns:
            ExecutionResult with execution details.
        """
        import time
        
        steps = self.parse_workflow(skill)
        
        if not steps:
            return ExecutionResult(
                success=False,
                error=f"No steps found in workflow: {skill.name}",
            )
        
        if self.verbose:
            print(f"[EXECUTOR] Workflow '{skill.name}' has {len(steps)} steps")
        
        executable = self.get_executable_steps(steps)
        manual_steps = [s for s in steps if s not in executable]
        
        if self.verbose:
            print(f"[EXECUTOR] {len(executable)} auto-executable, {len(manual_steps)} manual")
        
        if dry_run:
            return ExecutionResult(
                success=True,
                steps_executed=[],
                steps_skipped=[s.number for s in steps],
                output=f"DRY RUN: Would execute {len(executable)} steps",
            )
        
        # Execute steps
        outputs = []
        executed = []
        skipped = []
        bg_tasks = []
        error = None
        
        for step in steps:
            if step in executable and self.command_runner:
                command = step.code
                
                # Resolve placeholders
                if context_data:
                    for key, value in context_data.items():
                        placeholder = f"{{{{{key}}}}}"
                        if placeholder in command:
                            command = command.replace(placeholder, str(value))
                
                if self.verbose:
                    print(f"[EXECUTOR] Step {step.number}: {step.title}")
                    if step.is_background:
                        print(f"[EXECUTOR] Running in BACKGROUND")
                
                # Adapt command_runner to accept is_background if possible
                start = time.time()
                try:
                    import inspect
                    sig = inspect.signature(self.command_runner)
                    if "is_background" in sig.parameters:
                        exit_code, output = self.command_runner(command, is_background=step.is_background)
                    else:
                        exit_code, output = self.command_runner(command)
                except Exception as e:
                    exit_code, output = 1, str(e)
                
                duration = time.time() - start
                outputs.append(f"Step {step.number}: {output}")
                
                if step.is_background:
                    bg_tasks.append({
                        "step_number": step.number,
                        "title": step.title,
                        "command": command,
                        "output": output,
                    })
                
                if exit_code != 0 and not step.is_background:
                    error = f"Step {step.number} failed with exit code {exit_code}"
                    self.metrics.record(skill.name, duration, success=False, error=error)
                    return ExecutionResult(
                        success=False,
                        steps_executed=executed,
                        steps_skipped=skipped,
                        output="\n".join(outputs),
                        error=error,
                        background_tasks=bg_tasks,
                    )
                
                executed.append(step.number)
            else:
                if self.verbose:
                    print(f"[EXECUTOR] Step {step.number} (manual): {step.title}")
                skipped.append(step.number)
        
        self.metrics.record(skill.name, time.time() - start, success=True)
        
        return ExecutionResult(
            success=True,
            steps_executed=executed,
            steps_skipped=skipped,
            output="\n".join(outputs),
            background_tasks=bg_tasks,
        )
    
    def get_step_summary(self, skill: SkillDefinition) -> Dict[str, Any]:
        """Get summary of workflow steps without execution.
        
        Args:
            skill: SkillDefinition to summarize.
            
        Returns:
            Dictionary with step summary.
        """
        steps = self.parse_workflow(skill)
        
        return {
            "skill": skill.name,
            "total_steps": len(steps),
            "auto_executable": len(self.get_executable_steps(steps)),
            "manual_required": len([s for s in steps if s.step_type == StepType.MANUAL]),
            "steps": [
                {
                    "number": s.number,
                    "title": s.title,
                    "type": s.step_type.value,
                    "turbo": s.is_turbo,
                }
                for s in steps
            ],
        }
