"""Tests para el dashboard de calidad."""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from observability.dashboard import QualityDashboard, RunMetrics, AlertSeverity, AlertType


class TestQualityDashboard:
    """Tests para QualityDashboard."""
    
    @pytest.fixture
    def temp_dashboard(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
            temp_path = f.name
        dashboard = QualityDashboard(storage_path=temp_path)
        yield dashboard
        os.unlink(temp_path)
    
    @pytest.fixture
    def sample_metrics(self):
        return RunMetrics(
            run_id="run-001",
            hotel_id="hotel-test",
            evidence_coverage=0.96,
            hard_contradictions=0,
            soft_contradictions=0,
            financial_validity=True,
            critical_recall=0.95,
            coherence_score=0.85,
            publication_status="READY_FOR_CLIENT",
            url="https://test.com"
        )
    
    def test_record_run_stores_metrics(self, temp_dashboard, sample_metrics):
        temp_dashboard.record_run(sample_metrics)
        latest = temp_dashboard.get_latest_run()
        assert latest is not None
        assert latest.run_id == "run-001"
        assert latest.hotel_id == "hotel-test"
    
    def test_get_trends_returns_correct_data(self, temp_dashboard):
        # Crear corridas de prueba
        for i in range(3):
            metrics = RunMetrics(
                run_id=f"run-{i}",
                hotel_id="hotel-test",
                evidence_coverage=0.95,
                hard_contradictions=0,
                soft_contradictions=0,
                financial_validity=True,
                critical_recall=0.95,
                coherence_score=0.8 + (i * 0.05),
                publication_status="READY_FOR_CLIENT"
            )
            temp_dashboard.record_run(metrics)
        
        trends = temp_dashboard.get_trends(days=7, hotel_id="hotel-test")
        assert trends.total_runs == 3
        assert trends.avg_coherence > 0
    
    def test_check_alerts_detects_low_coherence(self, temp_dashboard):
        metrics = RunMetrics(
            run_id="run-low",
            hotel_id="hotel-test",
            evidence_coverage=0.95,
            hard_contradictions=0,
            soft_contradictions=0,
            financial_validity=True,
            critical_recall=0.95,
            coherence_score=0.49,  # Bajo
            publication_status="DRAFT_INTERNAL"
        )
        temp_dashboard.record_run(metrics)
        
        alerts = temp_dashboard.check_alerts()
        coherence_alerts = [a for a in alerts if a.alert_type == AlertType.COHERENCE_LOW]
        assert len(coherence_alerts) == 1
        assert coherence_alerts[0].severity == AlertSeverity.CRITICAL
    
    def test_check_alerts_detects_low_evidence_coverage(self, temp_dashboard):
        metrics = RunMetrics(
            run_id="run-low-cov",
            hotel_id="hotel-test",
            evidence_coverage=0.85,  # Bajo
            hard_contradictions=0,
            soft_contradictions=0,
            financial_validity=True,
            critical_recall=0.95,
            coherence_score=0.85,
            publication_status="REQUIRES_REVIEW"
        )
        temp_dashboard.record_run(metrics)
        
        alerts = temp_dashboard.check_alerts()
        coverage_alerts = [a for a in alerts if a.alert_type == AlertType.EVIDENCE_COVERAGE_LOW]
        assert len(coverage_alerts) == 1
    
    def test_check_alerts_detects_hard_contradictions(self, temp_dashboard):
        metrics = RunMetrics(
            run_id="run-contra",
            hotel_id="hotel-test",
            evidence_coverage=0.95,
            hard_contradictions=2,  # Hay contradicciones
            soft_contradictions=0,
            financial_validity=True,
            critical_recall=0.95,
            coherence_score=0.85,
            publication_status="DRAFT_INTERNAL"
        )
        temp_dashboard.record_run(metrics)
        
        alerts = temp_dashboard.check_alerts()
        contra_alerts = [a for a in alerts if a.alert_type == AlertType.HARD_CONTRADICTIONS]
        assert len(contra_alerts) == 1
        assert contra_alerts[0].severity == AlertSeverity.CRITICAL
    
    def test_generate_report_includes_all_metrics(self, temp_dashboard, sample_metrics):
        temp_dashboard.record_run(sample_metrics)
        report = temp_dashboard.generate_report()
        
        assert "Reporte de Calidad" in report
        assert "hotel-test" in report
        assert "0.85" in report or "0.96" in report
