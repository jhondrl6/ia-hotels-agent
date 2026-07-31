# FASE-1: F1 — Fix Tabla CAPEX Corrupta (MAYOR COMPLEJIDAD TÉCNICA)

## ⚠️ FASE DE MAYOR COMPLEJIDAD ⚠️
Requiere edición precisa de template markdown + test de integridad de estructura.

---

## Contexto de Fases Anteriores
- Primera fase del plan REFACTOR-CAPEX-BREAKDOWN v4.60.0
- Sin dependencias previas

---

## Bug: F1 — Tabla CAPEX Corrupta

### Causa Raíz (verificada contra código vivo)
**Commit culpable:** `e9da3bc` (FASE-1A IMP-03, 2026-05-29)
**Archivo:** `modules/commercial_documents/templates/propuesta_v6_template.md` L152
**Línea problemática:**
```markdown
| Desglose CAPEX | | ${capex_breakdown_table} | Detalle del activo |
```

### Mecanismo de falla
- `_build_capex_breakdown_table()` (L191-217) retorna tabla markdown completa:
  ```
  | Componente | Monto | Descripción |
  |---|---|---|
  | Auditoría Inicial | $800.000 COP | ... |
  ...
  ```
- `string.Template.safe_substitute()` inserta esta tabla COMPLETA dentro de una celda de la tabla exterior (4 columnas)
- Markdown NO soporta tablas anidadas → pipes internos se interpretan como columnas de la tabla exterior → estructura corrupta

### Evidencia del bug (output corrupto actual)
```
| Desglose CAPEX | | | Componente | Monto | Descripción |  ← 7 pipes (corrupto!)
|---|---|---|                                                ← 3 pipes (mismatch)
| Auditoría Inicial | $800.000 COP | ... |                  ← estructura rota
```

---

## Tareas

### T1: Fix template propuesta_v6_template.md

**Acción:** Eliminar L152 y agregar sección propia después de la nota CAPEX/OPEX

**Ubicación exacta:** `modules/commercial_documents/templates/propuesta_v6_template.md` L145-160

**Código ANTES (L147-160):**
```markdown
## 🏗️ CAPEX vs OPEX: Lo que es suyo vs. lo que es servicio

| Concepto | Tipo | Monto | ¿De quién es? |
|----------|------|-------|---------------|
| Setup fee (único) | **CAPEX** | ${capex_total} | **100% suyo** — Real Estate Digital |
| Desglose CAPEX | | ${capex_breakdown_table} | Detalle del activo |  ← ELIMINAR
| Fee mensual (×6) | **OPEX** | ${opex_total_6m} | Servicio de implementación |

${nota_capex_opex}

**Activos digitales que quedan en su propiedad:**
${activos_digitales_lista}
```

**Código DESPUÉS:**
```markdown
## 🏗️ CAPEX vs OPEX: Lo que es suyo vs. lo que es servicio

| Concepto | Tipo | Monto | ¿De quién es? |
|----------|------|-------|---------------|
| Setup fee (único) | **CAPEX** | ${capex_total} | **100% suyo** — Real Estate Digital |
| Fee mensual (×6) | **OPEX** | ${opex_total_6m} | Servicio de implementación |

${nota_capex_opex}

### Desglose del Setup Fee (CAPEX)
${capex_breakdown_table}

**Activos digitales que quedan en su propiedad:**
${activos_digitales_lista}
```

**Cambios:**
1. Eliminar: `| Desglose CAPEX | | ${capex_breakdown_table} | Detalle del activo |`
2. Agregar después de `${nota_capex_opex}`:
   ```markdown
   
   ### Desglose del Setup Fee (CAPEX)
   ${capex_breakdown_table}
   ```

**Verificación inmediata:**
```bash
grep -n 'capex_breakdown_table' modules/commercial_documents/templates/propuesta_v6_template.md
# Debe mostrar: UNA sola línea (la nueva sección), NO dentro de tabla
```

---

### T2: Agregar test de integridad de pipes en tabla CAPEX

**Motivación:** Ningún test actual verifica la estructura de la tabla CAPEX renderizada. Esta es la debilidad que permitió la regresión.

**Archivo:** `tests/test_capex_rename.py` (agregar nuevo test al final)

**Lógica del test:**
```python
def test_propuesta_capex_table_pipe_integrity(self):
    """Verify CAPEX vs OPEX table has exactly 4 pipes per row after rendering.
    
    Regression test for F1 bug: ${capex_breakdown_table} was embedded in a cell
    of the 4-column CAPEX table, causing pipe count mismatch and corrupt markdown.
    """
    # 1. Generar template data
    gen = V4ProposalGenerator(region='eje_cafetero')
    # Mock minimum required data (check existing tests for pattern)
    template_data = gen._prepare_template_data(...)
    
    # 2. Renderizar template
    with open('modules/commercial_documents/templates/propuesta_v6_template.md') as f:
        template_content = f.read()
    rendered = gen._render_template(template_content, template_data)
    
    # 3. Extraer sección CAPEX vs OPEX
    import re
    capex_section = re.search(
        r'## 🏗️ CAPEX vs OPEX.*?(?=\n## |\n### Desglose del Setup Fee)',
        rendered,
        re.DOTALL
    )
    assert capex_section, "CAPEX section not found in rendered output"
    
    # 4. Verificar que cada fila de tabla tiene exactamente 4 pipes
    table_lines = [line for line in capex_section.group(0).split('\n') 
                   if line.strip().startswith('|')]
    for line in table_lines:
        pipe_count = line.count('|')
        assert pipe_count == 5, (
            f"Expected 5 pipes (4 cells + closing) in CAPEX table row, "
            f"got {pipe_count}: {line}"
        )
    
    # 5. Verificar que Desglose existe como sección independiente
    assert '### Desglose del Setup Fee (CAPEX)' in rendered
    desglose_section = re.search(
        r'### Desglose del Setup Fee.*?(?=\n## |\n\*\*Activos digitales)',
        rendered,
        re.DOTALL
    )
    assert desglose_section, "Desglose section not found"
    
    # 6. Verificar que tabla de desglose tiene 3 pipes por fila
    desglose_lines = [line for line in desglose_section.group(0).split('\n')
                      if line.strip().startswith('|')]
    for line in desglose_lines:
        pipe_count = line.count('|')
        assert pipe_count == 4, (
            f"Expected 4 pipes (3 cells + closing) in desglose table row, "
            f"got {pipe_count}: {line}"
        )
```

