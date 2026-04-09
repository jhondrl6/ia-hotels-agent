# FASE-B: Generator Dinámico — Construir N Brechas en Runtime

**ID**: FASE-B
**Objetivo**: Modificar `_prepare_template_data()` para construir `${brechas_section}` y `${brechas_resumen_section}` dinámicamente desde `_identify_brechas()`, y eliminar `min(..., 4)` en `_inject_brecha_scores()`.
**Dependencias**: FASE-A (templates deben tener placeholders `${brechas_section}` y `${brechas_resumen_section}`)
**Duración estimada**: 1-1.5h
**Skill**: phased_project_executor

---

## Contexto

FASE-A reemplazó las ranuras fijas por placeholders. Ahora el generator necesita llenar esos placeholders con markdown generado dinámicamente basado en las N brechas de `_identify_brechas()`.

Ver contexto: `.opencode/plans/context/01-causa-raiz-limite-4-brechas.md` secciones CAPA 2 y CAPA 3.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada |

### Base Técnica Disponible
- `_identify_brechas()` ya retorna lista dinámica (0-10 brechas)
- Cada brecha tiene: `pain_id`, `nombre`, `impacto`, `detalle`
- Tests existentes en `tests/commercial_documents/test_diagnostic_brechas.py` verifican dinámico

---

## Tareas

### Tarea 1: Agregar `_build_brechas_section()` al generator

**Objetivo**: Nuevo método que genera markdown para N brechas.

**Archivo afectado**: `modules/commercial_documents/v4_diagnostic_generator.py`

**Implementación**:
```python
def _build_brechas_section(self, audit_result: V4AuditResult, financial_scenarios: FinancialScenarios) -> str:
    """Genera sección markdown con TODAS las brechas detectadas (0-10+)."""
    brechas = self._identify_brechas(audit_result)
    if not brechas:
        return "No se detectaron brechas críticas. Su presencia digital está en buen estado."
    
    sections = []
    for i, b in enumerate(brechas, 1):
        costo = self._get_brecha_costo(audit_result, financial_scenarios, i-1)
        sections.append(
            f"### [BRECHA {i}] {b['nombre']}\n"
            f"- **Detalle:** {b['detalle']}\n"
            f"- **Por qué importa:** {int(b.get('impacto', 0) * 100)}%\n"
            f"- **Costo:** {costo} COP/mes\n"
        )
    return "\n".join(sections)
```

**Criterios de aceptación**:
- [ ] Genera markdown para 0, 1, 4, 7, 10 brechas sin error
- [ ] Usa `format_cop()` para costo
- [ ] Numeración secuencial correcta

### Tarea 2: Agregar `_build_brechas_resumen_section()` al generator

**Objetivo**: Genera tabla markdown dinámica para sección resumen.

**Implementación**:
```python
def _build_brechas_resumen_section(self, audit_result: V4AuditResult, financial_scenarios: FinancialScenarios) -> str:
    """Genera tabla resumen dinámica de N brechas → oportunidades."""
    brechas = self._identify_brechas(audit_result)
    if not brechas:
        return "| Sin brechas detectadas | — |"
    
    rows = []
    for i, b in enumerate(brechas):
        detalle_corto = b.get('detalle', 'Sin resumen')[:80]
        if len(b.get('detalle', '')) > 80:
            detalle_corto += '...'
        recuperacion = self._get_brecha_recuperacion(audit_result, financial_scenarios, i)
        rows.append(f"| {detalle_corto} | +{recuperacion}/mes |")
    return "\n".join(rows)
```

**Criterios de aceptación**:
- [ ] Tabla tiene N filas (no siempre 4)
- [ ] Cada fila tiene recuperación estimada

### Tarea 3: Integrar en `_prepare_template_data()`

**Archivo afectado**: `modules/commercial_documents/v4_diagnostic_generator.py`

**Cambios**:
1. En el dict `data` (alrededor línea 465), agregar:
   ```python
   'brechas_section': self._build_brechas_section(audit_result, financial_scenarios),
   'brechas_resumen_section': self._build_brechas_resumen_section(audit_result, financial_scenarios),
   ```

2. Mantener las variables `brecha_1_*` a `brecha_4_*` por retrocompatibilidad (no eliminar de inmediato para no romper templates legacy que aun no se actualicen). Pero las NUEVAS secciones serán la fuente de verdad.

**Criterios de aceptación**:
- [ ] `data['brechas_section']` contiene markdown para N brechas
- [ ] `data['brechas_resumen_section']` contiene tabla para N filas
- [ ] Variables brecha_1..4 siguen existiendo (retrocompatibilidad)

### Tarea 4: Eliminar `min(..., 4)` en `_inject_brecha_scores()`

**Archivo afectado**: `modules/commercial_documents/v4_diagnostic_generator.py` línea 1934

**Cambios**:
```python
# ANTES:
for i in range(1, min(scores_count, 4) + 1):

# DESPUÉS:
MAX_BRECHAS_SCORES = 10  # O el número que _identify_brechas() puede retornar
for i in range(1, min(scores_count, MAX_BRECHAS_SCORES) + 1):
```

**Criterios de aceptación**:
- [ ] `_inject_brecha_scores()` genera scores para N brechas (no limitado a 4)
- [ ] Cada score tiene: nombre, costo, detalle, severity, effort, impact_score

### Tarea 5: Ampliar tests

**Archivo afectado**: `tests/commercial_documents/test_diagnostic_brechas.py`

**Tests nuevos a agregar**:
1. `test_build_brechas_section_with_5_brechas` — Verifica que genera 5 secciones markdown
2. `test_build_brechas_section_with_0_brechas` — Verifica mensaje alternativo
3. `test_build_brechas_resumen_section_dynamic` — Tabla con N filas
4. `test_inject_brecha_scores_no_truncation` — Scores para 7+ brechas, no 4
5. `test_brecha_section_markdown_valid` — Cada sección tiene headers, detalle, costo

---

## Tests Obligatorios

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Tests de brechas
.venv/Scripts/python.exe -m pytest tests/commercial_documents/test_diagnostic_brechas.py -v

# Tests del generator
.venv/Scripts/python.exe -m pytest tests/test_commercial_documents_composer.py -v
.venv/Scripts/python.exe -m pytest tests/test_commercial_documents_phase2.py -v

# Validaciones rápidas
.venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-B como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar items de FASE-B
3. **`09-documentacion-post-proyecto.md`**: Sección A (métodos nuevos) + Sección D (tests)
4. **`log_phase_completion.py`**:
```bash
.venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-B \
    --desc "Generator dinamico N brechas" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py" \
    --archivos-nuevos "" \
    --tests "5" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] `_build_brechas_section()` genera markdown para N brechas
- [ ] `_build_brechas_resumen_section()` genera tabla para N filas
- [ ] `_prepare_template_data()` incluye ambos placeholders
- [ ] `min(..., 4)` eliminado de `_inject_brecha_scores()`
- [ ] 5 tests nuevos pasan
- [ ] Tests existentes no se rompen
- [ ] `dependencias-fases.md` actualizado
- [ ] `log_phase_completion.py` ejecutado
