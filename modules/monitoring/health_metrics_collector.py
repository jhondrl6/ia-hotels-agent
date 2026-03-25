"""
HealthMetricsCollector - System health metrics collection for IA Hoteles Agent.

Collects execution metrics per hotel including:
- Assets generated/failed
- Success rate
- Average confidence
- Execution time
- Errors and warnings

Created as part of FASE-10-HEALTH-DASHBOARD.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class ExecutionMetrics:
    """
    Metrics collected during a single hotel execution.
    
    Attributes:
        hotel_id: Unique identifier for the hotel
        hotel_name: Human-readable hotel name
        timestamp: When the execution occurred
        assets_generated: Number of successfully generated assets
        assets_failed: Number of failed asset generations
        success_rate: Percentage of successful asset generations (0.0-1.0)
        avg_confidence: Average confidence score across all assets (0.0-1.0)
        execution_time: Total execution time in seconds
        errors: List of error messages encountered
        warnings: List of warning messages encountered
    """
    hotel_id: str
    hotel_name: str
    timestamp: datetime
    assets_generated: int = 0
    assets_failed: int = 0
    success_rate: float = 0.0
    avg_confidence: float = 0.0
    execution_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for JSON serialization."""
        return {
            "hotel_id": self.hotel_id,
            "hotel_name": self.hotel_name,
            "timestamp": self.timestamp.isoformat(),
            "assets_generated": self.assets_generated,
            "assets_failed": self.assets_failed,
            "success_rate": round(self.success_rate, 4),
            "avg_confidence": round(self.avg_confidence, 4),
            "execution_time": round(self.execution_time, 2),
            "errors": self.errors,
            "warnings": self.warnings,
        }


