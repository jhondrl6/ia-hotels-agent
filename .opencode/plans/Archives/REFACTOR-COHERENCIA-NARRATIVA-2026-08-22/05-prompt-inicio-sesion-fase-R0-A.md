# FASE-R0-A — Fix B2: Quick Win #1 con texto correcto (condición Schema)

**ID**: FASE-R0-A
**Objetivo**: Corregir el texto del Quick Win #1 en `_build_quick_wins()` para que corresponda a su condición real (`not hotel_schema_detected`) y no mencione WhatsApp cuando el audit lo reporta verificado.
**Dependencias**: Ninguna (primera fase del plan).
**Duración estimada**: 30-45 minutos
**Skill**: phased_project_executor v2.15.0
**Lectura previa obligatoria**: `.opencode/context/Historico/CONTEXT-REFACTOR-COHERENCIA-NARRATIVA-FUGAS-WHATSAPP-2026-08-22.md` — §2 (Bug 2), §4.2 (Fix propuesto), §8 (AC2, AC12)

---

## Contexto

El output E2E de Zione (whatsapp_status=VERIFIED) muestra el Quick Win #1 "Corregir el número de WhatsApp en Google Maps" disparado por la condición `not hotel_schema_detected` — un copy-paste que contradice los datos del audit (la Sección 2 reporta "✅ WhatsApp verificado — Canal directo funcional"). Este es el bug B2 de 7 manifestaciones de fosilización narrativa.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| (ninguna — primera fase del plan) | — |

### Base Técnica

- **Archivo a modificar**: `modules/commercial_documents/v4_diagnostic_generator.py` (3,544 líneas), método `_build_quick_wins()`, zona L1883-1888 (anclar por contenido: el comentario `# Schema implementation — translated to owner's action + delegation`).
- **Código actual** (verificado contra código vivo 2026-08-22):

```python
# Schema implementation — translated to owner's action + delegation
if audit_result.schema and not audit_result.schema.hotel_schema_detected:
    wins.append(
        f"{win_number}. **HOY (5 minutos): Corregir el número de WhatsApp en Google Maps.** "
        f"→ Usted mismo puede hacerlo desde su celular."
    )
    win_number += 1
```

- **Tests de referencia**: `tests/commercial_documents/test_diagnostic_generator.py` (incluye D8 tests del plan CREDIBILIDAD-NUMERICA — usar sus fixtures como base).
- **No afectado**: `tests/test_top_problems_consistency.py` usa `calculate_quick_wins` (función distinta) — verificar tras el cambio que sigue pasando.
- **Base de tests del sistema**: 3,360 funciones / 261 archivos. Esta fase agrega 1 test.

---

## Modo de Ejecución: DIRECTO (agente principal)

**Justificación** (executor §Regla-de-Decisión-código+tests): fase de implementación pura (fix + tests), sin comandos de larga duración ni trabajo paralelo independiente. El overhead de spawn de subagente degrada este perfil de fase. Los tests requieren el venv Windows del proyecto (regla venv WSL: `./venv/Scripts/python.exe`), al que los subagentes no tienen acceso.

**Presupuesto de iteraciones** (R2, máx. 60): ~5 lectura/verificación + ~10 fix + ~10 tests + ~10 docs/post-ejecución + margen.

---

## Tareas

### Tarea 1: Fix del texto Quick Win #1 (Bug 2)

**Archivos afectados**: `modules/commercial_documents/v4_diagnostic_generator.py` (método `_build_quick_wins`)

**Pasos**:
1. Leer el método `_build_quick_wins()` COMPLETO para confirmar que no existe otra rama que mencione WhatsApp sin una condición real de conflicto (lección del CONTEXT §3: "Nunca declarar bug sin leer el archivo completo").
2. Reemplazar el texto del Quick Win disparado por `not hotel_schema_detected`:

```python
# Antes (incorrecto — copy-paste, contradice la condición):
f"{win_number}. **HOY (5 minutos): Corregir el número de WhatsApp en Google Maps.** "
f"→ Usted mismo puede hacerlo desde su celular."

# Después (propuesta base del CONTEXT §4.2 — ajustar redacción final para
# coherencia con el marco narrativo DIY de los Quick Wins):
f"{win_number}. **HOY (5 minutos): Verificar qué datos de su hotel faltan en Google (ficha y resultados de búsqueda).** "
f"→ Usted mismo puede hacerlo desde su celular: busque su hotel y anote qué información no aparece."
```

**Reglas del cambio**:
- El texto NO puede mencionar WhatsApp (AC2, AC12).
- El texto DEBE corresponder a la brecha real que dispara la condición: datos del hotel (Hotel Schema) ausentes para Google e IA.
- Mantener el patrón narrativo de los demás Quick Wins: `**HOY (5 minutos): {acción}.** → {nota DIY}`.
- La redacción final es ajustable siempre que cumpla las 3 reglas anteriores.

**Criterios de aceptación**:
- [ ] La rama `not hotel_schema_detected` produce texto sobre datos/Schema en Google
- [ ] grep `Corregir el número de WhatsApp` en `modules/` retorna **0 resultados** (AC12)
- [ ] Ninguna otra rama de `_build_quick_wins()` menciona WhatsApp sin condición real

### Tarea 2: Test nuevo

