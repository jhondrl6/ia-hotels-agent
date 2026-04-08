# FASE-F: Limpieza Legacy - gap_analyzer.py + report_builder.py

**ID**: FASE-F
**Objetivo**: Alinear módulos legacy (gap_analyzer.py, report_builder.py) con el nuevo modelo dinámico de brechas, eliminando hardcoded "4" y "3" que generan inconsistencias.
**Dependencias**: FASE-A ✅ (puede ejecutarse en paralelo con FASE-B o C)
**Duración estimada**: 1-2 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada |

### Problema Actual
Dos módulos legacy tienen hardcoded que choca con el nuevo modelo dinámico:

1. **`gap_analyzer.py`** (línea 38): Prompt pide "3 brechas criticas" al LLM
2. **`gap_analyzer.py`** (línea 162): Toma `[:5]` top alerts del scraper
3. **`report_builder.py`** (línea 1164): `[:4]` maximo 4 brechas

Nota: `gap_analyzer.py` es legacy (comando `spark` deprecado), pero `_basic_analysis()` sigue siendo usado como fallback cuando el LLM falla en v4complete. El `_basic_analysis()` usa un modelo de "2 Pilares" diferente al de `_identify_brechas()`, lo que genera inconsistencia.

### Base Técnica
- `modules/analyzers/gap_analyzer.py` (450 líneas)
  - `analyze_with_llm()`: Prompt pide "3 brechas" (línea 38)
  - `_summarize_scraper_alerts()`: `[:5]` top alerts (línea 162)
  - `_basic_analysis()`: Modelo "2 Pilares" genera máximo 2 brechas (líneas 199-368)
- `modules/generators/report_builder.py` (línea 1164): `[:4]` truncation

---

## Tareas

### Tarea 1: Alinear gap_analyzer.py con modelo dinámico

**Objetivo**: gap_analyzer ya no impone número fijo de brechas.

**Archivos afectados**:
- `modules/analyzers/gap_analyzer.py`

**Cambios**:
1. Línea 38: Cambiar `"Identifica las 3 brechas criticas MAS costosas"` por `"Identifica las brechas criticas detectadas (todas las que tengan evidencia real)"`
2. Línea 162: Cambiar `[:5]` por eliminar truncamiento o usar una constante `MAX_BRECHAS = 10`
3. En el JSON format del prompt (líneas 52-74): El array `brechas_criticas` ya no dice "3 items", permite N

**Nota CRÍTICA sobre `_basic_analysis()`**:
El fallback local genera exactamente 2 brechas (Pilar 1: GBP, Pilar 2: AEO). Esto es CORRECTO porque es un modelo simplificado de emergencia. NO es necesario expandirlo a N categorías - su trabajo es dar un resultado rápido cuando el LLM falla. Lo que sí debe hacer es:
- NO mentir diciendo que son "3" si genera 2
- Documentar que genera "2 Pilares" como fallback

**Criterios de aceptación**:
- [ ] Prompt LLM no pide número fijo de brechas
- [ ] `_summarize_scraper_alerts()` no trunca a 5 (o usa constante explícita)
- [ ] Tests existentes de gap_analyzer pasan

### Tarea 2: Alinear report_builder.py con modelo dinámico

**Objetivo**: report_builder no trunca a 4.

**Archivos afectados**:
- `modules/generators/report_builder.py` (línea 1164)

**Cambios**:
1. Línea 1164: Cambiar `[:4]` por eliminar truncamiento o usar constante configurable
2. Verificar si report_builder.py está activo o es legacy

**Criterios de aceptación**:
- [ ] No hay `[:4]` en lógica de brechas
- [ ] Tests existentes pasan

### Tarea 3: Documentar modelo de brechas unificado

**Objetivo**: Un comentario/docstring que explique la arquitectura de brechas.

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (docstring de clase)

**Agregar**:
```python
# ARQUITECTURA DE BRECHAS (fuente: FASE-A)
# ===========================================
# _identify_brechas() es la UNICA fuente de verdad para brechas del diagnóstico.
# Detecta hasta 10 categorías de problemas basadas en evidencia real del audit.
# Retorna N brechas (0-10) sin defaults genéricos.
#
# Cadena de flujo:
#   V4AuditResult → _identify_brechas() → DiagnosticSummary.brechas
#       → v4_diagnostic_generator (template con N brechas)
#       → v4_proposal_generator (distribución proporcional)
#       → PainSolutionMapper (pain_ids → assets)
#
# Módulos legacy con modelos propios:
#   gap_analyzer._basic_analysis(): "2 Pilares" (solo fallback, no diagnóstico)
#   report_builder: legacy spark, usa datos de gap_analyzer
#
# NO agregar hardcoded "4" en ninguna parte de esta cadena.
```

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python -m pytest tests/analyzers/test_gap_analyzer.py -v 2>/dev/null || echo "No tests file - verify manually"
python scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-F como ✅ Completada
2. **`06-checklist-implementacion.md`**: Actualizar estado FASE-F
3. Ejecutar:
```bash
python scripts/log_phase_completion.py --fase FASE-F --desc "Limpieza legacy gap_analyzer + report_builder" --archivos-mod "modules/analyzers/gap_analyzer.py,modules/generators/report_builder.py,modules/commercial_documents/v4_diagnostic_generator.py" --check-manual-docs
```
4. `git add -A && git commit -m "FASE-F: limpieza legacy - sin hardcoded brechas en gap_analyzer y report_builder"`

## Criterios de Completitud (CHECKLIST)

- [ ] gap_analyzer.py no pide "3 brechas" fijas al LLM
- [ ] report_builder.py no trunca a `[:4]`
- [ ] Docstring de arquitectura de brechas agregado
- [ ] Tests existentes pasan sin regresión
- [ ] `python scripts/run_all_validations.py --quick` pasa
- [ ] No hay `[:4]` relacionado con brechas en todo el codebase (excluyendo venv)

## Restricciones

- NO expandir `_basic_analysis()` a N categorías (es fallback simplificado, correcto con 2)
- NO eliminar gap_analyzer (aún usado como fallback)
- Verificar que `v4complete` no depende de gap_analyzer para el diagnóstico principal
