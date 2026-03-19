"""Tests for Agent Harness Core."""

import tempfile
from pathlib import Path

import pytest

from agent_harness.core import AgentHarness
from agent_harness.memory import MemoryManager
from agent_harness.types import AgentTask, TaskContext


class TestAgentHarness:
    """Tests for AgentHarness class."""
    
    @pytest.fixture
    def temp_memory_dir(self):
        """Create a temporary directory for memory files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def harness(self, temp_memory_dir):
        """Create an AgentHarness with temporary storage."""
        memory = MemoryManager(memory_path=temp_memory_dir)
        return AgentHarness(memory_manager=memory, verbose=False)
    
    def test_register_handler(self, harness):
        """register_handler should store the handler."""
        def my_handler(payload, context):
            return {"result": "ok"}
        
        harness.register_handler("test_task", my_handler)
        
        assert "test_task" in harness._task_handlers
    
    def test_run_task_calls_handler(self, harness):
        """run_task should call the registered handler."""
        call_record = []
        
        def my_handler(payload, context):
            call_record.append(payload)
            return {"key": "value"}
        
        harness.register_handler("test_task", my_handler)
        task = AgentTask(name="test_task", payload={"input": "data"})
        
        result = harness.run_task(task)
        
        assert len(call_record) == 1
        assert call_record[0] == {"input": "data"}
    
    def test_run_task_returns_success_on_valid_result(self, harness):
        """run_task should return success=True when handler succeeds."""
        def my_handler(payload, context):
            return {"data": "result"}
        
        harness.register_handler("test_task", my_handler)
        task = AgentTask(name="test_task", payload={})
        
        result = harness.run_task(task)
        
        assert result.success is True
        assert result.outcome in ("success", "partial_failure")
    
    def test_run_task_returns_error_on_exception(self, harness):
        """run_task should return success=False when handler raises."""
        def my_handler(payload, context):
            raise ValueError("Test error")
        
        harness.register_handler("test_task", my_handler)
        task = AgentTask(name="test_task", payload={})
        
        result = harness.run_task(task)
        
        assert result.success is False
        assert result.outcome == "error"
        assert result.error_type == "ValueError"
        assert "Test error" in result.error
    
    def test_run_task_returns_error_for_unknown_handler(self, harness):
        """run_task should return error for unregistered task."""
        task = AgentTask(name="unknown_task", payload={})
    
        result = harness.run_task(task)
    
        assert result.success is False
        assert "no meta-skill" in result.error.lower()
    
    def test_run_task_logs_execution(self, harness, temp_memory_dir):
        """run_task should append entry to execution history (session files)."""
        def my_handler(payload, context):
            return {"data": "result"}
        
        harness.register_handler("test_task", my_handler)
        task = AgentTask(name="test_task", payload={"url": "https://test.com"})
        
        harness.run_task(task)
        
        # Check session files (new format)
        sessions_dir = temp_memory_dir / "sessions"
        session_files = list(sessions_dir.glob("*.json"))
        assert len(session_files) >= 1, "At least one session file should exist"
        
        # Read the session file and verify content
        import json
        content = json.loads(session_files[0].read_text())
        entries_str = json.dumps(content)
        assert "test_task" in entries_str
        assert "https://test.com" in entries_str
    
    def test_run_task_injects_context_from_memory(self, temp_memory_dir):
        """run_task should inject context from previous runs."""
        memory = MemoryManager(memory_path=temp_memory_dir)
        # Pre-populate history
        memory.append_log({
            "target_id": "https://hotel.com",
            "task_name": "spark",
            "outcome": "error",
            "error_type": "TimeoutError",
        })
        
        harness = AgentHarness(memory_manager=memory, verbose=False)
        context_received = []
        
        def my_handler(payload, context):
            context_received.append(context)
            return {"data": "result"}
        
        harness.register_handler("spark", my_handler)
        task = AgentTask(name="spark", payload={"url": "https://hotel.com"})
        
        harness.run_task(task)
        
        assert len(context_received) == 1
        ctx = context_received[0]
        assert ctx.previous_runs == 1
        assert ctx.last_outcome == "error"
        assert ctx.last_error_type == "TimeoutError"
    
    def test_validate_result_marks_empty_as_invalid(self, harness):
        """Empty results should be marked as partial_failure."""
        def my_handler(payload, context):
            return {}  # Empty result
        
        harness.register_handler("test_task", my_handler)
        task = AgentTask(name="test_task", payload={})
        
        result = harness.run_task(task)
        
        assert result.outcome == "partial_failure"
        assert "result_empty" in result.quality_metrics.get("checks_failed", [])
