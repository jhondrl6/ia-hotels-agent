"""Tests for Agent Harness Observer."""

import time

import pytest

from agent_harness.observer import Observer, ExecutionMetrics, observe


class TestExecutionMetrics:
    """Tests for ExecutionMetrics dataclass."""
    
    def test_mark_stage_adds_stage(self):
        """mark_stage should add stage to list."""
        metrics = ExecutionMetrics()
        metrics.mark_stage("geo")
        metrics.mark_stage("ia")
        
        assert metrics.stages_completed == ["geo", "ia"]
    
    def test_mark_stage_no_duplicates(self):
        """mark_stage should not add duplicate stages."""
        metrics = ExecutionMetrics()
        metrics.mark_stage("geo")
        metrics.mark_stage("geo")
        
        assert metrics.stages_completed == ["geo"]
    
    def test_to_dict(self):
        """to_dict should return dictionary representation."""
        metrics = ExecutionMetrics(
            duration_seconds=1.5,
            stages_completed=["geo", "ia"],
            exception_type="TimeoutError",
            retries=2,
        )
        
        result = metrics.to_dict()
        
        assert result["duration_seconds"] == 1.5
        assert result["stages_completed"] == ["geo", "ia"]
        assert result["exception_type"] == "TimeoutError"
        assert result["retries"] == 2


class TestObserver:
    """Tests for Observer class."""
    
    def test_observe_captures_success(self):
        """observe decorator should capture successful execution."""
        observer = Observer(verbose=False)
        
        @observer.observe
        def my_func():
            return "result"
        
        result, metrics = my_func()
        
        assert result == "result"
        assert metrics.duration_seconds > 0
        assert metrics.exception_type is None
    
    def test_observe_captures_exception(self):
        """observe decorator should capture exception."""
        observer = Observer(verbose=False)
        
        @observer.observe
        def my_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            my_func()
    
    def test_observe_measures_duration(self):
        """observe decorator should measure execution time."""
        observer = Observer(verbose=False)
        
        @observer.observe
        def slow_func():
            time.sleep(0.1)
            return "done"
        
        result, metrics = slow_func()
        
        assert metrics.duration_seconds >= 0.1
    
    def test_mark_stage_during_execution(self):
        """mark_stage should work during observed execution."""
        observer = Observer(verbose=False)
        
        @observer.observe
        def my_func():
            observer.mark_stage("step1")
            observer.mark_stage("step2")
            return "done"
        
        result, metrics = my_func()
        
        assert "step1" in metrics.stages_completed
        assert "step2" in metrics.stages_completed


class TestObserveDecorator:
    """Tests for standalone observe decorator."""
    
    def test_observe_without_args(self):
        """observe can be used without parentheses."""
        @observe
        def my_func():
            return "result"
        
        result, metrics = my_func()
        
        assert result == "result"
        assert isinstance(metrics, ExecutionMetrics)