**Archivos afectados**: `tests/commercial_documents/test_diagnostic_generator.py`

Crear `test_quick_wins_schema_text`:
- **Setup**: `audit_result` con `schema.hotel_schema_detected=False` (reusar fixtures/helpers existentes del archivo — ver D8 tests).
- **Assert 1**: el output de quick wins NO contiene "WhatsApp".
- **Assert 2**: el output menciona "Google" y/o "datos" (correspondencia con la condición Schema).
- **Caso complementario**: `hotel_schema_detected=True` → el Quick Win de Schema NO aparece.

### Tarea 3: Verificación de no-regresión + residuos

```bash
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_diagnostic_generator.py tests/test_top_problems_consistency.py tests/regression/ -v
```

- [ ] Suite `test_diagnostic_generator.py` completa pasa (sin regresión D8)
- [ ] `test_top_problems_consistency.py` pasa (no afectado — confirmación)
- [ ] `tests/regression/` pasa (26 tests)
- [ ] grep `Corregir el número de WhatsApp` en `modules/` → 0 resultados

### Tarea 4: Post-ejecución documental

Ver sección **Post-Ejecución** (obligatoria).

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_quick_wins_schema_text` (nuevo) | `tests/commercial_documents/test_diagnostic_generator.py` | Pasa; sin mención de WhatsApp; menciona datos/Google |
| Suite diagnostic_generator | ídem | 0 fallos |
| `test_top_problems_consistency.py` | `tests/test_top_problems_consistency.py` | 0 fallos (función `calculate_quick_winds` distinta, no afectada) |
| Regresión | `tests/regression/` | 26/26 |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_diagnostic_generator.py tests/test_top_problems_consistency.py tests/regression/ -v
```

> NOTA: NO ejecutar la suite completa de 3,360 tests en esta fase (regla de ejecución segura; los archivos patológicos ya están excluidos por el conftest de `tests/commercial_documents/`).

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE (antes de cerrar la sesión):

1. **`dependencias-fases.md`**: marcar FASE-R0-A como ✅ Completada con fecha y notas de ejecución.
2. **`README.md` del plan**: actualizar tabla de progreso (estado + sesión + fecha).
3. **`06-checklist-implementacion.md`**: marcar fila de FASE-R0-A ✅.
4. **`09-documentacion-post-proyecto.md`**:
   - Sección B (Funcionalidades): Quick Win #1 condicionado correctamente a Schema.
   - Sección D (Métricas): +1 test (3,361).
   - Sección E (Archivos): `v4_diagnostic_generator.py`, `test_diagnostic_generator.py`.
5. **`10-analisis-post-implementacion.md`**:
   - Resumen de Ejecución: fila de FASE-R0-A (estado, iteraciones, notas).
   - Lecciones Aprendidas: mínimo 3 (formato: qué pasó / por qué / qué lo previene + INCLUIR/EXCLUIR).
   - Matriz de Verificación: fila B2 con estado del fix.
6. **Evidencia**: no aplica (sin output de comandos largos).
7. **Registrar la fase** (executor §2.5 — anti-deuda, NO delegar a RELEASE):

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-R0-A \
    --desc "Fix B2: Quick Win #1 texto corresponde a condicion hotel_schema (sin WhatsApp)" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py" \
    --tests "1" \
    --check-manual-docs
```

> **SIN flag `--release`** (check "Prompts No Release" de `run_all_validations.py`).

8. **Validación final**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```
> Si fallan los checks "Version Sync" o "Document Integration": son issues de sincronización documental, NO de código. Resolver con `./venv/Scripts/python.exe scripts/sync_versions.py` y re-validar. NO re-ejecutar suites de tests para "arreglarlos".

9. **Regenerar DOMAIN_PRIMER** (estándar por cierre de fase):
```bash
./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer
```

---

## Criterios de Completitud (CHECKLIST)

⚠️ Verificar ANTES de marcar como ✅ COMPLETADA ⚠️

- [ ] Test nuevo `test_quick_wins_schema_text` pasa
- [ ] Suites obligatorias pasan (test_diagnostic_generator + test_top_problems_consistency + regression)
- [ ] grep "Corregir el número de WhatsApp" en `modules/` = 0 resultados (AC12)
- [ ] `log_phase_completion.py` ejecutado (SIN `--release`) y registrado en REGISTRY.md
- [ ] `dependencias-fases.md`, `README.md`, `06-checklist`, `09`, `10` actualizados
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Ninguna mención de WhatsApp introducida/alterada en el template o el proposal generator (fuera de alcance de esta fase)

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- Máximo 60 iteraciones del agente (R2). Si se alcanza: marcar fase `⏳ INCOMPLETA` con checkpoint y cerrar sesión.
- **NO ejecutar `v4complete`** (reservado exclusivamente a FASE-R0-E — única ejecución del plan).
- NO modificar el template `diagnostico_v6_template.md` ni `v4_proposal_generator.py` (fases R0-B/C/D).
- NO bump de versión, NO entrada nueva en CHANGELOG.md (reservado a FASE-RELEASE-4.72.1).
- NO modificar pain_ledger, publication gates ni lógica de datos.
- NO ejecutar la suite completa de tests (3,360) — solo los archivos especificados.
- `log_phase_completion.py` SIN `--release`.
