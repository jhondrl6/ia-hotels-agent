# FASE-P1-C: Cap de Plausibilidad (F6) + Trazabilidad del Rango Hook→Express (F11)

**ID**: CREDIBILIDAD-NUMERICA-2026-08-20 / FASE-P1-C
**Objetivo**: (1) Cablear la generación del rango del hook al benchmark master de P1-A —causa
raíz de F6: hoy usa defaults hardcodeados—, (2) acotar el rango resultante con un cap de
plausibilidad (F6) y (3) implementar el mecanismo de trazabilidad que verifica que la cifra del
Express caiga dentro del corredor prometido por el Hook y genere la narrativa de la delta
benchmark→dato real (F11). **El cap sin cableado acotaría un rango fabricado** (decisión D4 del
plan-maestro §7).
**Dependencias**: FASE-P1-B ✅ (benchmarks estables + OTA parametrizada)
**Duración estimada**: 1 sesión (≤60 iteraciones)
**Skill**: `phased_project_executor.md` (ejecución DIRECTA — decisión arquitectónica)

## Modo de Ejecución

**DIRECTO con el agente principal.** Diseñar el cap de plausibilidad y la trazabilidad del rango
como una promesa falsable requiere entender el flujo Hook→Express completo (`two_phase_flow.py`,
`hook_pdf_generator.py`, consistency checker). El CONTEXT §6.6 establece que "el cap de plausibilidad
y la trazabilidad del rango son dos mitades del mismo fix".

## Contexto

CONTEXT §2 fallos **F6** y **F11**, y §6.3 (acción propuesta vinculada a P1 acción 8):
- **F6**: Rango del hook 23x entre extremos ("entre $453.600 y $10.631.250 COP mensuales") —
  inverosímil comercialmente, invita descrédito. **Causa raíz verificada en código vivo**: la
  estimación del hook usa `_get_regional_benchmarks` (two_phase_flow.py L215-230), que devuelve
  `default_benchmarks` hardcodeados (min_rooms 15, max_rooms 50, min_adr 120000...) cuando
  `plan_maestro_data` está vacío — y `OnboardingController.__init__` (onboarding_controller.py
  L58-61), único caller productivo, NO lo pasa, aunque el constructor de `TwoPhaseOrchestrator`
  YA acepta el parámetro (L93): falta el cableado. Además `regions.get(region, default_benchmarks)`
  (L230) exige alinear las keys de región del master.
- **F11**: Ningún mecanismo valida que la cifra del Express caiga dentro del rango prometido por
  el Hook, ni genera la narrativa de la delta (benchmark → dato real). El rango del Hook se trata
  como marketing unidireccional, no como promesa falsable que el producto pagado debe cumplir.

**Insight estructural** (CONTEXT §6.3): la única función comercial real del rango del Hook es ser
validado por el Express (transacción promesa→cumplimiento que sostiene el modelo de 3 niveles).
Un rango que nunca se cierra es marketing decorativo. El cap existe para que el rango sea falsable
por el Express.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-P0-A/B/C | ✅ Completadas |
| FASE-P1-A | ✅ Completada |
| FASE-P1-B | ✅ Completada |

### Base Técnica Disponible
- `modules/orchestration_v4/two_phase_flow.py` (flujo Hook → Validación;
  `_get_regional_benchmarks` L215-230; constructor L93 ya acepta `plan_maestro_data`)
- `modules/orchestration_v4/onboarding_controller.py` (L58-61: instanciación SIN
  `plan_maestro_data` — punto exacto del cableado)
- `modules/commercial_documents/hook_pdf_generator.py` (`fuga_minima`/`fuga_maxima`)
- `data_validation/consistency_checker.py` (FASE 4.6: whatsapp/gbp/schema/adr)
- Escenarios financieros con percentiles conservador/realista/optimista
- Benchmark master de FASE-P1-A (fuente de valores reales para el rango)

## Tareas

### T1: Cablear el benchmark master a la generación del rango del hook (D4 — PRIMERO)
**Objetivo**: que el rango del hook se calcule con los valores del benchmark master de P1-A en
vez de los defaults hardcodeados de `_get_regional_benchmarks` (min_adr 120000, etc.).
**Pasos**:
- `OnboardingController` (onboarding_controller.py L58-61) carga el master de P1-A y lo pasa a
  `TwoPhaseOrchestrator(plan_maestro_data=...)` — el parámetro YA existe en el constructor (L93)
- Alinear las keys de región: `regions.get(region, default_benchmarks)` (L230) debe resolver con
  las keys del master (incluido el manejo de región sin match)
**Criterios de aceptación**:
- [ ] Con master presente, el rango del hook usa sus valores (verificado por test)
- [ ] Sin master, cae a defaults conservadores documentados (comportamiento actual, explícito)
- [ ] Región sin match en el master NO produce rango 23x por accidente de key (ej. 'colombia')

