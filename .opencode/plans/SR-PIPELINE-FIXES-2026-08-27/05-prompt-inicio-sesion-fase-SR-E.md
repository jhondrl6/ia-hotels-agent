# FASE-SR-E — Preflight `hotel_schema`: Confianza desde Fuentes Disponibles

**ID**: FASE-SR-E
**Objetivo**: Resolver la paradoja del pain #1 (H4/N4, L-SR4): con 0 schemas detectados y GBP completo, el asset `hotel_schema` DEBE generarse vía el fallback declarado del catálogo. Separar "confianza en los datos de entrada" de "confianza en la implementación del asset": para brechas de ausencia, la confianza se calcula desde las fuentes disponibles para CONSTRUIR el asset (GBP/web), no desde la presencia de la brecha.
**Dependencias**: FASE-SR-D ✅ (orden del plan; SR-E PRIMERO que SR-F — mismo archivo `pain_solution_mapper.py`).
**Complejidad**: Media-Alta · **Delegación**: ❌ DIRECTO (decisión de semántica de confianza + contrato con catálogo)
**Duración estimada**: 60 min · **Presupuesto**: ~22 iteraciones trabajo + ~15 verificación/docs (R2: máx. 60)

## Reglas de Sesión (MANDATORIO)

- R1: Una fase por sesión. R2: máx. 60 iteraciones (checkpoint + evidencia si se agota). R3: 4 tareas + 0 comandos largos.
- Python: `./venv/Scripts/python.exe`.

## Contexto

**Lectura previa obligatoria**: CONTEXT-SALENTOREAL §5 (H4), §9.5.2 N4, §8.2 L-SR4, §9 #4 y #11 + plan maestro §8.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-SR-A…SR-D | ✅ Completadas |

### Base Técnica Disponible (N4 verificado contra código vivo)
- `modules/commercial_documents/pain_solution_mapper.py:889`: `reason=f"...Insufficient confidence ({avg_confidence:.2f} < {min_confidence})"` — el preflight de confianza que mató la generación en corrida C (`hotel_schema: Insufficient confidence (0.00 < 0.8)`).
- `modules/asset_generation/asset_catalog.py:92-98`: `hotel_schema` declara `fallback="generate_basic_schema"`, `block_on_failure=False` → el catálogo DICE "puedo generar desde GBP". Dos contratos contradictorios para el mismo asset (N4): el preflight lo bloquea antes de que el fallback opere. **Decisión D-PF3: el contrato del catálogo gana — nunca ambos criterios.**
- Evidencia corrida C: pain #1 `no_hotel_schema` (score 85, HIGH, $1.06M COP/mes); audit = 0 schemas; asset NO generado; `coherence_validation.json` check `promised_assets_exist` FAILED ("Assets no implementados: hotel_schema"); `pain_ledger_resolved.json`: `no_hotel_schema` = DETECTED, `mapped_to_service: 0`, `justified_skip: 0`.
- Datos GBP disponibles para construir el schema: nombre, dirección, rating 4.5, 984 reseñas, teléfono (todos presentes). Nota: `geo_enriched/hotel_schema_rich.json` y `faq_schema.json` sí se generan en la rama GEO pero NO cuentan como asset `hotel_schema` para ningún gate.

## Tareas

### T1: Investigar el flujo preflight ↔ catálogo ↔ coherence_validator
**Archivos**: `pain_solution_mapper.py` (cálculo de `avg_confidence` y `min_confidence`), `asset_catalog.py` (contrato `fallback`/`block_on_failure`), `modules/commercial_documents/coherence_validator.py` (`_check_promised_assets_exist`, L543/611), orquestador de preflight (linker/orchestrator — localizar el caller de la decisión 0.00 < 0.8).
**Criterios**:
- [ ] Mapa: de dónde sale `avg_confidence` para `hotel_schema` (por qué es 0.00 con 0 schemas) y dónde se consulta `min_confidence`
- [ ] Confirmar cómo el catálogo expone `fallback`/`block_on_failure` y quién debería consumirlo