**Nota:** Adaptar el test al patrón de los tests existentes en `test_capex_rename.py`. Verificar cómo se mockean los datos necesarios.

---

### T3: Ejecutar tests de regresión

**Comando:**
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/test_capex_rename.py tests/commercial_documents/test_financial_coherence.py -v
```

**Criterios de éxito:**
- ✅ Todos los tests existentes pasan sin cambios
- ✅ Nuevo test de integridad de pipes pasa
- ✅ Sin errores de importación o mock

---

## Post-Ejecución: log_phase_completion.py

**Comando (ejecutar SOLO si T1-T3 completan exitosamente):**
```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\log_phase_completion.py --fase FASE-1 --desc F1_CAPEX_template_fix_mayor_complejidad --archivos-mod modules/commercial_documents/templates/propuesta_v6_template.md --tests 1 --check-manual-docs"
```

---

## Actualizar Documentación

**Después de log_phase_completion.py:**

1. **CHANGELOG.md** (agregar entrada al inicio):
```markdown
## [4.60.0] - CAPEX Breakdown Fix & Cleanup — En progreso

### Cambios Implementados
- **FASE-1**: Fix tabla CAPEX corrupta (F1) — movido `${capex_breakdown_table}` a sección independiente
```

2. **GUIA_TECNICA.md** (agregar nota técnica):
```markdown
### Notas de Cambios v4.60.0 - FASE-1

**Problema:** Tabla CAPEX corrupta por anidamiento de tablas markdown (F1)
**Solución:** Mover `${capex_breakdown_table}` a sección propia después de la nota CAPEX/OPEX
**Módulos afectados:** `modules/commercial_documents/templates/propuesta_v6_template.md`
**Backwards compatibility:** ✅ Sin breaking changes
**Tests:** Nuevo test de integridad de pipes en `tests/test_capex_rename.py`
```

3. **09-documentacion-post-proyecto.md** (acumular datos):
Editar sección correspondiente con datos de FASE-1

---

## Criterios de Completitud

- [ ] **T1**: Template fix aplicado (grep confirma `${capex_breakdown_table}` en sección propia)
- [ ] **T2**: Test de integridad de pipes agregado y pasando
- [ ] **T3**: `pytest tests/test_capex_rename.py tests/commercial_documents/test_financial_coherence.py -v` → all pass
- [ ] **log_phase_completion.py**: Ejecutado exitosamente
- [ ] **Docs cascade**: CHANGELOG, GUIA_TECNICA, 09-documentacion actualizados

---

## Restricciones

- **NO ejecutar v4complete** (eso es FASE-4)
- **NO modificar `v4_proposal_generator.py`** (eso es FASE-2 y FASE-3)
- **NO modificar `config/commercial.yaml`** (datos correctos, verificados)
- **Máximo 60 iteraciones** del agente
- **Verificar contra código vivo** antes de aplicar patch (los line numbers pueden estar stale)

---

## Budget de Iteraciones Estimado

```
Fijos:
  - Leer plan + verificar estado: ~3 iters
  - Investigar código/archivos: ~5-10 iters
  - log_phase_completion.py + docs cascade: ~10 iters
  Total fijo: ~18-23 iters

Específico:
  - T1 (fix template): ~5-8 iters
  - T2 (agregar test): ~10-15 iters
  - T3 (run tests): ~2-3 iters
  Total específico: ~17-26 iters

Total estimado: 35-49 iters (dentro del límite de 60)
```

**Modo de ejecución:** Agente principal DIRECTO (código puro, sin comandos largos)

---

## Recuperación en Caso de Agotamiento

Si el agente alcanza 60 iteraciones:
1. Guardar estado actual del template (si ya se editó)
2. Marcar fase como `⏳ INCOMPLETA` en el plan
3. Documentar checkpoint en esta sección
4. Retomar en nueva sesión

---

## Checklist Final

- [ ] Template L152 eliminado
- [ ] Sección `### Desglose del Setup Fee (CAPEX)` agregada
- [ ] Test `test_propuesta_capex_table_pipe_integrity` agregado
- [ ] Todos los tests pasan
- [ ] log_phase_completion.py ejecutado
- [ ] CHANGELOG.md actualizado
- [ ] GUIA_TECNICA.md actualizado
- [ ] 09-documentacion-post-proyecto.md actualizado
