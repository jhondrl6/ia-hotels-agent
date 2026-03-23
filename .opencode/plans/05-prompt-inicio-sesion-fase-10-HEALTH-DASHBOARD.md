# FASE 10: Health Dashboard - System Health Monitor

**ID**: FASE-10-HEALTH-DASHBOARD
**Objetivo**: Implementar dashboard unificado de métricas de salud del sistema
**Dependencias**: FASE 7 completada
**Duración estimada**: 1-2 horas
**Skill**: reporting, metrics, dashboard

---

## Problema Actual

```
No hay visibility del estado del sistema:
- Cuántos assets se generan por hotel
- Success rate
- Confidence promedio
- Tiempo de ejecución
- Errors/warnings
```

---

## Solución: Health Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│              IA HOTELES - SYSTEM HEALTH DASHBOARD           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    156      │  │    89%      │  │   0.72      │        │
│  │  Hotels     │  │  Success    │  │  Avg Conf   │        │
│  │  Analyzed   │  │  Rate       │  │  Score      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│  ┌─────────────────────────────────────────────┐            │
│  │          Confidence Distribution             │            │
│  │  ██████████████████░░░░ 0.9+ (65)          │            │
│  │  ████████████░░░░░░░░░░░ 0.7-0.9 (45)       │            │
│  │  ██████░░░░░░░░░░░░░░░░ 0.5-0.7 (30)       │            │
│  │  ████░░░░░░░░░░░░░░░░░░ <0.5 (16)          │            │
│  └─────────────────────────────────────────────┘            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Tareas

### T10A: HealthMetricsCollector
**Archivo**: `modules/monitoring/health_metrics_collector.py` (NUEVO)

```python
@dataclass
class ExecutionMetrics:
    hotel_id: str
    timestamp: datetime
    assets_generated: int
    assets_failed: int
    success_rate: float
    avg_confidence: float
    execution_time: float
    errors: List[str]
    warnings: List[str]
```

### T10B: HealthDashboardGenerator
**Archivo**: `modules/monitoring/health_dashboard_generator.py` (NUEVO)

```python
class HealthDashboardGenerator:
    def generate_html(metrics: List[ExecutionMetrics]) -> str:
        """Genera dashboard HTML con Chart.js"""
    
    def generate_json_summary(metrics: List[ExecutionMetrics]) -> dict:
        """Genera summary para integración"""
```

### T10C: Integrar en Orchestration
**Archivo**: `modules/orchestration_v4/` (modificar)

```python
# En post_execution()
metrics = collector.collect()
dashboard = generator.generate_html(all_metrics)
save("output/health_dashboard.html", dashboard)
```

---

## Tests Obligatorios

| Test | Criterio |
|------|----------|
| `test_metrics_collector` | Métricas se recolectan correctamente |
| `test_dashboard_html_generated` | HTML con gráficos se genera |
| `test_dashboard_integrated` | Dashboard disponible post-ejecución |

---

## Criterios de Completitud

- [ ] HealthMetricsCollector implementado
- [ ] Dashboard HTML genera con Chart.js
- [ ] Dashboard se genera después de cada ejecución
- [ ] Tests pasan
