# FASE-R0-D — Fix B6+B7: Propuesta comercial condicional (plan 30 días + servicios adicionales)

**ID**: FASE-R0-D
**Objetivo**: Eliminar la mención hardcoded "(WhatsApp + datos para IA)" del plan de 30 días de la propuesta (condicionarla a `whatsapp_conflict` real) y corregir la narrativa de "Servicios adicionales disponibles" para el botón de WhatsApp cuando no es brecha.
**Dependencias**: Ninguna hard (archivos independientes de A/B/C); orden canónico tras FASE-R0-C por R1.
**Duración estimada**: 45-60 minutos
**Skill**: phased_project_executor v2.15.0
**Lectura previa obligatoria**: `.opencode/context/Historico/CONTEXT-REFACTOR-COHERENCIA-NARRATIVA-FUGAS-WHATSAPP-2026-08-22.md` — §2 (Bug 6, Bug 7), §4.4, §4.6, §4.7, §8 (AC11)

---

## Contexto

La propuesta de Zione muestra "Semana 2: Implementación Fase 1 (WhatsApp + datos para IA): Hotel Schema" cuando WhatsApp NO es un problema detectado (B6, `v4_proposal_generator.py` L2195), y lista "Botón de WhatsApp" como "Servicios adicionales disponibles" (B7, L1455-1457) — técnicamente correcto pero narrativamente confuso cuando el diagnóstico (pre-fix) lo señalaba como fuga #1. Tras R0-B el diagnóstico ya no menciona WhatsApp como fuga, por lo que B7 queda mayormente auto-resuelto; se implementa la Opción B del CONTEXT §4.7 para robustez completa.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-R0-A | ✅ Completada (B2) |
| FASE-R0-B | ✅ Completada (B1+B4) |
| FASE-R0-C | ✅ Completada (B3+B5) |

### Base Técnica (verificada contra código vivo 2026-08-22)

- **Archivo**: `modules/commercial_documents/v4_proposal_generator.py` (2,411 líneas).
- **B6 — L2195** (anclar por `Implementación Fase 1 (WhatsApp + datos para IA)`):

```python
# P1 assets needing client data
if p1_assets:
    asset_names = [a.asset_type.replace("_", " ").title() for a in p1_assets[:3]]
    items.append(f"- [ ] **Semana 2**: Implementación Fase 1 (WhatsApp + datos para IA): {', '.join(asset_names)}")
```

- **B6 — dato clave**: el parámetro `whatsapp_conflict` YA se extrae en el mismo generador (zona L792-798) pero NO se pasa a `_build_30_day_plan()`. El fix es cablear el parámetro existente (lección L16: el gap está en el caller).
- **B7 — L1455-1457** (anclar por `Servicios adicionales disponibles`):

```python
if excluded_services:
    excluded_names = ", ".join(excluded_services)
    rows.append(f"\n> **Servicios adicionales disponibles:** {excluded_names}")
```

- **Evidencia del output Zione**: 02_PROPUESTA L60: "Servicios adicionales disponibles: Botón de WhatsApp, Schema Organization"; L203: "Semana 2: Implementación Fase 1 (WhatsApp + datos para IA): Hotel Schema".
- **Tests de referencia**: `tests/commercial_documents/test_proposal_dynamic.py` (490 líneas) y `tests/commercial_documents/test_proposal_breach_consistency.py`.
- **Base de tests**: 3,368 funciones tras R0-A/B/C. Esta fase agrega 4 tests.

---

## Modo de Ejecución: DIRECTO (agente principal)

**Justificación** (executor): código+tests puro con venv Windows (regla venv WSL). Sin comandos largos, sin trabajo paralelo (un solo archivo de código + tests).

**Presupuesto de iteraciones** (R2, máx. 60): ~8 investigación (leer `_build_30_day_plan` completo + sus callers) + ~15 implementación + ~12 tests + ~10 docs + margen.

---

## Tareas

### Tarea 1: Fix B6 — Plan 30 días condicional

**Archivos afectados**: `modules/commercial_documents/v4_proposal_generator.py`

**Pasos**:
1. Leer `_build_30_day_plan()` completo y localizar TODOS sus callers (grep `_build_30_day_plan`).
2. Agregar el parámetro `whatsapp_conflict: bool = False` a la firma (default conservador para backwards compatibility).
3. Actualizar los callers para pasar el valor ya extraído en la zona L792-798 del generador.
4. Condicionar la mención:

