# FASE-4: Tests E2E (H4) + v4complete Hotel Don Alfonso + Análisis Post-Implementación

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: MIXTO (delegate_task para tests + terminal background para v4complete)

## Contexto previo

FASE-1 completada: harness recibe y respeta ADR + occupancy del onboarding.
FASE-2 completada: proposal generator usa ADR del onboarding; ValidationSummary deriva confidence de fuente real.
FASE-3 completada: taxonomía unificada; CTAs condicionados a has_onboarding.

Estado: todos los fixes de código están aplicados. Quedan tests e2e + verificación con v4complete.

## Objetivo de esta fase

1. Escribir tests e2e que cierren el pipeline: YAML → harness → JSON → documento
2. Ejecutar v4complete para Hotel Don Alfonso con onboarding y verificar que los fixes fueron superados
3. Generar el análisis post-implementación (08-analisis-post-implementacion.md)

### Tareas

- [ ] 4.1 Tests e2e: YAML → harness → JSON (delegate_task)
  - Test: cargar YAML de onboarding de Don Alfonso → construir payload → ejecutar handler → verificar adr_cop=330000 en result_data
  - Test: verificar occupancy_rate=0.4242 en result_data (no 0.512)
  - Test: verificar adr_source != "handler" en result_data
  - Test: verificar que ValidationSummary no tiene confidence=VERIFIED cuando value no vino del onboarding
  - Ubicación: `tests/e2e/test_onboarding_to_harness_pipeline.py` (nuevo archivo)

- [ ] 4.2 Ejecutar v4complete para Hotel Don Alfonso
  - URL: https://www.donalfonsohotel.com/
  - Onboarding YAML: `output/clientes/donalfonsohotel_onboarding.yaml` (ya existe)
  - Comando: `python3 main.py v4complete https://www.donalfonsohotel.com/ --timeout 900`
  - Timeout: 900s (v4complete toma 5-10 min)
  - Guardar output: log, JSON, diagnóstico, propuesta, gate_report

- [ ] 4.3 Análisis post-implementación: comparar cifras esperadas vs reales
  - Leer el JSON de financial_scenarios generado
  - Verificar: adr_cop == 330000 (no 420000)
  - Verificar: occupancy_rate == 0.4242 (no 0.512)
  - Verificar: adr_source != "handler"
  - Leer el diagnóstico: verificar que CTA "Complete el onboarding" NO aparece
  - Leer la propuesta: verificar que ADR == $330,000 COP (no $420,000)
  - Verificar consistencia ADR entre diagnóstico y propuesta (mismo valor)

- [ ] 4.4 Llenar 08-analisis-post-implementacion.md
  - Tabla de ejecución (fase, sesión, status, delegate_task usado)
  - Tabla de cifras esperadas vs reales (todas las métricas del §8 del plan maestro)
  - Análisis de fase de mayor complejidad (FASE-2): mitigaciones aplicadas, resultado
  - Veredicto: ¿los 3 bugs + 4 hallazgos fueron superados?

### Restricciones

- v4complete requiere terminal background con notify_on_complete=true y timeout=900s
- NO modificar código en esta fase (solo tests + verificación)
- Si v4complete falla por reasons unrelated (timeout, network), documentar y no reintentar en esta sesión
- Los 55 tests preexistentes que fallan NO son regressión — no intentar fixearlos

### Criterios de completitud

- [ ] Nuevo archivo `tests/e2e/test_onboarding_to_harness_pipeline.py` existe y pasa
- [ ] v4complete ejecutado para Hotel Don Alfonso (log guardado)
- [ ] JSON muestra adr_cop=330000, occupancy_rate=0.4242, adr_source!="handler"
- [ ] Diagnóstico NO muestra CTA "Complete el onboarding"
- [ ] Propuesta muestra ADR=$330,000 COP (consistente con diagnóstico)
- [ ] 08-analisis-post-implementacion.md completado con tabla de cifras esperadas vs reales
- [ ] Commit: `test(H4): e2e onboarding pipeline + v4complete Don Alfonso verification`

### Próxima sesión

FASE-5: RELEASE — version bump, CHANGELOG, docs cascade, pre-commit.

---

## Prompt para delegate_task (tests e2e — auto-contenido)

```
Eres un subagento que trabaja en el proyecto iah-cli en /mnt/c/Users/Jhond/Github/iah-cli.

OBJETIVO: Escribir tests e2e que cierren el pipeline onboarding → harness → JSON → documento.

CONTEXTO TÉCNICO:
- El archivo output/clientes/donalfonsohotel_onboarding.yaml contiene datos del Hotel Don Alfonso
- Datos esperados: rooms=11, adr_cop=330000, occupancy_rate=0.4242, direct_channel=30.0, region=eje_cafetero
- FASE-1: el payload del harness ahora incluye user_provided_adr y occupancy_source
- FASE-2: ValidationSummary deriva confidence de adr_source real
- FASE-3: taxonomía unificada, CTAs condicionados

TESTS A ESCRIBIR en tests/e2e/test_onboarding_to_harness_pipeline.py:

1. test_onboarding_yaml_loads_correctly:
   - Cargar output/clientes/donalfonsohotel_onboarding.yaml
   - Verificar datos_operativos.valor_reserva_cop == 330000
   - Verificar datos_operativos.occupancy_rate == 0.4242

2. test_harness_receives_onboarding_adr:
   - Simular la construcción del payload como lo hace main.py
   - Verificar que el payload incluye "user_provided_adr": 330000
   - Verificar que el payload incluye "occupancy_source": "onboarding"

3. test_handler_returns_onboarding_adr:
   - Ejecutar harness_handlers con payload que incluye user_provided_adr=330000
   - Verificar result_data["adr_cop"] == 330000
   - Verificar result_data["adr_resolution"]["source"] == "user_provided"

4. test_handler_respects_onboarding_occupancy:
   - Ejecutar harness_handlers con payload occupancy_rate=0.4242, occupancy_source="onboarding"
   - Verificar que result_data no sobrescribe occupancy con 0.512

5. test_validation_summary_confidence_matches_source:
   - Si adr_source == "user_provided": confidence debe ser VERIFIED
   - Si adr_source == "regional_v410": confidence debe ser ESTIMATED
   - confidence=VERIFIED solo cuando el value realmente vino del onboarding

6. test_json_adr_source_not_handler:
   - Verificar que adr_source en el JSON no es "handler" (placeholder muerto)

UBICACIÓN: tests/e2e/test_onboarding_to_harness_pipeline.py (crear archivo nuevo)

VERIFICACIÓN:
- python3 -m pytest tests/e2e/test_onboarding_to_harness_pipeline.py -v --timeout=60

IMPORTANTE: Lee harness_handlers.py y main.py para entender las firmas reales antes de escribir los tests. Los tests deben usar los imports correctos del proyecto.
```