### T2: Implementar D-PF3
**Criterios**:
- [ ] Para brechas de **ausencia** (pain "no existe X"), la confianza del asset se calcula desde las fuentes disponibles para construir X (GBP completo → confianza alta; sin GBP y sin web → confianza baja, comportamiento previo)
- [ ] El preflight respeta `fallback` + `block_on_failure=False` del catálogo: si hay fallback disponible, NO bloquea por confianza de datos de entrada
- [ ] Consistencia con SR-B: un asset generado vía fallback cuenta como LINKED/GENERATED en la matriz y en el gate (un solo criterio)
- [ ] Sin invención: si no hay fuentes para construir el asset, el comportamiento de bloqueo se mantiene (con `justified_skip` trazable)

### T3: Tests (2 casos opuestos)
**Criterios**:
- [ ] Test caso Salento Real: 0 schemas + GBP completo (nombre/dirección/rating/teléfono) → asset `hotel_schema` GENERADO; `no_hotel_schema` = ASSET_GENERATED en pain_ledger; `promised_assets_exist` sin "Assets no implementados"
- [ ] Test caso sin fuentes: 0 schemas + sin GBP → sin generación, sin invención, `justified_skip` documentado
- [ ] Test de consistencia: el asset por fallback satisface `promised_assets_exist`
- [ ] Tests de regresión de pain_solution_mapper y coherence_validator (archivos específicos)

### T4: Greps + docs
**Criterios**:
- [ ] Grep: 0 residuos del criterio "confianza desde presencia de la brecha" para assets con fallback
- [ ] Grep: 0 referencias a `generate_basic_schema` sin su consumidor del preflight (el fallback pasa a estar cableado)

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| caso Salento Real | tests de `tests/commercial_documents/test_pain_solution_mapper*.py` (específicos) | asset generado + ASSET_GENERATED |
| caso sin fuentes | ídem | bloqueo mantenido + justified_skip |
| consistencia promised_assets_exist | tests del coherence_validator | sin "Assets no implementados" |

**Comandos** (procesos aislados, salida a archivo):
```bash
./venv/Scripts/python.exe -m pytest tests/commercial_documents -k "mapper or schema" -v > temp/fase_sr_e_tests1.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/asset_generation -k "catalog or preflight" -v > temp/fase_sr_e_tests2.txt 2>&1
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO — antes de cerrar la sesión)

1. `dependencias-fases.md` §2 → ✅. 2. `README.md` → ✅. 3. `06-checklist` → SR-E. 4. `09-documentacion` → B/D/E + Notas. 5. `10-analisis` → Resumen + D-PF3 confirmada/ajustada + lecciones. 6. `evidence/FASE-SR-E/` → diff + tests. 7. Registro (SIN `--release`):
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-SR-E --desc "Preflight hotel_schema: confianza desde fuentes disponibles (GBP/web); respeta fallback del catalogo" --archivos-mod "modules/commercial_documents/pain_solution_mapper.py" --tests "<N reales>" --check-manual-docs
```
8. `./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer`

## Criterios de Completitud (CHECKLIST)

- [ ] Tests de los 2 casos pasan; regresiones = 0
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] D-PF3 implementada (contrato del catálogo gana; sin doble criterio)
- [ ] Docs post-fase completos (1-8)
- [ ] Evidencia en `evidence/FASE-SR-E/`

## Restricciones

- Máx. 60 iteraciones; NO ejecutar v4complete/v4audit.
- NO modificar `asset_catalog.py` (el contrato del catálogo es la fuente — se consume, no se reescribe).
- NO bajar el umbral global 0.8 (enmascara el problema semántico — D-PF3).
- NO tocar la rama GEO existente (`geo_enriched/hotel_schema_rich.json`) — esta fase trata el asset del catálogo.
- NO delegar a subagente; NO usar `--release` en log_phase_completion.
- AC10: capa financiera intacta.