```python
# Antes (hardcoded):
items.append(f"- [ ] **Semana 2**: Implementación Fase 1 (WhatsApp + datos para IA): {', '.join(asset_names)}")

# Después (condicional — CONTEXT §4.6):
whatsapp_mention = "WhatsApp + " if whatsapp_conflict else ""
items.append(f"- [ ] **Semana 2**: Implementación Fase 1 ({whatsapp_mention}datos para IA): {', '.join(asset_names)}")
```

**Criterios**:
- [ ] Con `whatsapp_conflict=False` (caso Zione): "Semana 2: Implementación Fase 1 (datos para IA): …" — sin WhatsApp (AC11)
- [ ] Con `whatsapp_conflict=True`: la mención "WhatsApp + datos para IA" se conserva
- [ ] Todos los callers actualizados; ningún caller rompe por la firma nueva (default False)

### Tarea 2: Fix B7 — Narrativa de servicios adicionales (Opción B corregida)

**Archivos afectados**: `modules/commercial_documents/v4_proposal_generator.py` (zona L1454-1457)

**⚠️ Hechos verificados del código vivo (críticos para el diseño)**:
1. `excluded_services` contiene **display names** (`service_name` del iter `PROPOSAL_SERVICE_TO_ASSET.items()`, L1338-1339/L1379), **NO asset_types**. Un check `"whatsapp_button" in excluded_services` NUNCA sería True.
2. Un servicio entra a `excluded_services` cuando `not has_asset and not is_present` (L1376-1380) — es decir, NO hay asset generado NI señal de presencia en producción. Por tanto, afirmar "ya presente y funcional en su sitio (verificado)" para un servicio excluido sería **factualmente falso** (no existe señal de presencia que lo respalde).
3. El signal dinámico correcto YA está en scope: `breach_by_asset = self._build_dynamic_breach_map(opportunity_scores)` (L1310) — si existe una brecha real ligada al botón de WhatsApp, `breach_by_asset.get("whatsapp_button")` es no-None.

**Cambio** (Opción B corregida): cuando NO exista brecha ni conflicto ligado a WhatsApp (`not whatsapp_conflict` y `breach_by_asset.get("whatsapp_button")` vacío), el botón de WhatsApp NO se ofrece como "servicio adicional disponible" — ofrecer algo que el diagnóstico no señala como problema es ruido narrativo. Para trackearlo correctamente, acumular en la exclusión también el `asset_type`:

```python
# Esquema de la lógica (adaptar a las variables reales del scope):
# En el loop L1338+: cambiar excluded_services a lista de tuplas (asset_type, service_name)
# o trackear whatsapp_service_name por separado.
whatsapp_sin_brecha = (
    (whatsapp_service_name is not None)
    and (not whatsapp_conflict)
    and not breach_by_asset.get("whatsapp_button")
)
if excluded_services:
    if whatsapp_sin_brecha:
        otros = [s for s in excluded_services if s != whatsapp_service_name]
    else:
        otros = list(excluded_services)
    if otros:
        rows.append(f"\n> **Servicios adicionales disponibles:** {', '.join(otros)}")
    # Si whatsapp_sin_brecha: el botón simplemente NO se lista (sin claim de presencia)
```

**Reglas**:
- Reutilizar el valor de `whatsapp_conflict` ya disponible en el generador (misma fuente que Tarea 1) y `breach_by_asset` (datos vivos de opportunity_scores, L1310).
- La comparación debe ser contra el **service_name real** del catálogo (display name, p. ej. "Botón de WhatsApp") obtenido del iter `PROPOSAL_SERVICE_TO_ASSET` donde `asset_type == "whatsapp_button"` — NO hardcodear el string; derivarlo de `PROPOSAL_SERVICE_TO_ASSET` o `SERVICE_CATALOG`.
- NUNCA afirmar "ya presente y funcional" sin señal real de presencia (`presence_lookup`); los servicios en `excluded_services` por definición carecen de esa señal.
- Si `whatsapp_conflict=True` o existe brecha ligada al botón, permanece en "Servicios adicionales disponibles" (es solución legítima del conflicto — caso especial del PainSolutionMapper).

### Tarea 3: Tests nuevos

**Archivos afectados**: `tests/commercial_documents/test_proposal_dynamic.py`

