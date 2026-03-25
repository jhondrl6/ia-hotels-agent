"""
Tests for FASE 10: Health Dashboard - HealthMetricsCollector

Tests:
- test_metrics_collector: Métricas se recolectan correctamente
- test_dashboard_html_generated: HTML con gráficos se genera
- test_dashboard_integrated: Dashboard disponible post-ejecución
"""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

from modules.monitoring.health_metrics_collector import (
    ExecutionMetrics,
    HealthMetricsCollector,
)
from modules.monitoring.health_dashboard_generator import HealthDashboardGenerator


class TestMetricsCollector:
    """Test suite for HealthMetricsCollector."""

    def test_metrics_collector_initialization(self):
        """Test that collector initializes correctly."""
        collector = HealthMetricsCollector()
        
        assert collector._metrics == []
        assert collector._current_execution_start is None
        assert collector._current_hotel_id is None
        assert collector._current_hotel_name is None

    def test_start_and_end_execution(self):
        """Test execution timing with start/end methods."""
        collector = HealthMetricsCollector()
        
        collector.start_execution("hotel_1", "Hotel Test")
        assert collector._current_hotel_id == "hotel_1"
        assert collector._current_hotel_name == "Hotel Test"
        assert collector._current_execution_start is not None
        
        metrics = collector.end_execution()
        
        assert metrics is not None
        assert metrics.hotel_id == "hotel_1"
        assert metrics.hotel_name == "Hotel Test"
        assert metrics.execution_time >= 0

    def test_collect_from_result_with_mock(self):
        """Test collecting metrics from a mock AssetGenerationResult."""
        collector = HealthMetricsCollector()
        collector.start_execution("hotel_2", "Hotel Mock")
        
        # Create a mock result similar to AssetGenerationResult
        mock_result = MagicMock()
        mock_result.generated_assets = [
            MagicMock(confidence_score=0.85),
            MagicMock(confidence_score=0.90),
        ]
        mock_result.failed_assets = [
            MagicMock(asset_type="test_asset", reason="Test failure"),
        ]
        mock_result.hotel_id = "hotel_2"
        mock_result.hotel_name = "Hotel Mock"
        
        metrics = collector.collect_from_result(mock_result)
        
        assert metrics.assets_generated == 2
        assert metrics.assets_failed == 1
        assert metrics.success_rate == pytest.approx(2/3)
        assert metrics.avg_confidence == pytest.approx(0.875)
        assert len(metrics.errors) == 1
        assert "test_asset" in metrics.errors[0]

    def test_add_metrics(self):
        """Test adding pre-collected metrics."""
        collector = HealthMetricsCollector()
        
        metrics = ExecutionMetrics(
            hotel_id="hotel_3",
            hotel_name="Hotel Tres",
            timestamp=datetime.now(),
            assets_generated=5,
            assets_failed=1,
            success_rate=0.833,
            avg_confidence=0.75,
            execution_time=10.5,
            errors=[],
            warnings=["Minor warning"]
        )
        
        collector.add_metrics(metrics)
        
        assert len(collector.get_all_metrics()) == 1
        retrieved = collector.get_all_metrics()[0]
        assert retrieved.hotel_id == "hotel_3"
        assert retrieved.assets_generated == 5

    def test_get_summary_empty(self):
        """Test summary with no metrics."""
        collector = HealthMetricsCollector()
        
        summary = collector.get_summary()
        
        assert summary["total_executions"] == 0
        assert summary["total_assets_generated"] == 0
        assert summary["overall_success_rate"] == 0.0

    def test_get_summary_with_metrics(self):
        """Test summary calculation with multiple executions."""
        collector = HealthMetricsCollector()
        
        metrics1 = ExecutionMetrics(
            hotel_id="h1", hotel_name="Hotel 1", timestamp=datetime.now(),
            assets_generated=10, assets_failed=2, success_rate=0.833,
            avg_confidence=0.80, execution_time=5.0
        )
        metrics2 = ExecutionMetrics(
            hotel_id="h2", hotel_name="Hotel 2", timestamp=datetime.now(),
            assets_generated=8, assets_failed=0, success_rate=1.0,
            avg_confidence=0.90, execution_time=3.0
        )
        
        collector.add_metrics(metrics1)
        collector.add_metrics(metrics2)
        
        summary = collector.get_summary()
        
        assert summary["total_executions"] == 2
        assert summary["total_assets_generated"] == 18
        assert summary["total_assets_failed"] == 2
        assert summary["overall_success_rate"] == pytest.approx(0.9)
        assert summary["avg_confidence"] == pytest.approx(0.85)
        assert summary["avg_execution_time"] == pytest.approx(4.0)
        assert summary["unique_hotels"] == 2

    def test_clear(self):
        """Test clearing all metrics."""
        collector = HealthMetricsCollector()
        collector.start_execution("hotel_x", "Hotel X")
        collector.end_execution()
        
        assert len(collector.get_all_metrics()) == 1
        
        collector.clear()
        
        assert len(collector.get_all_metrics()) == 0
        assert collector._current_execution_start is None


