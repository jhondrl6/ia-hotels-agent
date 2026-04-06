"""Dashboard de Calidad - Métricas y Tendencias.

Este módulo implementa el dashboard de calidad que:
- Registra métricas de cada corrida
- Muestra tendencias históricas
- Genera alertas de degradación
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from enum import Enum
from pathlib import Path
import json


class AlertSeverity(Enum):
    """Severidad de las alertas de calidad."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AlertType(Enum):
    """Tipos de alertas detectables."""
    COHERENCE_LOW = "coherence_low"
    EVIDENCE_COVERAGE_LOW = "evidence_coverage_low"
    HARD_CONTRADICTIONS = "hard_contradictions"
    FINANCIAL_INVALID = "financial_invalid"
    CRITICAL_RECALL_LOW = "critical_recall_low"
    DEGRADATION_TREND = "degradation_trend"


@dataclass
class Alert:
    """Alerta de calidad detectada."""
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    metric_name: str
    current_value: Any
    threshold: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    run_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "threshold": self.threshold,
            "timestamp": self.timestamp.isoformat(),
            "run_id": self.run_id
        }


@dataclass
class RunMetrics:
    """Métricas de una corrida de análisis."""
    run_id: str
    hotel_id: str
    evidence_coverage: float
    hard_contradictions: int
    soft_contradictions: int
    financial_validity: bool
    critical_recall: float
    coherence_score: float
    publication_status: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    url: Optional[str] = None
    gate_results: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp.isoformat(),
            "hotel_id": self.hotel_id,
            "url": self.url,
            "evidence_coverage": self.evidence_coverage,
            "hard_contradictions": self.hard_contradictions,
            "soft_contradictions": self.soft_contradictions,
            "financial_validity": self.financial_validity,
            "critical_recall": self.critical_recall,
            "coherence_score": self.coherence_score,
            "publication_status": self.publication_status,
            "gate_results": self.gate_results
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunMetrics":
        return cls(
            run_id=data["run_id"],
            hotel_id=data["hotel_id"],
            evidence_coverage=data["evidence_coverage"],
            hard_contradictions=data["hard_contradictions"],
            soft_contradictions=data.get("soft_contradictions", 0),
            financial_validity=data["financial_validity"],
            critical_recall=data["critical_recall"],
            coherence_score=data["coherence_score"],
            publication_status=data["publication_status"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            url=data.get("url"),
            gate_results=data.get("gate_results", {})
        )


@dataclass
class TrendReport:
    """Reporte de tendencias de calidad."""
    period_days: int
    total_runs: int
    avg_coherence: float
    avg_evidence_coverage: float
    coherence_trend: str
    evidence_trend: str
    alert_count: int
    degradation_events: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "period_days": self.period_days,
            "total_runs": self.total_runs,
            "avg_coherence": self.avg_coherence,
            "avg_evidence_coverage": self.avg_evidence_coverage,
            "coherence_trend": self.coherence_trend,
            "evidence_trend": self.evidence_trend,
            "alert_count": self.alert_count,
            "degradation_events": self.degradation_events
        }