| Test | Setup | Asserts |
|------|-------|---------|
| `test_proposal_plan_sin_whatsapp` | `whatsapp_conflict=False`, p1_assets con Hotel Schema | Plan 30 días NO contiene "WhatsApp + datos para IA"; contiene "datos para IA" (AC11) |
| `test_proposal_plan_con_whatsapp` | `whatsapp_conflict=True` | Plan 30 días SÍ contiene "WhatsApp + datos para IA" |
| `test_servicios_adicionales_sin_brecha_whatsapp` | `whatsapp_conflict=False`, sin brecha whatsapp en opportunity_scores, service_name del botón en excluded_services | El output NO lista el botón de WhatsApp en "Servicios adicionales disponibles" y NO afirma "ya presente" (B7 — sin señal de presencia no se afirma presencia) |
| `test_servicios_adicionales_con_brecha_whatsapp` | `whatsapp_conflict=True` (o brecha whatsapp en opportunity_scores) | El botón SÍ aparece en "Servicios adicionales disponibles" |

### Tarea 4: Verificación de no-regresión

```bash
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_proposal_dynamic.py tests/commercial_documents/test_proposal_breach_consistency.py tests/commercial_documents/test_proposal_confidence_disclosure.py tests/regression/ -v
```

- [ ] 4 tests nuevos pasan
- [ ] Suites de propuesta pasan (sin regresión en alineación propuesta↔brechas)
- [ ] `tests/regression/` pasa (26 tests)

### Tarea 5: Post-ejecución documental

Ver sección **Post-Ejecución**.

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| 4 tests nuevos (Tarea 3) | `tests/commercial_documents/test_proposal_dynamic.py` | 4/4 pasan |
| Suite proposal breach consistency | `tests/commercial_documents/test_proposal_breach_consistency.py` | 0 fallos |
| Regresión | `tests/regression/` | 26/26 |

> NOTA: NO ejecutar `tests/commercial_documents/test_proposal_generator.py` ni los otros archivos patológicos (excluidos por conftest L1/L11 — fuga de RAM). NO ejecutar la suite completa.

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**: FASE-R0-D ✅ + notas.
2. **`README.md` del plan**: tabla de progreso actualizada.
3. **`06-checklist-implementacion.md`**: fila FASE-R0-D ✅.
4. **`09-documentacion-post-proyecto.md`**:
   - Sección B: plan 30 días condicional + botón de WhatsApp fuera de "Servicios adicionales" cuando no hay brecha/conflicto (sin claim de presencia).
   - Sección D: +4 tests (3,372).
   - Sección E: `v4_proposal_generator.py`, `test_proposal_dynamic.py`.
5. **`10-analisis-post-implementacion.md`**:
   - Resumen de Ejecución: fila FASE-R0-D.
   - Lecciones Aprendidas: mínimo 3.
   - Matriz de Verificación: filas B6 y B7.
6. **Registrar la fase**:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-R0-D \
    --desc "Fix B6+B7: plan 30 dias condicional a whatsapp_conflict + boton WhatsApp fuera de servicios adicionales sin brecha" \
    --archivos-mod "modules/commercial_documents/v4_proposal_generator.py" \
    --tests "4" \
    --check-manual-docs
```

> **SIN flag `--release`**.

7. **Validación final**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```
> Fallos "Version Sync"/"Document Integration" → `sync_versions.py` + re-validar (NO re-ejecutar tests).

8. **Regenerar DOMAIN_PRIMER**:
```bash
./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer
```

---

## Criterios de Completitud (CHECKLIST)

⚠️ Verificar ANTES de marcar como ✅ COMPLETADA ⚠️

- [ ] 4 tests nuevos pasan
- [ ] Suites obligatorias pasan (proposal_dynamic + breach_consistency + regression)
- [ ] grep "WhatsApp + datos para IA" en `modules/commercial_documents/v4_proposal_generator.py` → solo dentro de la rama condicional (`whatsapp_mention`), nunca incondicional
- [ ] Todos los callers de `_build_30_day_plan()` actualizados
- [ ] `log_phase_completion.py` ejecutado (SIN `--release`)
- [ ] `dependencias-fases.md`, `README.md`, `06-checklist`, `09`, `10` actualizados
- [ ] `run_all_validations.py --quick` TOTAL PASS

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- Máximo 60 iteraciones (R2). Si se alcanza: `⏳ INCOMPLETA` + checkpoint + cerrar sesión.
- **NO ejecutar `v4complete`** (reservado a FASE-R0-E — siguiente fase).
- NO modificar el diagnóstico ni su template (fases A/B/C ya completadas).
- NO alterar proposal_asset_matrix ni la lógica de excluded_services más allá de la narrativa (la clasificación técnica de servicios no cambia).
- NO bump de versión ni CHANGELOG (FASE-RELEASE-4.72.1).
- NO ejecutar archivos de test patológicos ni la suite completa.
- `log_phase_completion.py` SIN `--release`.
