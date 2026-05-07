"""Tests para rutas persistentes de evidencia JSON (FASE-PROP-G)."""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from main import _make_evidence_path


class TestMakeEvidencePath:
    """Unit tests for _make_evidence_path helper."""

    def test_builds_correct_path_with_timestamp(self, tmp_path: Path):
        output_dir = tmp_path / "v4_complete"
        hotel_id = "hotel_castilla_real"
        basename = "gate_report"
        timestamp = "20260505_202709"

        path = _make_evidence_path(output_dir, hotel_id, basename, timestamp)

        expected = output_dir / hotel_id / "v4_audit" / f"{basename}_{timestamp}.json"
        assert path == expected

    def test_creates_directories(self, tmp_path: Path):
        output_dir = tmp_path / "v4_complete"
        hotel_id = "amazilia_hotel"
        basename = "audit_report"
        timestamp = "20260505_120000"

        evidence_dir = output_dir / hotel_id / "v4_audit"
        assert not evidence_dir.exists()

        _make_evidence_path(output_dir, hotel_id, basename, timestamp)

        assert evidence_dir.exists()
        assert evidence_dir.is_dir()

    def test_uses_current_time_when_no_timestamp(self, tmp_path: Path):
        output_dir = tmp_path / "v4_complete"
        hotel_id = "test_hotel"
        basename = "financial_scenarios"

        fixed_now = datetime(2026, 5, 5, 20, 27, 9)
        with patch("main.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_now
            # _make_evidence_path calls datetime.now().strftime(...)
            # but since we imported datetime directly in main.py, we patch main.datetime
            path = _make_evidence_path(output_dir, hotel_id, basename)

        expected = output_dir / hotel_id / "v4_audit" / "financial_scenarios_20260505_202709.json"
        assert path == expected

    def test_different_timestamps_produce_different_paths(self, tmp_path: Path):
        output_dir = tmp_path / "v4_complete"
        hotel_id = "hotel_a"
        basename = "gate_report"

        path1 = _make_evidence_path(output_dir, hotel_id, basename, "20260505_120000")
        path2 = _make_evidence_path(output_dir, hotel_id, basename, "20260505_120001")

        assert path1 != path2
        assert path1.parent == path2.parent
        assert path1.name == "gate_report_20260505_120000.json"
        assert path2.name == "gate_report_20260505_120001.json"

    def test_same_basename_same_timestamp_idempotent(self, tmp_path: Path):
        output_dir = tmp_path / "v4_complete"
        hotel_id = "hotel_b"
        basename = "audit_report"
        timestamp = "20260505_120000"

        path1 = _make_evidence_path(output_dir, hotel_id, basename, timestamp)
        path2 = _make_evidence_path(output_dir, hotel_id, basename, timestamp)

        assert path1 == path2

    def test_multiple_basenames_coexist(self, tmp_path: Path):
        output_dir = tmp_path / "v4_complete"
        hotel_id = "hotel_c"
        timestamp = "20260505_120000"

        audit = _make_evidence_path(output_dir, hotel_id, "audit_report", timestamp)
        scenarios = _make_evidence_path(output_dir, hotel_id, "financial_scenarios", timestamp)
        gate = _make_evidence_path(output_dir, hotel_id, "gate_report", timestamp)

        assert audit.name == "audit_report_20260505_120000.json"
        assert scenarios.name == "financial_scenarios_20260505_120000.json"
        assert gate.name == "gate_report_20260505_120000.json"
        assert audit.parent == scenarios.parent == gate.parent


class TestEvidenceNoOverwrite:
    """Integration-style tests verifying successive calls produce distinct files."""

    def test_files_persist_across_runs(self, tmp_path: Path):
        output_dir = tmp_path / "v4_complete"
        hotel_id = "persist_hotel"
        basename = "gate_report"

        # Simulate two runs with different timestamps
        path1 = _make_evidence_path(output_dir, hotel_id, basename, "20260505_120000")
        path2 = _make_evidence_path(output_dir, hotel_id, basename, "20260505_120001")

        # Write dummy content to both
        path1.write_text("{}", encoding="utf-8")
        path2.write_text("{}", encoding="utf-8")

        # Both should exist
        assert path1.exists()
        assert path2.exists()

        # Directory should contain both
        evidence_dir = output_dir / hotel_id / "v4_audit"
        files = list(evidence_dir.glob("*.json"))
        assert len(files) == 2

    def test_actual_file_written_matches_path(self, tmp_path: Path):
        output_dir = tmp_path / "v4_complete"
        hotel_id = "write_test"
        basename = "financial_scenarios"
        timestamp = "20260505_120000"

        path = _make_evidence_path(output_dir, hotel_id, basename, timestamp)
        data = {"hotel": "Test", "value": 42}
        path.write_text(json.dumps(data), encoding="utf-8")

        assert path.exists()
        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert loaded == data
