# Plan de Documentación Post-Proyecto

**Proyecto**: Corrección Trazabilidad "Calidad Garantizada"
**Fecha**: 2026-04-24
**Última actualización**: 2026-04-25 (v3 — FASE-07 absorbida en FASE-06, 4 fases total)
**Versión target**: 4.35.1 (patch increment sobre 4.35.0)

---

## Estructura de Documentación

### Sección A: Módulos Afectados

| Módulo | Cambio | Fase |
|--------|--------|------|
| `README.md` | Corrección "6" → "9 gates" | FASE-TRAZABILIDAD-DOCS |
| `.agents/workflows/v4_complete.md` | Remover referencia a comando inexistente | FASE-TRAZABILIDAD-DOCS |
|| `modules/quality_gates/publication_gates.py` | Docstring corregido + T1-BUG02 fix | FASE-TRAZABILIDAD-DOCS + PATCH+SEO-06 |
|| `AGENTS.md` | Sincronización coherence score | FASE-TRAZABILIDAD-DOCS |
|| `main.py` | Cableado PublicationGatesOrchestrator + T3 seo_score en JSON | FASE-TRAZABILIDAD-RAIZ + PATCH+SEO-06 |
|| `modules/commercial_documents/v4_diagnostic_generator.py` | Template + gate_results + T2 encabezados secciones | FASE-TRAZABILIDAD-RAIZ + PATCH+SEO-06 |
|| `modules/commercial_documents/templates/diagnostico_v6_template.md` | T2: agregar `## ✅ Validación de Calidad` + `${manual_attention_table}` | PATCH+SEO-06 |
| `tests/quality_gates/test_publication_gates.py` | 16 tests (originales + nuevos) | FASE-TRAZABILIDAD-RAIZ |

### Sección B: Métricas Acumulativas

| Métrica | Antes | Después |
|---------|-------|---------|
| Publication Gates ejecutados | 1/9 (solo coherence) | 9/9 |
| Código muerto | 1062 líneas (publication_gates.py) | 0 líneas (cableado) |
| Tests | 0 para publication gates | 16 tests |
| Trazabilidad en output | 0% | 100% (gate_report.json + sección en doc) |
| Coherence Score | 0.84 (AGENTS.md) / 0.89 (último doc) | Sincronizado |
| SEO score en JSON | Ausente | Presente (v4_complete_report.json) |
| Secciones diagnóstico | Sin encabezados formales | "## 🔍 Trazabilidad de Brechas" + "## ✅ Validación de Calidad" |

### Sección C: Archivos de Plan

| Archivo | Descripción |
|---------|-------------|
| `README.md` | Índice del directorio |
| `00-decisiones-deprecacion.md` | Decisiones de qué deprecar y por qué (DEP-01/02/03, RES-01/02/03, BUG-01/02) |
| `dependencias-fases.md` | Diagrama de dependencias + conflictos entre fases |
| `05-prompt-inicio-sesion-fase-trazabilidad-docs.md` | Prompt FASE 1 |
| `05-prompt-inicio-sesion-fase-trazabilidad-raiz.md` | Prompt FASE 2 |
| `05-prompt-inicio-sesion-fase-trazabilidad-validate.md` | Prompt FASE 3 |
| `06-checklist-implementacion.md` | Checklist maestro |
| `06-fase-trazabilidad-patch-issues.md` | **NUEVO** — Plan FASE-06 PATCH |
| `07-fase-seo-score.md` | **NUEVO** — Plan FASE-07 SEO-SCORE |
| `fase-trazabilidad-patch-eval.md` | **NUEVO** — Baseline + criterios de evaluación |
| `09-documentacion-post-proyecto.md` | Este archivo |

### Sección D: Flujo Documental (Post-Completitud Total)

Una vez completadas las 4 fases, ejecutar en orden:

```bash
# 1. Registrar cada fase en REGISTRY.md
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-TRAZABILIDAD-DOCS --desc "..." --check-manual-docs
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-TRAZABILIDAD-RAIZ --desc "..." --check-manual-docs
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-TRAZABILIDAD-VALIDATE --desc "..." --check-manual-docs
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-TRAZABILIDAD-PATCH+SEO --desc "..." --check-manual-docs

# 2. Sincronizar versiones
./venv/Scripts/python.exe scripts/sync_versions.py

# 3. Validar CHANGELOG
# Verificar formato: Objetivo / Cambios / Archivos / Tests

# 4. Validar GUIA_TECNICA.md
# Agregar nota técnica: "Notas de Cambios v4.35.1 - Trazabilidad Publication Gates"

# 5. Validación final
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/doctor.py --status
```

### Sección E: Checklist de Documentación Final

| Verificación | Estado |
|-------------|--------|
| REGISTRY.md actualizado (4 fases) | ⬜ |
| sync_versions.py ejecutado | ⬜ |
| CHANGELOG.md formato correcto (4 fases) | ⬜ |
| GUIA_TECNICA.md con nota técnica | ⬜ |
| run_all_validations.py --quick (4/4) | ⬜ |
| doctor.py --status sin errores | ⬜ |
| DOMAIN_PRIMER.md actualizado | ✅ (sin cambios necesarios) |
| AGENTS.md actualizado | ✅ |
| seo_score presente en v4_complete_report.json | ⬜ (T3 PATCH+SEO-06) |
| Encabezados de sección en diagnóstico | ⬜ (T2 PATCH+SEO-06) |
