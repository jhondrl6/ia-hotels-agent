# Plan Maestro: FEATURE-CONFIG-EXTRACTION

**Versión del plan:** 1.1.0 (revisado 2026-04-29 17:00)
**Creado:** 2026-04-29 16:45
**Fuente:** `.opencode/context/TECHNICAL_DEBT_2026-04-29.md` (Validación Forense v2 + revisión severidad H4)
**Workflow:** `.agents/workflows/phased_project_executor.md` v2.9.0
**Versión target:** 4.38.0

---

## Objetivo

Corregir el bug de sync_versions + migrar 31 hardcodes a archivos YAML con schema validado + deprecar 4 módulos huérfanos + ejecutar v4complete de validación en Amazilia Hotel.

## Alcance

- **7 Causas Raíz** (CR-1 a CR-7)
- **31 Hardcodes** (19 originales confirmados + 12 nuevos descubiertos N-01 a N-12)
- **1 Bug activo**: sync_versions.py reporta falsos positivos
- **1 Disconnect**: settings.yaml no leído por generadores
- **NUEVO H6**: 4 módulos huérfanos en analytics/ (847 líneas de código muerto)
- **NUEVO**: AnalyticsStatus.is_any_missing() siempre True por stubs no inicializados

## Corrección de Severidad (vs TECHNICAL_DEBT original)

| Hallazgo | Severidad Original | Severidad Corregida | Motivo |
|----------|-------------------|---------------------|--------|
| 6 API stubs (Profound/Semrush) | 🔴 HIGH | 🟢 LOW | 3/6 funciones YA cubiertas por GSC + GA4 + PageSpeed (gratuitos). Los 3 de Profound no alimentan scores. |
| Módulos huérfanos (data_aggregator, aeo_metrics_gen) | No catalogado | 🟢 LOW | 558 líneas de código muerto. Deprecar para evitar confusión. |
| AnalyticsStatus.is_any_missing() bug | No catalogado | 🟡 MEDIUM | Siempre True → transparencia aparece innecesariamente. |

## Estructura de Fases (10 fases, 10 sesiones)

| # | Fase | Scope | Tareas | Cmd Largo | R3 |
|---|------|-------|--------|-----------|-----|
| 1 | FASE-CONFIG-1 | sync_versions fix (CR-1, CR-2, CR-3) | 4 | 0 | ✓ |
| 2 | FASE-CONFIG-2 | Fallbacks peligrosos (CR-3) | 4 | 0 | ✓ |
| 3 | FASE-CONFIG-3A | Pricing extraction (CR-4 pricing) | 4 | 0 | ✓ |
| 4 | FASE-CONFIG-3B | Scenarios + financial engine (CR-4) | 4 | 0 | ✓ |
| 5 | FASE-CONFIG-4 | Template + comerciales (CR-5) | 4 | 0 | ✓ |
| 6 | FASE-CONFIG-5 | Umbrales + narrativas (CR-7) | 4 | 0 | ✓ |
| 7 | FASE-CONFIG-6 | Config reconnect + Deprecación módulos (CR-6 + H6) | 4 | 0 | ✓ |
| 8 | FASE-CONFIG-7 | Tests + v4complete Amazilia + Análisis | 3 | 1 | ✓ |
| 9 | FASE-CONFIG-8 | Suite de tests de regresión | 4 | 0 | ✓ |
| 10 | FASE-RELEASE-4.38.0 | Documentación + Release oficial | 4 | 0 | ✓ |

## Cómo Iniciar

Cada fase se ejecuta en una sesión nueva. El prompt para la primera fase:

```
Carga y ejecuta .opencode/plans/05-prompt-inicio-sesion-fase-CONFIG-1.md siguiendo .agents/workflows/phased_project_executor.md
```

## Archivos del Plan

```
.opencode/plans/
├── README.md
├── dependencias-fases.md
├── 06-checklist-implementacion.md
├── 05-prompt-inicio-sesion-fase-CONFIG-1.md
├── 05-prompt-inicio-sesion-fase-CONFIG-2.md
├── 05-prompt-inicio-sesion-fase-CONFIG-3A.md
├── 05-prompt-inicio-sesion-fase-CONFIG-3B.md
├── 05-prompt-inicio-sesion-fase-CONFIG-4.md
├── 05-prompt-inicio-sesion-fase-CONFIG-5.md
├── 05-prompt-inicio-sesion-fase-CONFIG-6.md        ← ACTUALIZADO: incluye deprecación
├── 05-prompt-inicio-sesion-fase-CONFIG-7.md
├── 05-prompt-inicio-sesion-fase-CONFIG-8.md
├── 05-prompt-inicio-sesion-fase-RELEASE-4.38.0.md
└── 09-documentacion-post-proyecto.md
```

## Cobertura de Hallazgos (Actualizada)

| Hallazgo | Fase(s) que lo cubren | Estado |
|----------|----------------------|--------|
| H1: sync_versions bug (CR-1, CR-2, CR-3) | FASE-CONFIG-1 | Cubierto |
| H2: Hardcodes Grupo A (fallbacks) | FASE-CONFIG-2 | Cubierto |
| H2: Hardcodes Grupo B (financieros) | FASE-CONFIG-3A, 3B | Cubierto |
| H2: Hardcodes Grupo C+D (comerciales) | FASE-CONFIG-4 | Cubierto |
| H3: Hardcodes N-01 a N-12 | FASE-CONFIG-3B, 4, 5, 3A | Cubierto |
| H4: TODOs y stubs | FASE-CONFIG-2 (flags) + FASE-CONFIG-6 (deprecación) | Cubierto |
| H5: settings.yaml disconnect | FASE-CONFIG-6 | Cubierto |
| **H6: Módulos huérfanos analytics/ (NUEVO)** | **FASE-CONFIG-6** | **Cubierto** |

### GAPs NO cubiertos

| GAP | Razón | Mitigación |
|-----|-------|------------|
| Profound AI Visibility (3 métricas) | API paga no disponible. No alimenta scores. | Transparencia honesta: "No disponible en esta versión" |
| Coordenadas 0.0 en auditors | Bug de datos, no de configuración | Fuera de scope |
| scraper_fallback LLM stub | Feature no implementada, baja prioridad | Fuera de scope |
