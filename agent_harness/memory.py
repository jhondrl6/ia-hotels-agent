"""Memory Manager for Agent Harness.

Handles persistent storage and retrieval of execution history.
Uses session-based file storage for improved scalability and multi-tenant support.

v3.1: Added thread safety (per-session locks) + inverted index for O(1) target lookups.
"""

import json
import threading
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timezone, timedelta

from agent_harness.types import TaskContext


class MemoryManager:
    """Manages execution history and context injection.
    
    Stores each session as an individual JSON file in sessions/ directory.
    Format: sessions/YYYY-MM-DD_{session_id}.json
    
    Thread safety: uses a threading.Lock per session file to prevent
    concurrent read-modify-write race conditions.
    
    Inverted index: maintains target_id -> [session_file_paths] mapping
    so load_history() scans only relevant files instead of all sessions.
    """
    
    DEFAULT_MEMORY_PATH = Path(__file__).parent.parent / ".agent" / "memory"
    SESSIONS_DIR = "sessions"
    INDEX_FILE = "target_index.json"
    LEGACY_HISTORY_FILE = "execution_history.jsonl"  # For migration compatibility
    
    def __init__(self, memory_path: Optional[Path] = None, session_id: Optional[str] = None):
        """Initialize MemoryManager.
        
        Args:
            memory_path: Path to memory directory. Defaults to .agent/memory/.
            session_id: Optional session identifier. Auto-generated if not provided.
        """
        self.memory_path = memory_path or self.DEFAULT_MEMORY_PATH
        self.sessions_path = self.memory_path / self.SESSIONS_DIR
        self.session_id = session_id or self._generate_session_id()
        self._current_session_file: Optional[Path] = None
        
        # Thread safety: one lock per session file path
        self._locks: Dict[str, threading.Lock] = {}
        self._locks_lock = threading.Lock()  # Lock for the locks dict itself
        
        # Inverted index: target_id -> list of session file paths (str)
        self._target_index: Dict[str, List[str]] = {}
        
        self._ensure_directories_exist()
        self._load_target_index()
    
    def _get_lock_for_file(self, file_path: Path) -> threading.Lock:
        """Get or create a lock for a specific session file. Thread-safe."""
        key = str(file_path.resolve())
        with self._locks_lock:
            if key not in self._locks:
                self._locks[key] = threading.Lock()
            return self._locks[key]
    
    def _generate_session_id(self) -> str:
        """Generate a unique session identifier."""
        date_prefix = datetime.now().strftime("%Y-%m-%d")
        short_uuid = uuid.uuid4().hex[:8]
        return f"{date_prefix}_{short_uuid}"
    
    def _ensure_directories_exist(self) -> None:
        """Create memory and sessions directories if they don't exist."""
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.sessions_path.mkdir(parents=True, exist_ok=True)
    
    def _get_session_file_path(self, session_id: Optional[str] = None) -> Path:
        """Get the path for a session file."""
        sid = session_id or self.session_id
        return self.sessions_path / f"{sid}.json"
    
    def _load_session_file(self, file_path: Path) -> Dict[str, Any]:
        """Load a single session file."""
        try:
            if file_path.exists():
                return json.loads(file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            pass
        return {"session_id": file_path.stem, "entries": []}
    
    def _save_session_file(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """Save session data to file. Caller must hold the lock for this file."""
        try:
            # Atomic write: write to temp, then rename
            tmp_path = file_path.with_suffix(".tmp")
            tmp_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            tmp_path.replace(file_path)
            return True
        except IOError as e:
            print(f"[HARNESS WARN] Failed to write session: {e}")
            return False
    
    def _load_target_index(self) -> None:
        """Load the inverted index from disk if it exists."""
        index_path = self.memory_path / self.INDEX_FILE
        if index_path.exists():
            try:
                self._target_index = json.loads(index_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                self._target_index = {}
        else:
            # First time: build index from existing sessions
            self._build_target_index()
    
    def _build_target_index(self) -> None:
        """Scan all session files and build the inverted index from scratch."""
        self._target_index = {}
        
        session_files = sorted(self.sessions_path.glob("*.json"))
        for session_file in session_files:
            session_data = self._load_session_file(session_file)
            file_path_str = str(session_file.resolve())
            for entry in session_data.get("entries", []):
                target_id = entry.get("target_id")
                if target_id:
                    if target_id not in self._target_index:
                        self._target_index[target_id] = []
                    if file_path_str not in self._target_index[target_id]:
                        self._target_index[target_id].append(file_path_str)
        
        self._save_target_index()
    
    def _save_target_index(self) -> None:
        """Persist the inverted index to disk."""
        index_path = self.memory_path / self.INDEX_FILE
        try:
            tmp_path = index_path.with_suffix(".tmp")
            tmp_path.write_text(
                json.dumps(self._target_index, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            tmp_path.replace(index_path)
        except IOError:
            pass  # Non-critical: index can be rebuilt
    
    def _update_target_index(self, target_id: str, session_file: Path) -> None:
        """Add a session file to the inverted index for a target_id. Thread-safe."""
        # Note: we don't need a lock here because the dict mutation is GIL-safe
        # for single-key updates; the index is saved on append_log anyway.
        if target_id not in self._target_index:
            self._target_index[target_id] = []
        file_path_str = str(session_file.resolve())
        if file_path_str not in self._target_index[target_id]:
            self._target_index[target_id].append(file_path_str)
    
    def load_history(self, target_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Load execution history for a specific target.
        
        Uses the inverted index to scan ONLY session files that contain
        entries for the given target_id, instead of scanning ALL sessions.
        
        Args:
            target_id: Unique identifier for the target (e.g., URL).
            limit: Maximum number of records to return (most recent first).
            
        Returns:
            List of execution log entries matching the target_id.
        """
        matching_entries: List[Dict[str, Any]] = []
        
        # Use inverted index to find relevant session files
        session_path_strs = self._target_index.get(target_id, [])
        
        for session_path_str in session_path_strs:
            session_file = Path(session_path_str)
            if not session_file.exists():
                # Clean stale index entry
                continue
            
            session_data = self._load_session_file(session_file)
            for entry in session_data.get("entries", []):
                if entry.get("target_id") == target_id:
                    matching_entries.append(entry)
        
        # If index is empty (e.g., first run or corrupted), fall back to full scan
        if not matching_entries:
            session_files = sorted(self.sessions_path.glob("*.json"))
            for session_file in session_files:
                session_data = self._load_session_file(session_file)
                for entry in session_data.get("entries", []):
                    if entry.get("target_id") == target_id:
                        matching_entries.append(entry)
        
        # Return most recent entries first
        return matching_entries[-limit:][::-1]
    
    def build_context(self, target_id: str) -> TaskContext:
        """Build a TaskContext from historical data.
        
        Args:
            target_id: Unique identifier for the target.
            
        Returns:
            TaskContext with historical information injected.
        """
        history = self.load_history(target_id, limit=5)
        
        if not history:
            return TaskContext()
        
        last_entry = history[0]  # Most recent
        suggestions = []
        
        # Generate suggestions based on patterns
        error_count = sum(1 for e in history if e.get("outcome") == "error")
        if error_count >= 2:
            suggestions.append(f"This target has failed {error_count} times recently. Consider manual review.")
        
        if last_entry.get("error_type") == "TimeoutError":
            suggestions.append("Last failure was timeout. Consider increasing wait times.")
        
        return TaskContext(
            previous_runs=len(history),
            last_outcome=last_entry.get("outcome"),
            last_error_type=last_entry.get("error_type"),
            suggestions=suggestions,
        )
    
    def append_log(self, entry: Dict[str, Any]) -> bool:
        """Append a log entry to the current session file. Thread-safe.
        
        Uses per-file locking to prevent race conditions when multiple
        threads/appends happen concurrently.
        
        Args:
            entry: Dictionary to add to session log.
            
        Returns:
            True if write was successful.
        """
        session_file = self._get_session_file_path()
        lock = self._get_lock_for_file(session_file)
        
        with lock:
            session_data = self._load_session_file(session_file)
            
            # Add timestamp if not present
            if "timestamp" not in entry:
                entry["timestamp"] = datetime.now(timezone.utc).isoformat()
            
            # Add session_id reference
            entry["session_id"] = self.session_id
            
            session_data["entries"].append(entry)
            session_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            success = self._save_session_file(session_file, session_data)
            
            # Update inverted index
            if success:
                target_id = entry.get("target_id")
                if target_id:
                    self._update_target_index(target_id, session_file)
                    # Periodically persist index (every 10th append heuristic)
                    entry_count = len(session_data.get("entries", []))
                    if entry_count % 10 == 0:
                        self._save_target_index()
            
            return success
    
    def get_all_targets(self) -> List[str]:
        """Get list of all unique target_ids in history.
        
        Returns:
            List of unique target identifiers.
        """
        return list(self._target_index.keys())
    
    def get_session_ids(self) -> List[str]:
        """Get list of all session IDs.
        
        Returns:
            List of session identifiers (filenames without extension).
        """
        return [f.stem for f in sorted(self.sessions_path.glob("*.json"))]
    
    def load_session(self, session_id: str) -> Dict[str, Any]:
        """Load a specific session by ID.
        
        Args:
            session_id: The session identifier.
            
        Returns:
            Session data dictionary with entries.
        """
        session_file = self._get_session_file_path(session_id)
        return self._load_session_file(session_file)

    def save_state(self, state: Dict[str, Any]) -> bool:
        """Save current operational state (e.g., current URL).
        
        Args:
            state: Dictionary with state data.
            
        Returns:
            True if successful.
        """
        state_file = self.memory_path / "current_state.json"
        try:
            state["last_updated"] = datetime.now(timezone.utc).isoformat()
            state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
            return True
        except IOError:
            return False

    def load_state(self) -> Dict[str, Any]:
        """Load the last saved operational state.
        
        Returns:
            Dictionary with saved state or empty dict.
        """
        state_file = self.memory_path / "current_state.json"
        if not state_file.exists():
            return {}
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            return {}

    def find_latest_analysis(self, target_id: str) -> Optional[Path]:
        """Find the most recent analisis_completo.json for a target.
        
        Searches in:
        1. Session history (analysis_path stored in entries)
        2. output/{target_id}_{timestamp}/evidencias/raw_data/
        
        Args:
            target_id: Unique identifier for the target (hotel name/URL).
            
        Returns:
            Path to the most recent analysis JSON file, or None if not found.
        """
        # First, check session history for stored analysis paths
        history = self.load_history(target_id, limit=20)
        for entry in history:
            analysis_path = entry.get("analysis_path")
            if analysis_path:
                path = Path(analysis_path)
                if path.exists():
                    return path
        
        # Second, scan output directories for analisis_completo.json
        output_dir = Path("output")
        if not output_dir.exists():
            return None
        
        target_lower = target_id.lower().replace(" ", "").replace("_", "")
        candidate_dirs = []
        
        for dir_path in output_dir.iterdir():
            if not dir_path.is_dir():
                continue
            
            dir_name = dir_path.name.lower()
            # Match directory names like "hotelvisperas_20260225_131029"
            if target_lower in dir_name:
                analysis_file = dir_path / "evidencias" / "raw_data" / "analisis_completo.json"
                if analysis_file.exists():
                    # Get modification time for sorting
                    mtime = analysis_file.stat().st_mtime
                    candidate_dirs.append((mtime, analysis_file))
        
        if candidate_dirs:
            # Return most recent
            candidate_dirs.sort(key=lambda x: x[0], reverse=True)
            return candidate_dirs[0][1]
        
        return None

    def save_analysis_reference(self, target_id: str, analysis_path: Path, metadata: dict = None) -> bool:
        """Save reference to analysis file in session history.

        Args:
            target_id: Unique identifier for the target.
            analysis_path: Path to the analisis_completo.json file.
            metadata: Optional metadata dictionary to include in the log entry.

        Returns:
            True if save was successful.
        """
        entry = {
            "target_id": target_id,
            "action": "analysis_reference",
            "analysis_path": str(analysis_path.absolute()),
            "outcome": "reference_saved",
        }
        if metadata:
            entry["metadata"] = metadata
        return self.append_log(entry)

    def cleanup_old_sessions(self, days: int = 20) -> int:
        """Remove session files older than specified days.
        
        Args:
            days: Number of days to retain. Default 20.
            
        Returns:
            Number of files removed.
        """
        if not self.sessions_path.exists():
            return 0
        
        cutoff = datetime.now() - timedelta(days=days)
        removed_count = 0
        
        for session_file in self.sessions_path.glob("*.json"):
            try:
                # Parse date from filename: YYYY-MM-DD_*.json
                filename = session_file.stem
                date_part = filename.split("_")[0]
                file_date = datetime.strptime(date_part, "%Y-%m-%d")
                
                if file_date < cutoff:
                    # Remove from inverted index
                    file_path_str = str(session_file.resolve())
                    for target_id, paths in self._target_index.items():
                        if file_path_str in paths:
                            paths.remove(file_path_str)
                    
                    session_file.unlink()
                    removed_count += 1
            except (ValueError, OSError):
                # Skip files that don't match the pattern or can't be deleted
                continue
        
        # Clean empty index entries and rebuild if significant cleanup
        self._target_index = {k: v for k, v in self._target_index.items() if v}
        self._save_target_index()
        
        return removed_count
    
    def rebuild_index(self) -> int:
        """Force-rebuild the inverted index from scratch.
        
        Useful if the index got corrupted or out of sync.
        
        Returns:
            Number of entries indexed.
        """
        old_count = len(self._target_index)
        self._build_target_index()
        new_count = len(self._target_index)
        return new_count
