# FASE-CONFIG-2: Extracción de Fallbacks Peligrosos (CR-3)

**Plan:** FEATURE-CONFIG-EXTRACTION v1.0.0
**Workflow:** `.agents/workflows/phased_project_executor.md` v2.9.0
**Presupuesto:** 60 iteraciones max | **Estimado esta fase:** ~44 iteraciones
**Dependencias:** FASE-CONFIG-1 (sync propagará cambios a docs)
**Fase siguiente:** FASE-CONFIG-3A

---

## Contexto

**Fuente:** `.opencode/context/TECHNICAL_DEBT_2026-04-29.md` §HALLAZGO 2, Grupo A (líneas 164-173)

### Problema

4 fallbacks en el código producen DATOS FALSOS si el módulo upstream falla silenciosamente. El cliente ve un número inventado sin saber que es fallback:

| ID | Fallback | Archivo | Línea | Valor | Peligro |
|----|----------|---------|-------|-------|---------|
| H-11 | benchmark_score | v4_proposal_generator.py | L1040 | 58 | Cliente ve "promedio regional 58" sin importar región real |
| H-12 | score_tecnico | v4_proposal_generator.py | L573, L986 | 50 | Cliente ve 50/100 sin disclaimer |
| H-13 | coherence_score | v4_proposal_generator.py | L569 | '70' (string) | Cliente ve coherencia "70%" inventada |
| H-27 | voice_readiness | v4_diagnostic_generator.py | L613-617 | '0' + 'unknown' | Cero falso sin explicación |

### Causa Raíz (CR-3)

Fallbacks silenciosos: el código usa `getattr(x, 'field', DEFAULT)` o `x or DEFAULT` sin notificar al template que el valor es estimado. El generador de documentos no distingue entre dato real y fallback.

---

## Tareas Específicas

### Tarea 1: Crear config/fallbacks.yaml con schema validado
Crear archivo YAML con estructura:
```yaml
# config/fallbacks.yaml
version: "1.0.0"
description: "Valores de fallback cuando datos reales no están disponibles"

scores:
  benchmark_score:
    value: 58
    type: int
    description: "Score regional de referencia cuando no hay benchmarks reales"
  score_tecnico:
    value: 50
    type: int
    description: "Score técnico cuando el módulo de auditoría falla"
  coherence_score:
    value: 70
    type: int
    description: "Score de coherencia cuando no se puede calcular"
  voice_readiness:
    value: 0
    type: int
    description: "Voice readiness cuando el proxy falla"
  voice_status:
    value: "unknown"
    type: str
    description: "Estado de voice readiness sin datos reales"

flags:
  show_estimated_badge: true
  estimated_text: "⚠️ Valor estimado — no se pudo verificar con fuentes externas"
```

Agregar validación de schema al cargar (tipos correctos, rangos válidos).

### Tarea 2: Refactorizar v4_proposal_generator.py (4 hardcodes)
- **L569 (H-13):** Reemplazar `'70'` con carga de `fallbacks.yaml → scores.coherence_score`
- **L573 (H-12):** Reemplazar `50` con carga de YAML → `scores.score_tecnico`
- **L986 (H-12):** Mismo fix que L573 (segunda ubicación)
- **L1040 (H-11):** Reemplazar `58` con carga de YAML → `scores.benchmark_score`
- Agregar método `_load_fallback(key)` que lee YAML con cache
- Agregar flag `is_estimated=True` al contexto del template cuando se usa fallback
- Inyectar `${estimated_disclaimer}` en template cuando aplique

### Tarea 3: Refactorizar v4_diagnostic_generator.py (H-27)
- **L613-614 + L616-617:** Reemplazar '0' y 'unknown' con carga de YAML
- Agregar flag `voice_estimated=True` cuando se usa fallback
- Inyectar disclaimer en sección de voice readiness del diagnóstico

### Tarea 4: Tests de fallback
- Test: YAML presente → usa valores de YAML
- Test: YAML ausente → error claro (no crash silencioso)
- Test: YAML con valor inválido (string en vez de int) → error de schema
- Test: flag `is_estimated` presente en output cuando se usa fallback
- Test: flag NO presente cuando el valor es real (no fallback)
- Verificar que `fallbacks.yaml` aparece en output de `doctor.py --status`

---

## Archivos Involucrados

| Archivo | Tipo | Hardcodes |
|---------|------|-----------|
| `config/fallbacks.yaml` | NUEVO | H-11, H-12, H-13, H-27 |
| `modules/commercial_documents/v4_proposal_generator.py` | MODIFICAR | H-11 (L1040), H-12 (L573, L986), H-13 (L569) |
| `modules/commercial_documents/v4_diagnostic_generator.py` | MODIFICAR | H-27 (L613-617) |

---

## Criterios de Completitud

- [x] `config/fallbacks.yaml` creado con schema validado
- [x] H-11 benchmark_score → leído de YAML (no hardcoded en código)
- [x] H-12 score_tecnico → leído de YAML (ambas ubicaciones L592, L1005)
- [x] H-13 coherence_score → leído de YAML
- [x] H-27 voice_readiness → leído de YAML
- [x] Flag "estimated" visible en template cuando se usa fallback
- [x] Tests: YAML presente, ausente, corrupto, flags correctos (16/16 PASSED)
- [x] Fallbacks originales NO existen como literales en el código Python

---

## Restricciones

- **NO modificar** lógica de negocio (solo fuente de valores)
- **NO eliminar** la capacidad de fallback (solo hacerla configurable y visible)
- **NO ejecutar** v4complete
- **NO crear** otros archivos YAML (solo fallbacks.yaml)
- **Máximo 60 iteraciones** (R2)

---

## Post-Ejecución

```bash
mkdir -p evidence/fase-config-2
cp config/fallbacks.yaml evidence/fase-config-2/
cp modules/commercial_documents/v4_proposal_generator.py evidence/fase-config-2/
cp modules/commercial_documents/v4_diagnostic_generator.py evidence/fase-config-2/

venv/Scripts/python.exe scripts/log_phase_completion.py     --fase FASE-CONFIG-2     --desc "Extracción de fallbacks a config/fallbacks.yaml: benchmark_score, score_tecnico, coherence_score, voice_readiness + flag estimated"     --archivos-nuevos "config/fallbacks.yaml"     --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/v4_diagnostic_generator.py"     --tests "5"     --check-manual-docs
```

**Siguiente fase:**
```
Carga y ejecuta .opencode/plans/05-prompt-inicio-sesion-fase-CONFIG-3A.md siguiendo .agents/workflows/phased_project_executor.md
```