class HealthMetricsCollector:
    """
    Collects and aggregates health metrics across multiple hotel executions.
    
    Usage:
        collector = HealthMetricsCollector()
        
        # After each hotel execution:
        metrics = collector.collect_from_result(result)
        collector.add_metrics(metrics)
        
        # After all executions:
        all_metrics = collector.get_all_metrics()
        summary = collector.get_summary()
    """
    
    def __init__(self):
        """Initialize the metrics collector."""
        self._metrics: List[ExecutionMetrics] = []
        self._current_execution_start: Optional[float] = None
        self._current_hotel_id: Optional[str] = None
        self._current_hotel_name: Optional[str] = None
    
    def start_execution(self, hotel_id: str, hotel_name: str) -> None:
        """
        Mark the start of a hotel execution.
        
        Args:
            hotel_id: Unique hotel identifier
            hotel_name: Human-readable hotel name
        """
        import time
        self._current_execution_start = time.time()
        self._current_hotel_id = hotel_id
        self._current_hotel_name = hotel_name
    
    def end_execution(self) -> Optional[ExecutionMetrics]:
        """
        Mark the end of a hotel execution and collect metrics.
        
        Returns:
            ExecutionMetrics for the completed execution, or None if no execution was started.
        """
        import time
        
        if self._current_execution_start is None:
            return None
        
        execution_time = time.time() - self._current_execution_start
        
        metrics = ExecutionMetrics(
            hotel_id=self._current_hotel_id or "unknown",
            hotel_name=self._current_hotel_name or "Unknown Hotel",
            timestamp=datetime.now(),
            execution_time=execution_time,
        )
        
        self._metrics.append(metrics)
        
        # Reset state
        self._current_execution_start = None
        self._current_hotel_id = None
        self._current_hotel_name = None
        
        return metrics
    
    def collect_from_result(
        self,
        result: Any,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None
    ) -> ExecutionMetrics:
        """
        Collect metrics from an AssetGenerationResult.
        
        Args:
            result: AssetGenerationResult from V4AssetOrchestrator
            errors: Optional list of additional error messages
            warnings: Optional list of additional warning messages
            
        Returns:
            ExecutionMetrics populated from the result
        """
        import time
        
        # Calculate execution time if we have a start time
        execution_time = 0.0
        if self._current_execution_start:
            execution_time = time.time() - self._current_execution_start
        
        errors = errors or []
        warnings = warnings or []
        
        # Extract asset counts from result
        if hasattr(result, 'generated_assets'):
            assets_generated = len(result.generated_assets)
            assets_failed = len(result.failed_assets)
        elif isinstance(result, dict):
            assets_generated = result.get('generated', 0)
            assets_failed = result.get('failed', 0)
        else:
            assets_generated = 0
            assets_failed = 0
        
        # Calculate success rate
        total_assets = assets_generated + assets_failed
        success_rate = assets_generated / total_assets if total_assets > 0 else 0.0
        
        # Calculate average confidence from generated assets
        avg_confidence = 0.0
        if hasattr(result, 'generated_assets') and result.generated_assets:
            confidences = [a.confidence_score for a in result.generated_assets if hasattr(a, 'confidence_score')]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        elif isinstance(result, dict) and 'generated_assets' in result:
            gen_assets = result.get('generated_assets', [])
            if gen_assets:
                confidences = [a.get('confidence_score', 0.0) for a in gen_assets if isinstance(a, dict)]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Add errors from failed assets
        if hasattr(result, 'failed_assets'):
            for failed in result.failed_assets:
                if hasattr(failed, 'reason') and failed.reason:
                    errors.append(f"Asset failure ({failed.asset_type}): {failed.reason}")
        elif isinstance(result, dict) and 'failed_assets' in result:
            for failed in result.get('failed_assets', []):
                if isinstance(failed, dict) and failed.get('reason'):
                    errors.append(f"Asset failure ({failed.get('asset_type', 'unknown')}): {failed.get('reason')}")
        
        metrics = ExecutionMetrics(
            hotel_id=self._current_hotel_id or getattr(result, 'hotel_id', 'unknown'),
            hotel_name=self._current_hotel_name or getattr(result, 'hotel_name', 'Unknown Hotel'),
            timestamp=datetime.now(),
            assets_generated=assets_generated,
            assets_failed=assets_failed,
            success_rate=success_rate,
            avg_confidence=avg_confidence,
            execution_time=execution_time,
            errors=errors,
            warnings=warnings,
        )
        
        self._metrics.append(metrics)
        return metrics
    
    def add_metrics(self, metrics: ExecutionMetrics) -> None:
        """
        Add pre-collected metrics to the collector.
        
        Args:
            metrics: ExecutionMetrics to add
        """
        self._metrics.append(metrics)
    
    def get_all_metrics(self) -> List[ExecutionMetrics]:
        """
        Get all collected metrics.
        
        Returns:
            List of all ExecutionMetrics collected
        """
        return list(self._metrics)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get aggregate summary statistics across all executions.
        
        Returns:
            Dictionary with summary statistics
        """
        if not self._metrics:
            return {
                "total_executions": 0,
                "total_assets_generated": 0,
                "total_assets_failed": 0,
                "overall_success_rate": 0.0,
                "avg_confidence": 0.0,
                "avg_execution_time": 0.0,
                "total_execution_time": 0.0,
                "unique_hotels": 0,
            }
        
        total_assets_gen = sum(m.assets_generated for m in self._metrics)
        total_assets_fail = sum(m.assets_failed for m in self._metrics)
        total_assets = total_assets_gen + total_assets_fail
        
        all_confidences = [m.avg_confidence for m in self._metrics if m.avg_confidence > 0]
        all_times = [m.execution_time for m in self._metrics]
        
        summary = {
            "total_executions": len(self._metrics),
            "total_assets_generated": total_assets_gen,
            "total_assets_failed": total_assets_fail,
            "overall_success_rate": round(total_assets_gen / total_assets, 4) if total_assets > 0 else 0.0,
            "avg_confidence": round(sum(all_confidences) / len(all_confidences), 4) if all_confidences else 0.0,
            "avg_execution_time": round(sum(all_times) / len(all_times), 2) if all_times else 0.0,
            "total_execution_time": round(sum(all_times), 2),
            "unique_hotels": len(set(m.hotel_id for m in self._metrics)),
        }
        
        return summary
    
    def clear(self) -> None:
        """Clear all collected metrics."""
        self._metrics.clear()
        self._current_execution_start = None
        self._current_hotel_id = None
        self._current_hotel_name = None


# Global collector instance for easy access
_global_collector: Optional[HealthMetricsCollector] = None


def get_global_collector() -> HealthMetricsCollector:
    """Get or create the global metrics collector instance."""
    global _global_collector
    if _global_collector is None:
        _global_collector = HealthMetricsCollector()
    return _global_collector