class TestHealthDashboardGenerator:
    """Test suite for HealthDashboardGenerator."""

    def test_dashboard_generator_initialization(self):
        """Test generator initializes correctly."""
        generator = HealthDashboardGenerator()
        
        assert generator._chart_colors["success"] == "#10b981"
        assert generator._chart_colors["error"] == "#ef4444"

    def test_generate_html_with_empty_metrics(self):
        """Test HTML generation with no data."""
        generator = HealthDashboardGenerator()
        
        html = generator.generate_html([])
        
        assert "No Data Available" in html
        assert "<html" in html

    def test_generate_html_with_metrics(self):
        """Test HTML generation with sample metrics."""
        generator = HealthDashboardGenerator()
        
        metrics = [
            ExecutionMetrics(
                hotel_id="h1", hotel_name="Hotel Uno", timestamp=datetime.now(),
                assets_generated=10, assets_failed=2, success_rate=0.833,
                avg_confidence=0.85, execution_time=5.5, errors=[], warnings=[]
            ),
            ExecutionMetrics(
                hotel_id="h2", hotel_name="Hotel Dos", timestamp=datetime.now(),
                assets_generated=8, assets_failed=0, success_rate=1.0,
                avg_confidence=0.92, execution_time=3.2, errors=[], warnings=[]
            ),
        ]
        
        html = generator.generate_html(metrics)
        
        assert "Hotel Uno" in html
        assert "Hotel Dos" in html
        assert "Chart.js" in html
        assert "successChart" in html
        assert "confidenceChart" in html
        assert "83.3%" in html or "83%" in html  # Success rate formatting

    def test_generate_json_summary(self):
        """Test JSON summary generation."""
        generator = HealthDashboardGenerator()
        
        metrics = [
            ExecutionMetrics(
                hotel_id="h1", hotel_name="Hotel One", timestamp=datetime.now(),
                assets_generated=10, assets_failed=2, success_rate=0.833,
                avg_confidence=0.85, execution_time=5.5, errors=["Error 1"], warnings=["Warning 1"]
            ),
        ]
        
        summary = generator.generate_json_summary(metrics)
        
        assert summary["total_executions"] == 1
        assert summary["total_assets_generated"] == 10
        assert summary["total_assets_failed"] == 2
        assert summary["overall_success_rate"] == pytest.approx(83.3, rel=1)
        assert summary["avg_confidence"] == pytest.approx(85.0, rel=1)
        assert summary["unique_hotels"] == 1
        assert summary["total_errors"] == 1
        assert summary["total_warnings"] == 1

    def test_confidence_distribution(self):
        """Test confidence bucket calculation."""
        generator = HealthDashboardGenerator()
        
        metrics = [
            ExecutionMetrics(
                hotel_id="h1", hotel_name="H1", timestamp=datetime.now(),
                assets_generated=5, assets_failed=0, success_rate=1.0,
                avg_confidence=0.95, execution_time=1.0
            ),
            ExecutionMetrics(
                hotel_id="h2", hotel_name="H2", timestamp=datetime.now(),
                assets_generated=5, assets_failed=0, success_rate=1.0,
                avg_confidence=0.75, execution_time=1.0
            ),
            ExecutionMetrics(
                hotel_id="h3", hotel_name="H3", timestamp=datetime.now(),
                assets_generated=5, assets_failed=0, success_rate=1.0,
                avg_confidence=0.60, execution_time=1.0
            ),
            ExecutionMetrics(
                hotel_id="h4", hotel_name="H4", timestamp=datetime.now(),
                assets_generated=5, assets_failed=0, success_rate=1.0,
                avg_confidence=0.40, execution_time=1.0
            ),
        ]
        
        summary = generator.generate_json_summary(metrics)
        dist = summary["confidence_distribution"]
        
        assert dist["0.9+"] == 1
        assert dist["0.7-0.9"] == 1
        assert dist["0.5-0.7"] == 1
        assert dist["<0.5"] == 1

    def test_save_dashboard(self, tmp_path):
        """Test saving dashboard to files."""
        generator = HealthDashboardGenerator()
        
        metrics = [
            ExecutionMetrics(
                hotel_id="test_hotel", hotel_name="Test Hotel", timestamp=datetime.now(),
                assets_generated=8, assets_failed=1, success_rate=0.889,
                avg_confidence=0.82, execution_time=4.5, errors=[], warnings=[]
            ),
        ]
        
        output_path = tmp_path / "health_dashboard.html"
        result = generator.save_dashboard(metrics, str(output_path))
        
        assert "html" in result
        assert Path(result["html"]).exists()
        assert "json" in result
        assert Path(result["json"]).exists()
        
        # Verify HTML content
        html_content = Path(result["html"]).read_text(encoding='utf-8')
        assert "Test Hotel" in html_content


class TestDashboardIntegration:
    """Integration tests for dashboard with collector."""

    def test_full_workflow(self):
        """Test complete metrics collection and dashboard generation workflow."""
        collector = HealthMetricsCollector()
        generator = HealthDashboardGenerator()
        
        # Execute multiple hotels
        hotels = [
            ("hotel_a", "Hotel Alpha", 10, 0, 0.90, 5.0),
            ("hotel_b", "Hotel Beta", 8, 2, 0.75, 7.5),
            ("hotel_c", "Hotel Gamma", 5, 5, 0.50, 10.0),
        ]
        
        for hotel_id, name, generated, failed, conf, exec_time in hotels:
            collector.start_execution(hotel_id, name)
            
            mock_result = MagicMock()
            mock_result.generated_assets = [MagicMock(confidence_score=conf) for _ in range(generated)]
            mock_result.failed_assets = [MagicMock() for _ in range(failed)]
            
            collector.collect_from_result(mock_result)
        
        # Generate dashboard
        all_metrics = collector.get_all_metrics()
        html = generator.generate_html(all_metrics)
        summary = generator.generate_json_summary(all_metrics)
        
        # Verify results
        assert len(all_metrics) == 3
        assert summary["total_executions"] == 3
        assert summary["total_assets_generated"] == 23
        assert summary["total_assets_failed"] == 7
        assert summary["unique_hotels"] == 3
        assert "Hotel Alpha" in html
        assert "Hotel Beta" in html
        assert "Hotel Gamma" in html
