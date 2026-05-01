# Dependencias y Análisis de Fases — FEATURE-CONFIG-EXTRACTION

**Plan:** FEATURE-CONFIG-EXTRACTION v1.1.0 (revisado 2026-04-29 17:00)
**Workflow:** phased_project_executor.md v2.9.0
**Target:** v4.38.0

---

## 1. Diagrama de Dependencias

```
TECHNICAL_DEBT_2026-04-29.md (fuente, revisado v3)
           │
           ├── FASE-CONFIG-1 (sync fix) ──── independiente
           │
           ├── FASE-CONFIG-2 (fallbacks) ──── post-CONFIG-1
           │
           ├── FASE-CONFIG-3A (pricing) ──── independiente (nuevo YAML)
           │      │
           │      └── FASE-CONFIG-3B (scenarios) ──── post-3A
           │             │
           │             ├── FASE-CONFIG-4 (template) ──── post-3B
           │             ├── FASE-CONFIG-5 (umbrales) ──── post-3B (paralelo con 4)
           │             │
           │             └── FASE-CONFIG-6 (config + deprecación) ──── post-3B/4/5
           │                    │
           │                    └── FASE-CONFIG-7 (v4complete) ──── post-TODAS
           │                           │
           │                           └── FASE-CONFIG-8 (regression) ── post-7
           │                                  │
           │                                  └── FASE-RELEASE-4.38.0 ──── post-TODAS
```

---

## 2. Evaluación R3 por Fase

### FASE-CONFIG-1 a 5: Sin cambios (ver versión anterior)

### FASE-CONFIG-6: Config Reconnect + Deprecación Módulos Huérfanos

```
TAREAS DE LA FASE:
  [x] Auditar settings.yaml vs YAML nuevos + identificar TODOS los módulos huérfanos
  [x] Reconectar settings.yaml + Deprecar 4 módulos huérfanos con DeprecationWarning
  [x] Corregir bugs colaterales: AnalyticsStatus.is_any_missing(), __init__.py cleanup
  [x] Tests: config reconnect + deprecation warnings + AnalyticsStatus corregido

CONTADOR:
  - 4 tareas
  - 0 comandos largos
  - Total: 4 tareas + 0 largos → ✓ PASA (máx 4+0)
```

**Iteration Budget:**
- Fixed costs: ~28 iteraciones
- Phase work: ~17 iteraciones (auditar + settings cleanup + 4 módulos + AnalyticsStatus + tests)
- **Total estimado: 45 iteraciones** (de 60 disponibles)

### FASE-CONFIG-7 a RELEASE: Sin cambios (ver versión anterior)

---

## 3. Tabla de Conflictos de Archivos (Actualizada)

| Archivo | Fases que lo modifican | Tipo de conflicto | Mitigación |
|---------|----------------------|-------------------|------------|
| `v4_proposal_generator.py` | CONFIG-2, CONFIG-3B, CONFIG-4 | Secuencial | Orden: 2 → 3B → 4 |
| `v4_diagnostic_generator.py` | CONFIG-2, CONFIG-5, CONFIG-6 | Secuencial | Orden: 2 → 5 → 6 |
| `modules/analytics/__init__.py` | CONFIG-6 | Sin conflicto | — |
| `data_models/analytics_status.py` | CONFIG-6 | Sin conflicto | — |
| `config/settings.yaml` | CONFIG-6 | Sin conflicto | — |

---

## 4. Cobertura de Hallazgos (Actualizada v1.1.0)

### Causas Raíz

| CR | Descripción | Fase |
|----|-------------|------|
| CR-1 | Doble escape YAML sync_config.yaml | CONFIG-1 |
| CR-2 | Ausencia validación post-reemplazo | CONFIG-1 |
| CR-3 | Fallbacks silenciosos | CONFIG-2 |
| CR-4 | Parámetros financieros hardcodeados | CONFIG-3A, 3B |
| CR-5 | Duplicación garantías | CONFIG-4 |
| CR-6 | Disconnect config/code | CONFIG-6 |
| CR-7 | Narrativas de impacto | CONFIG-5 |

### Hallazgo H6 (NUEVO)

| ID | Descripción | Fase | Severidad |
|----|-------------|------|-----------|
| H6 | 4 módulos huérfanos en analytics/ (847 líneas) + AnalyticsStatus.is_any_missing() bug | CONFIG-6 | 🟡 MEDIUM |

### Severidad Corregida (API Stubs)

| Stub | Original | Corregida | Cubierto por |
|------|----------|-----------|-------------|
| ProfoundClient (3 métodos) | 🔴 HIGH | 🟢 LOW | Sin alternativa, pero no alimenta scores |
| SemrushClient (3 métodos) | 🔴 HIGH | 🟢 LOW | GoogleSearchConsoleClient + GA4 + PageSpeed |
| data_aggregator.py | N/A | 🟢 LOW | Código muerto — deprecar |
| aeo_metrics_gen.py | N/A | 🟢 LOW | Código muerto — deprecar |

---

## 5. Presupuesto Total Estimado (Sin cambios)

10 sesiones, ~440 iteraciones totales, 6 YAML nuevos, 8 archivos Python modificados, 59+ tests.
