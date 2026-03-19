"""Tests for Agent Harness Memory Manager.

Updated for session-based storage (v3.0).
"""

import json
import tempfile
from pathlib import Path

import pytest

from agent_harness.memory import MemoryManager
from agent_harness.types import TaskContext


class TestMemoryManager:
    """Tests for MemoryManager class."""
    
    @pytest.fixture
    def temp_memory_dir(self):
        """Create a temporary directory for memory files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def manager(self, temp_memory_dir):
        """Create a MemoryManager with temporary storage."""
        return MemoryManager(memory_path=temp_memory_dir, session_id="test-session-001")
    
    def test_init_creates_directories(self, temp_memory_dir):
        """MemoryManager should create memory and sessions directories."""
        manager = MemoryManager(memory_path=temp_memory_dir)
        assert (temp_memory_dir / "sessions").exists()
        assert (temp_memory_dir / "sessions").is_dir()
    
    def test_session_id_auto_generated(self, temp_memory_dir):
        """MemoryManager should auto-generate session_id if not provided."""
        manager = MemoryManager(memory_path=temp_memory_dir)
        assert manager.session_id is not None
        assert len(manager.session_id) > 10  # Format: YYYY-MM-DD_shortid
    
    def test_append_log_creates_session_file(self, manager, temp_memory_dir):
        """append_log should create a session file with entry."""
        entry = {"target_id": "https://hotel.com", "outcome": "success"}
        result = manager.append_log(entry)
        
        assert result is True
        session_file = temp_memory_dir / "sessions" / "test-session-001.json"
        assert session_file.exists()
        
        content = json.loads(session_file.read_text())
        assert len(content["entries"]) == 1
        assert content["entries"][0]["target_id"] == "https://hotel.com"
    
    def test_append_log_adds_timestamp(self, manager, temp_memory_dir):
        """append_log should add timestamp if not present."""
        entry = {"target_id": "https://hotel.com", "outcome": "success"}
        manager.append_log(entry)
        
        session_file = temp_memory_dir / "sessions" / "test-session-001.json"
        content = json.loads(session_file.read_text())
        
        assert "timestamp" in content["entries"][0]
    
    def test_load_history_returns_matching_entries(self, manager, temp_memory_dir):
        """load_history should return entries matching target_id."""
        manager.append_log({"target_id": "https://hotel-a.com", "outcome": "success"})
        manager.append_log({"target_id": "https://hotel-b.com", "outcome": "error"})
        manager.append_log({"target_id": "https://hotel-a.com", "outcome": "error"})
        
        history = manager.load_history("https://hotel-a.com")
        
        assert len(history) == 2
        assert all(e["target_id"] == "https://hotel-a.com" for e in history)
    
    def test_load_history_returns_most_recent_first(self, manager):
        """load_history should return entries in reverse chronological order."""
        manager.append_log({"target_id": "https://hotel.com", "outcome": "success", "run": 1})
        manager.append_log({"target_id": "https://hotel.com", "outcome": "error", "run": 2})
        manager.append_log({"target_id": "https://hotel.com", "outcome": "success", "run": 3})
        
        history = manager.load_history("https://hotel.com")
        
        assert history[0]["run"] == 3  # Most recent first
        assert history[2]["run"] == 1  # Oldest last
    
    def test_load_history_across_sessions(self, temp_memory_dir):
        """load_history should find entries across multiple session files."""
        # Create entries in two different sessions
        manager1 = MemoryManager(memory_path=temp_memory_dir, session_id="2026-01-14_session1")
        manager1.append_log({"target_id": "https://hotel.com", "outcome": "success", "run": 1})
        
        manager2 = MemoryManager(memory_path=temp_memory_dir, session_id="2026-01-15_session2")
        manager2.append_log({"target_id": "https://hotel.com", "outcome": "error", "run": 2})
        
        # Query from any manager should find both
        history = manager2.load_history("https://hotel.com")
        
        assert len(history) == 2
        assert history[0]["run"] == 2  # Most recent first
        assert history[1]["run"] == 1
    
    def test_load_history_empty_for_unknown_target(self, manager):
        """load_history should return empty list for unknown target."""
        manager.append_log({"target_id": "https://hotel-a.com", "outcome": "success"})
        
        history = manager.load_history("https://unknown.com")
        
        assert history == []
    
    def test_build_context_empty_for_new_target(self, manager):
        """build_context should return default context for unknown target."""
        context = manager.build_context("https://new-hotel.com")
        
        assert context.previous_runs == 0
        assert context.last_outcome is None
        assert context.suggestions == []
    
    def test_build_context_includes_history_info(self, manager):
        """build_context should include previous run info."""
        manager.append_log({"target_id": "https://hotel.com", "outcome": "success"})
        manager.append_log({"target_id": "https://hotel.com", "outcome": "error", "error_type": "TimeoutError"})
        
        context = manager.build_context("https://hotel.com")
        
        assert context.previous_runs == 2
        assert context.last_outcome == "error"
        assert context.last_error_type == "TimeoutError"
    
    def test_build_context_suggests_on_repeated_failures(self, manager):
        """build_context should add suggestions when target has multiple failures."""
        for _ in range(3):
            manager.append_log({"target_id": "https://hotel.com", "outcome": "error"})
        
        context = manager.build_context("https://hotel.com")
        
        assert len(context.suggestions) >= 1
        assert "failed" in context.suggestions[0].lower() or "falló" in context.suggestions[0].lower() or "failed 3 times" in context.suggestions[0]
    
    def test_get_all_targets(self, manager):
        """get_all_targets should return unique target_ids."""
        manager.append_log({"target_id": "https://hotel-a.com", "outcome": "success"})
        manager.append_log({"target_id": "https://hotel-b.com", "outcome": "success"})
        manager.append_log({"target_id": "https://hotel-a.com", "outcome": "error"})
        
        targets = manager.get_all_targets()
        
        assert set(targets) == {"https://hotel-a.com", "https://hotel-b.com"}
    
    def test_get_session_ids(self, temp_memory_dir):
        """get_session_ids should return all session IDs."""
        manager1 = MemoryManager(memory_path=temp_memory_dir, session_id="2026-01-14_abc")
        manager1.append_log({"target_id": "https://hotel.com", "outcome": "success"})
        
        manager2 = MemoryManager(memory_path=temp_memory_dir, session_id="2026-01-15_def")
        manager2.append_log({"target_id": "https://hotel.com", "outcome": "success"})
        
        session_ids = manager2.get_session_ids()
        
        assert "2026-01-14_abc" in session_ids
        assert "2026-01-15_def" in session_ids
    
    def test_load_session(self, manager, temp_memory_dir):
        """load_session should return session data by ID."""
        manager.append_log({"target_id": "https://hotel.com", "outcome": "success"})
        manager.append_log({"target_id": "https://hotel.com", "outcome": "error"})
        
        session_data = manager.load_session("test-session-001")
        
        assert len(session_data["entries"]) == 2
        assert session_data["session_id"] == "test-session-001"
