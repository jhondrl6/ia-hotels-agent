# FASE-P0-C: Fix Encoding UTF-8 en Writers de Artefactos (F7)

**ID**: CREDIBILIDAD-NUMERICA-2026-08-20 / FASE-P0-C
**Objetivo**: Garantizar que TODOS los writers de artefactos (JSON/MD/HTML de output) usen
`encoding='utf-8'` explícito para eliminar el encoding corrupto que produce artefactos ilegibles.
**Dependencias**: FASE-P0-A ✅ y FASE-P0-B ✅ (por orden de conflictividad en hook_pdf_generator.py)
**Duración estimada**: 1 sesión (≤60 iteraciones)
**Skill**: `phased_project_executor.md` — **fase DELEGABLE vía `delegate_task`**

## Modo de Ejecución — delegate_task (AJUSTADO)

Esta fase es **delegable** porque el fix es un patrón mecánico repetitivo (agregar
`encoding='utf-8'` a `open()`/`json.dump`/`Path.write_text` en writers), sin decisión
arquitectónica. El agente principal actúa como coordinador:

```
SI el presupuesto del agente principal es limitado:
  → delegate_task(
      goal="Auditar y corregir encoding utf-8 en todos los writers de artefactos del proyecto",
      context="""
        FALLO F7: artefactos de salida con encoding corrupto (cp1252 por defecto en Windows).
        EJEMPLO REAL: delivery_quality_report.json lanza UnicodeDecodeError (byte 0xf3).
        TAREA:
        1. Buscar TODOS los open() y json.dump() en modules/ que escriben a output/
        2. Agregar encoding='utf-8' explícito en cada uno
        3. NO cambiar lógica de negocio, solo encoding
        4. Tests: pytest tests/ -k encoding -v (si no existen, crear 1 test de contrato)
      """,
      timeout=600,
      toolsets=["file", "terminal"]
    )
  → Agente principal verifica el diff con git diff + ejecuta tests completos
SI no (presupuesto suficiente):
  → Ejecución DIRECTA (más eficiente, evita overhead de spawn)
```

**Regla**: el agente principal SIEMPRE ejecuta los tests finales y la validación
`run_all_validations.py --quick` — NO delegar la verificación.

## Contexto

CONTEXT §2 fallo **F7**: `delivery_quality_report.json` dentro del ZIP de entrega lanza
`UnicodeDecodeError` (byte 0xf3); mojibake en `data/benchmarks/plan_maestro_data.json`;
"B+ ? Datos fuente" en el diagnóstico FASE-F. Causa raíz: `open()`/`json.dump` sin
`encoding='utf-8'` explícito en Windows (cp1252 por defecto). Reconfirmado en la corrida
s5b (§7.2). P0 es prerrequisito del primer cliente.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-P0-A | ✅ Completada |
| FASE-P0-B | ✅ Completada |

### Base Técnica Disponible
- Módulos que generan artefactos: `modules/asset_generation/`, `modules/quality_gates/`,
  `modules/delivery/`, `modules/commercial_documents/`, `modules/financial_engine/`
- Tests base: 3,233 funciones + nuevos de P0-A y P0-B

## Tareas

### T1: Auditoría de writers de artefactos
**Objetivo**: identificar TODOS los puntos de escritura de archivos de output que NO usan
encoding explícito. Buscar en `modules/` con patrones:
- `open(` sin `encoding=`
- `json.dump(` sin `encoding=` en el file handle
- `Path.write_text(` sin `encoding=`
**Criterios de aceptación**:
- [ ] Inventario escrito de archivos+writers afectados (guardar en notas de la fase)

### T2: Fix — agregar encoding='utf-8' en cada writer
**Criterios de aceptación**:
- [ ] Todos los writers de artefactos usan `encoding='utf-8'` explícito
- [ ] Sin cambios de lógica de negocio (solo encoding)
- [ ] Tests existentes siguen pasando

### T3: Test de contrato anti-regresión
**Criterios de aceptación**:
- [ ] Test nuevo: verificar que un artefacto JSON generado por el pipeline es legible con `encoding='utf-8'`
- [ ] Test nuevo: verificar que NO hay mojibake en campos de texto de diagnóstico (ej. "B+ ? Datos fuente" → "B+ – Datos fuente")
- [ ] Suite afectada pasa sin fallos NUEVOS vs línea base (§6 del 01-plan-maestro)

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Encoding artefactos | `tests/test_encoding_artifacts.py` (nuevo) | Contrato F7 pasa |
| Regresión global | `pytest tests/ -k "delivery or quality_gates" -v` | 0 fallos NUEVOS (línea base §6 del 01-plan-maestro) |

**Comando de validación**:
```powershell
.\venv\Scripts\python.exe -m pytest tests/ -k "encoding or delivery or quality_gates" -v
.\venv\Scripts\python.exe scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. `dependencias-fases.md` y `06-checklist-implementacion.md`: marcar FASE-P0-C ✅.
2. `README.md` del plan: actualizar tabla de progreso.
3. `09-documentacion-post-proyecto.md`: secciones A/B/D/E.
4. `10-analisis-post-implementacion.md`: fila de ejecución + mínimo 3 lecciones.
5. **Registrar la fase**:
```powershell
.\venv\Scripts\python.exe scripts/log_phase_completion.py --fase FASE-P0-C --desc "Fix encoding utf-8 en writers de artefactos (F7)" --archivos-mod "<rutas REALES del inventario T1, separadas por coma — SIN wildcards>" --tests "<N>" --check-manual-docs
```
6. Editar CHANGELOG.md y GUIA_TECNICA.md (template §6).

## Criterios de Completitud (CHECKLIST)

- [ ] Test de encoding pasa (artefacto JSON legible utf-8)
- [ ] Suite delivery + quality_gates sin fallos NUEVOS vs línea base (§6 del 01-plan-maestro)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Post-ejecución completada

## Restricciones

- Máximo 60 iteraciones.
- NO cambiar lógica de negocio (solo encoding).
- NO modificar tests existentes salvo que sean incompatibles con el fix.
- NO ejecutar v4complete.