### T2: Diseñar e implementar el cap de plausibilidad (F6)
**Objetivo**: acotar el rango ya cableado para que no sea inverosímil (ratio max/min razonable).
**Decisión a documentar** (10-analisis-post-implementacion.md, decisión D7):
- ¿Cap percentil (ej. P95 del escenario optimista) o ratio fijo (ej. max/min ≤ 5x)?
- ¿Dónde se aplica el cap: en la generación del hook message o en el cálculo de escenarios?

**Archivos afectados**:
- `modules/orchestration_v4/two_phase_flow.py` (generación del hook message, ya cableado en T1)
- Posiblemente `modules/financial_engine/scenario_calculator.py` (si el cap se aplica en escenarios)

**Criterios de aceptación**:
- [ ] Rango del hook acotado (ratio max/min ≤ umbral definido, ej. 5x o 8x)
- [ ] El cap es configurable (no hardcodeado)
- [ ] El hook message muestra el rango acotado

### T3: Implementar trazabilidad del rango Hook→Express (F11)
**Objetivo**: mecanismo que verifica que la cifra del Express caiga dentro del corredor prometido
por el Hook y genere una sección de trazabilidad: *Hook estimó X con benchmarks → el hotel reportó
ADR/ocupación reales → resultado Z*.

**Archivos afectados**:
- `modules/orchestration_v4/two_phase_flow.py` (disclaimer que promete "cálculo preciso")
- `modules/commercial_documents/hook_pdf_generator.py` (`fuga_minima`/`fuga_maxima` sin consumo posterior)
- Posiblemente `data_validation/consistency_checker.py` (nuevo check de continuidad hook→express)

**Criterios de aceptación**:
- [ ] Al ejecutar el Express para un hotel que recibió Hook, se verifica que la cifra cae dentro
      del corredor prometido (o se documenta por qué no)
- [ ] Se genera una sección de trazabilidad del rango en el output del Express
- [ ] La narrativa de la delta explica la corrección benchmark → dato real

### T4: Tests de contrato anti-regresión
**Criterios de aceptación**:
- [ ] Test cableado: con master presente, el rango usa sus valores (no los defaults 120000+)
- [ ] Test F6: rango del hook acotado (ratio max/min ≤ umbral)
- [ ] Test F11: trazabilidad del rango genera sección con delta benchmark→real
- [ ] Suite `tests/orchestration_v4/` sin fallos NUEVOS vs línea base (§6 del 01-plan-maestro)

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Cap plausibilidad | `tests/orchestration_v4/test_hook_plausibility_cap.py` (nuevo) | Contrato F6 pasa |
| Trazabilidad rango | `tests/orchestration_v4/test_hook_express_traceability.py` (nuevo) | Contrato F11 pasa |

**Comando de validación**:
```powershell
.\venv\Scripts\python.exe -m pytest tests/orchestration_v4/ -v
.\venv\Scripts\python.exe scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. `dependencias-fases.md` y `06-checklist-implementacion.md`: marcar FASE-P1-C ✅.
2. `README.md` del plan: actualizar tabla de progreso.
3. `09-documentacion-post-proyecto.md`: secciones A/B/D/E.
4. `10-analisis-post-implementacion.md`: fila de ejecución + mínimo 3 lecciones + decisión del cap documentada.
5. **Registrar la fase**:
```powershell
.\venv\Scripts\python.exe scripts/log_phase_completion.py --fase FASE-P1-C --desc "Cableado benchmark master al hook (F6 causa raiz, D4) + cap plausibilidad (F6) + trazabilidad rango Hook-Express (F11)" --archivos-mod "modules/orchestration_v4/two_phase_flow.py,modules/orchestration_v4/onboarding_controller.py,modules/commercial_documents/hook_pdf_generator.py" --tests "<N>" --check-manual-docs
```
6. Editar CHANGELOG.md y GUIA_TECNICA.md (template §6).

## Criterios de Completitud (CHECKLIST)

- [ ] Rango del hook cableado al benchmark master (verificado por test)
- [ ] Rango del hook acotado por el cap (verificado por test)
- [ ] Trazabilidad del rango genera narrativa de delta (verificado por test)
- [ ] Suite orchestration_v4 sin fallos NUEVOS vs línea base (§6)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Post-ejecución completada

## Restricciones

- Máximo 60 iteraciones.
- NO modificar benchmarks ni fallback de región (ya cerrados en P1-A y P1-B).
- NO modificar la comisión OTA (cerrada en P1-B; si two_phase_flow.py necesita el valor del
  rango OTA para el cap, consumirlo de config — no hardcodear).
- NO modificar la verdad del sitio vivo (es FASE-P1-D).
- NO ejecutar v4complete.
