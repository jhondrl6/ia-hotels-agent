# FASE-1: Root Cause — Propagación de ADR y Occupancy del Onboarding al Harness

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: SUBAGENTE (delegate_task)

## Contexto previo

Sin fases anteriores. Esta es la primera fase del plan BUGS-ONBOARDING-ADR-2026-07-22.

Estado base del código:
- 700 tests pasan, 55 fallan (preexistentes, no relacionados)
- `main.py:1765` extrae `adr_from_onboarding = datos_operativos.get('valor_reserva_cop')` → 330000 ✓
- `main.py:1797-1806` payload del harness NO incluye `user_provided_adr`
- `harness_handlers.py:49` recibe `user_provided_adr = payload.get("user_provided_adr")` → None
- `harness_handlers.py:94` sobrescribe occupancy con regional si `should_use_regional_for(region)=True`
- `main.py:1861` `adr_source = result_data.get("adr_source", "handler")` → placeholder muerto

## Objetivo de esta fase

Corregir la causa raíz: el payload del harness no transporta el ADR ni marca el occupancy como proveniente del onboarding. Después de esta fase, el harness debe recibir y respetar ambos valores.

### Tareas

- [ ] 1.1 Agregar `user_provided_adr` al payload del `AgentTask` financiero en `main.py:~1806`
  - ANTES: payload incluye rooms, region, occupancy_rate, direct_channel_percentage, hotel_id, hotel_name
  - DESPUÉS: payload incluye además `"user_provided_adr": adr_from_onboarding`

- [ ] 1.2 Agregar `occupancy_source` al payload para que el handler no sobrescriba occupancy
  - En `main.py:~1806`: agregar `"occupancy_source": "onboarding" if adr_from_onboarding_verified else "default"`
  - En `harness_handlers.py:91-99`: guardar occupancy del payload antes del bloque `should_use_regional_for`. Si `payload.get("occupancy_source") == "onboarding"`, NO sobrescribir.

- [ ] 1.3 Arreglar `main.py:1861` para leer `result_data["adr_resolution"]["source"]` en lugar del placeholder `"handler"`
  - ANTES: `adr_source = result_data.get("adr_source", "handler")`
  - DESPUÉS: `adr_source = result_data.get("adr_resolution", {}).get("source", "unknown")`

- [ ] 1.4 Verificación: ejecutar test unitario del handler con `user_provided_adr=330000`
  - El handler ya funciona cuando recibe el dato (ver §3.2 del contexto, prueba de fuego)
  - Verificar que `result_data["adr_cop"] == 330000`
  - Verificar que `result_data["adr_resolution"]["source"] == "user_provided"`

### Restricciones

- NO modificar el proposal generator (H1 — eso es FASE-2)
- NO modificar ValidationSummary construction (H3 — eso es FASE-2)
- NO unificar taxonomía de fuentes (H2 — eso es FASE-3)
- NO agregar tests e2e (H4 — eso es FASE-4)
- Máximo 4 tareas, 0 comandos largos
- Plan line numbers son referencia: siempre grep antes de patchear

### Criterios de completitud

- [ ] `grep "user_provided_adr" main.py` muestra el ADR being passed en el payload del financial_task
- [ ] `grep "occupancy_source" main.py` y `grep "occupancy_source" harness_handlers.py` muestran el flag
- [ ] `grep '"handler"' main.py` no aparece como fallback de adr_source
- [ ] 700 tests preexistentes siguen pasando (no regressión)
- [ ] Commit con mensaje: `fix(BUG-1+NEW-1): propagate ADR+occupancy from onboarding to harness payload`

### Próxima sesión

FASE-2: Cascade fix — proposal generator (H1) + ValidationSummary falsa confianza (H3). Esta es la fase de mayor complejidad técnica.

---

## Prompt para delegate_task (auto-contenido)

```
Eres un subagente que trabaja en el proyecto iah-cli en /mnt/c/Users/Jhond/Github/iah-cli.

OBJETIVO: Corregir la causa raíz de BUG-1 y NEW-1: el payload del harness financiero no transporta el ADR del onboarding ni marca el occupancy como proveniente del onboarding.

CONTEXTO TÉCNICO:
1. main.py:1765 extrae adr_from_onboarding = datos_operativos.get('valor_reserva_cop') → 330000
2. main.py:~1797-1806 construye financial_task = AgentTask(payload={...}) SIN user_provided_adr
3. harness_handlers.py:49 hace user_provided_adr = payload.get("user_provided_adr") → None
4. harness_handlers.py:91-99 sobrescribe occupancy_rate con regional si flags.should_use_regional_for(region)
5. main.py:1861 hace adr_source = result_data.get("adr_source", "handler") → placeholder muerto "handler"
6. main.py:2107 define adr_from_onboarding_verified = adr_from_onboarding is not None and adr_from_onboarding > 0

CAMBIOS REQUERIDOS:

A) En main.py, en el payload del AgentTask financiero (buscar "payload={" cerca de línea 1797-1810, el que incluye "rooms" y "region"):
   - Agregar: "user_provided_adr": adr_from_onboarding,
   - Agregar: "occupancy_source": "onboarding" if adr_from_onboarding_verified else "default",

B) En harness_handlers.py, en el bloque que sobrescribe occupancy (buscar "should_use_regional_for" cerca de línea 91-99):
   - Antes del bloque if flags.should_use_regional_for(region):
   - Agregar: occupancy_source = payload.get("occupancy_source", "default")
   - Envolver el override en: if flags.should_use_regional_for(region) and occupancy_source != "onboarding":

C) En main.py:1861, cambiar:
   adr_source = result_data.get("adr_source", "handler")
   por:
   adr_source = result_data.get("adr_resolution", {}).get("source", "unknown")

VERIFICACIÓN:
- grep "user_provided_adr" en el bloque del financial_task payload en main.py
- grep "occupancy_source" en main.py y harness_handlers.py
- grep '"handler"' main.py — no debe aparecer como default de adr_source
- python3 -m pytest tests/financial_engine/test_adr_resolution_wrapper.py -v --timeout=30
- python3 -m pytest tests/financial_engine/ -v --timeout=60 -x (no debe haber regresión vs los 700 que pasaban)

IMPORTANTE: Los line numbers son referencia y pueden haber driftado. Usa grep para encontrar las ubicaciones reales antes de patchear. Lee cada archivo antes de modificarlo.
```