class QualityDashboard:
    """Dashboard de calidad para monitoreo de métricas."""
    
    DEFAULT_COHERENCE_THRESHOLD = 0.8
    DEFAULT_EVIDENCE_THRESHOLD = 0.95
    DEFAULT_RECALL_THRESHOLD = 0.90
    
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path is None:
            storage_path = ".observability/runs.jsonl"
        
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._runs: List[RunMetrics] = []
        self._load_runs()
    
    def _load_runs(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            self._runs.append(RunMetrics.from_dict(data))
                        except (json.JSONDecodeError, KeyError):
                            continue
        except Exception:
            pass
    
    def _save_run(self, metrics: RunMetrics) -> None:
        with open(self.storage_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(metrics.to_dict(), ensure_ascii=False) + chr(10))
    
    def record_run(self, metrics: RunMetrics) -> None:
        self._runs.append(metrics)
        self._save_run(metrics)
    
    def get_latest_run(self, hotel_id: Optional[str] = None) -> Optional[RunMetrics]:
        runs = self._runs
        if hotel_id:
            runs = [r for r in runs if r.hotel_id == hotel_id]
        if not runs:
            return None
        return max(runs, key=lambda r: r.timestamp)
    
    def get_runs(self, hotel_id: Optional[str] = None, days: Optional[int] = None) -> List[RunMetrics]:
        runs = self._runs
        if hotel_id:
            runs = [r for r in runs if r.hotel_id == hotel_id]
        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            runs = [r for r in runs if r.timestamp >= cutoff]
        return sorted(runs, key=lambda r: r.timestamp)

    
    def check_alerts(self, hotel_id: Optional[str] = None, run_id: Optional[str] = None) -> List[Alert]:
        alerts = []
        if run_id:
            run = next((r for r in self._runs if r.run_id == run_id), None)
        elif hotel_id:
            run = self.get_latest_run(hotel_id)
        else:
            run = self.get_latest_run()
        
        if not run:
            return alerts
        
        if run.coherence_score < self.DEFAULT_COHERENCE_THRESHOLD:
            sev = AlertSeverity.CRITICAL if run.coherence_score < 0.5 else AlertSeverity.WARNING
            alerts.append(Alert(
                alert_type=AlertType.COHERENCE_LOW,
                severity=sev,
                message=f"Coherence score bajo: {run.coherence_score:.2f}",
                metric_name="coherence_score",
                current_value=run.coherence_score,
                threshold=self.DEFAULT_COHERENCE_THRESHOLD,
                run_id=run.run_id
            ))
        
        if run.evidence_coverage < self.DEFAULT_EVIDENCE_THRESHOLD:
            alerts.append(Alert(
                alert_type=AlertType.EVIDENCE_COVERAGE_LOW,
                severity=AlertSeverity.WARNING,
                message=f"Evidence coverage bajo: {run.evidence_coverage:.1%}",
                metric_name="evidence_coverage",
                current_value=run.evidence_coverage,
                threshold=self.DEFAULT_EVIDENCE_THRESHOLD,
                run_id=run.run_id
            ))
        
        if run.hard_contradictions > 0:
            alerts.append(Alert(
                alert_type=AlertType.HARD_CONTRADICTIONS,
                severity=AlertSeverity.CRITICAL,
                message=f"Hay {run.hard_contradictions} contradiccion(es) dura(s)",
                metric_name="hard_contradictions",
                current_value=run.hard_contradictions,
                threshold=0,
                run_id=run.run_id
            ))
        
        if not run.financial_validity:
            alerts.append(Alert(
                alert_type=AlertType.FINANCIAL_INVALID,
                severity=AlertSeverity.CRITICAL,
                message="Datos financieros invalidos",
                metric_name="financial_validity",
                current_value=run.financial_validity,
                threshold=True,
                run_id=run.run_id
            ))
        
        if run.critical_recall < self.DEFAULT_RECALL_THRESHOLD:
            alerts.append(Alert(
                alert_type=AlertType.CRITICAL_RECALL_LOW,
                severity=AlertSeverity.WARNING,
                message=f"Critical recall bajo: {run.critical_recall:.1%}",
                metric_name="critical_recall",
                current_value=run.critical_recall,
                threshold=self.DEFAULT_RECALL_THRESHOLD,
                run_id=run.run_id
            ))
        
        return alerts

    
    def get_trends(self, days: int = 30, hotel_id: Optional[str] = None) -> TrendReport:
        runs = self.get_runs(days=days, hotel_id=hotel_id)
        
        if not runs:
            return TrendReport(
                period_days=days, total_runs=0, avg_coherence=0.0,
                avg_evidence_coverage=0.0, coherence_trend="stable",
                evidence_trend="stable", alert_count=0, degradation_events=[]
            )
        
        avg_coherence = sum(r.coherence_score for r in runs) / len(runs)
        avg_evidence = sum(r.evidence_coverage for r in runs) / len(runs)
        
        mid = len(runs) // 2
        if mid > 0:
            first_coh = sum(r.coherence_score for r in runs[:mid]) / mid
            second_coh = sum(r.coherence_score for r in runs[mid:]) / (len(runs) - mid)
            first_ev = sum(r.evidence_coverage for r in runs[:mid]) / mid
            second_ev = sum(r.evidence_coverage for r in runs[mid:]) / (len(runs) - mid)
            
            coh_diff = second_coh - first_coh
            ev_diff = second_ev - first_ev
            
            coh_trend = "up" if coh_diff > 0.05 else ("down" if coh_diff < -0.05 else "stable")
            ev_trend = "up" if ev_diff > 0.05 else ("down" if ev_diff < -0.05 else "stable")
        else:
            coh_trend = "stable"
            ev_trend = "stable"
        
        alert_count = 0
        degradation_events = []
        
        for i, run in enumerate(runs):
            alerts = self.check_alerts(run_id=run.run_id)
            alert_count += len(alerts)
            if i > 0:
                prev = runs[i-1]
                if run.coherence_score < prev.coherence_score - 0.1:
                    degradation_events.append({
                        "run_id": run.run_id,
                        "timestamp": run.timestamp.isoformat(),
                        "metric": "coherence",
                        "previous": prev.coherence_score,
                        "current": run.coherence_score
                    })
        
        return TrendReport(
            period_days=days, total_runs=len(runs), avg_coherence=avg_coherence,
            avg_evidence_coverage=avg_evidence, coherence_trend=coh_trend,
            evidence_trend=ev_trend, alert_count=alert_count,
            degradation_events=degradation_events
        )

    
    def generate_report(self, run_id: Optional[str] = None, hotel_id: Optional[str] = None) -> str:
        if run_id:
            run = next((r for r in self._runs if r.run_id == run_id), None)
        else:
            run = self.get_latest_run(hotel_id)
        
        if not run:
            return "No hay datos disponibles."
        
        alerts = self.check_alerts(run_id=run.run_id)
        trends = self.get_trends(days=7, hotel_id=hotel_id)
        
        lines = [
            "# Reporte de Calidad - IA Hoteles",
            f"Hotel: {run.hotel_id}",
            f"Corrida: {run.run_id}",
            f"Fecha: {run.timestamp.strftime("%Y-%m-%d %H:%M UTC")}",
            "",
            "## Métricas de Calidad",
            f"Coherence Score: {run.coherence_score:.2f} (umbral: {self.DEFAULT_COHERENCE_THRESHOLD})",
            f"Evidence Coverage: {run.evidence_coverage:.1%} (umbral: {self.DEFAULT_EVIDENCE_THRESHOLD:.0%})",
            f"Hard Contradictions: {run.hard_contradictions}",
            f"Financial Validity: {"Valido" if run.financial_validity else "Invalido"}",
            f"Critical Recall: {run.critical_recall:.1%}",
            f"Estado de Publicacion: {run.publication_status}",
            "",
            "## Alertas",
        ]
        
        if alerts:
            for alert in alerts:
                lines.append(f"- [{alert.severity.value}] {alert.message}")
        else:
            lines.append("No hay alertas.")
        
        lines.extend([
            "",
            "## Tendencias (ultimos 7 dias)",
            f"Corridas: {trends.total_runs}",
            f"Coherencia promedio: {trends.avg_coherence:.2f} ({trends.coherence_trend})",
            f"Evidence promedio: {trends.avg_evidence_coverage:.1%} ({trends.evidence_trend})",
            f"Eventos de degradacion: {len(trends.degradation_events)}"
        ])
        
        return chr(10).join(lines)


def create_metrics_from_assessment(assessment, gate_results=None, run_id=None):
    """Crea RunMetrics desde un assessment."""
    import uuid
    if run_id is None:
        run_id = f"run-{uuid.uuid4().hex[:8]}"
    
    if hasattr(assessment, "url"):
        return RunMetrics(
            run_id=run_id,
            hotel_id=assessment.url.replace("https://", "").replace("http://", "").replace("/", "_"),
            url=assessment.url,
            evidence_coverage=getattr(assessment, "evidence_coverage", 0.0),
            hard_contradictions=getattr(assessment, "hard_contradictions", 0),
            soft_contradictions=getattr(assessment, "soft_contradictions", 0),
            financial_validity=True,
            critical_recall=getattr(assessment, "critical_recall", 0.0),
            coherence_score=getattr(assessment, "coherence_score", 0.0),
            publication_status=getattr(assessment, "publication_status", "DRAFT_INTERNAL"),
            gate_results={g.gate_name: g.passed for g in gate_results} if gate_results else {}
        )
    else:
        return RunMetrics(
            run_id=run_id,
            hotel_id=assessment.get("url", "unknown").replace("https://", "").replace("/", "_"),
            url=assessment.get("url"),
            evidence_coverage=assessment.get("evidence_coverage", 0.0),
            hard_contradictions=assessment.get("hard_contradictions", 0),
            soft_contradictions=assessment.get("soft_contradictions", 0),
            financial_validity=assessment.get("financial_validity", True),
            critical_recall=assessment.get("critical_recall", 0.0),
            coherence_score=assessment.get("coherence_score", 0.0),
            publication_status=assessment.get("publication_status", "DRAFT_INTERNAL"),
            gate_results={g.gate_name: g.passed for g in gate_results} if gate_results else {}
        )
