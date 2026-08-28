# FASE-SR-B — Unificación Promesa/Matriz/Gate (Fuente Única de Verdad) ⚠️ FASE MÁS COMPLEJA

**ID**: FASE-SR-B
**Objetivo**: Eliminar el bloqueo estructural recurrente de `proposal_asset_alignment` (3ª manifestación: Zione jul-2026 + Salento 18:03 + 18:30) implementando la decisión D-PF1: la propuesta deriva sus servicios prometidos del **pain_ledger + present_in_production** (fuente única), y el gate excluye los estados `NO_BREACH` del denominador de `coverage_ratio`.
**Dependencias**: FASE-SR-A ✅ (helper `compute_unresolved()` + mismo archivo `alignment_result.py`).
**Complejidad**: **MÁXIMA** (§4 del plan maestro) · **Delegación**: ❌ DIRECTO — decisión arquitectónica cross-module, PREVALECE sobre eficiencia (lección DT-3 del executor: un subagente carece del contexto completo de las 4 implementaciones).
**Duración estimada**: 60-90 min · **Presupuesto**: ~25-30 iteraciones de trabajo + ~15 verificación/docs (R2: máx. 60)

## Reglas de Sesión (MANDATORIO)

- R1: Una fase por sesión. R2: máx. 60 iteraciones (si se alcanza → `⏳ INCOMPLETA` + checkpoint + evidencia). R3: 4 tareas + 0 comandos largos.
- Python: `./venv/Scripts/python.exe`.

## Contexto

**Lectura previa obligatoria**: CONTEXT-SALENTOREAL §4 (H3, tabla de 3 capas), §8.2 L-SR3, §9 #1, §9.5.2 N1 + plan maestro §4 (justificación de complejidad) y §8 (restricciones).

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-SR-A | ✅ Completada (helper `AlignmentResult.compute_unresolved()` disponible) |

### Base Técnica Disponible (H3 verificado)
- Las 3 capas con 3 contabilizaciones del mismo hecho (corrida C, 7 servicios):
  1. **RC1** (`modules/commercial_documents/v4_proposal_generator.py`, texto "sin costo (fallback)" en L1248, tabla fallback L1189-1411): promete servicios del **catálogo estático del tier**; declara "sin costo" cuando la brecha candidata no está en `opportunity_scores`.
  2. **Matriz** (`modules/asset_generation/proposal_asset_alignment.py`): respeta la decisión de RC1 (`NO_BREACH`, `pain_ids: []`); el concepto **`actionable` ya existe en L783-789** (excluye NO_BREACH).
  3. **Gate** (`modules/quality_gates/publication_gates.py:862-903` vía `verify_proposal_asset_alignment` en `proposal_asset_alignment.py:159`): **ignora NO_BREACH** y cuenta como `missing` en `coverage_ratio` (3/7 = 0.4286 < 0.80 → BLOCKED).
- La fuente de la promesa (catálogo estático) NO se deriva del pain_ledger; el plan de assets sí. Promesa y plan provienen de fuentes distintas que nadie reconcilia (L-SR3, L-NC10 en capa de gating).
- Fix B7 vigente (REFACTOR-COHERENCIA D-NC7): botón WhatsApp fuera de "Servicios adicionales" sin brecha ni presencia — NO regresar.

## Tareas

### T1: Investigar el contrato actual de las 4 capas
**Archivos**: `v4_proposal_generator.py` (emisión del catálogo + texto fallback), `proposal_asset_alignment.py` (matriz + `actionable`), `publication_gates.py:862-903` (consumo del report), `delivery_quality_report.py` (G9 reconstruido).
**Criterios**:
- [ ] Mapa de consumidores documentado: quién lee qué estado y dónde se calcula `coverage_ratio`
- [ ] Confirmar que SR-A dejó UN solo cálculo de `unresolved` (base de esta fase)

### T2: Implementar la fuente única (D-PF1)
**Criterios**:
- [ ] La propuesta deriva la lista de servicios prometidos del **pain_ledger** (pains con solución mapeada) + **present_in_production** (SitePresence cuenta como cubierto)
- [ ] Servicios sin pain ni presencia NO se prometen como comprometidos (pasan a "adicionales disponibles sin compromiso", respetando B7/D-NC7)
- [ ] El gate calcula `coverage_ratio` sobre el conjunto **`actionable`** (reutiliza el concepto existente; NO_BREACH fuera del denominador)
- [ ] Taxonomía única de estados compartida por propuesta/matriz/gate/G9 (sin criterios paralelos)
- [ ] El mensaje de G9 se deriva del helper único (coherente con coverage_ratio)

### T3: Tests de contrato (L3 — contra fuente dinámica)
**Criterios**:
- [ ] Test de contrato: para un pain_ledger dado, propuesta ↔ matriz ↔ gate reportan estados idénticos por servicio
- [ ] Test escenario corrida C (7 servicios: 2 LINKED, 1 present_in_production, 1 MISSING-con-pain, 3 NO_BREACH): sin fix SR-E, coverage sobre actionable = 3/4 (≥ 0.8 pasa el umbral solo tras SR-E generar hotel_schema — documentar el estado intermedio esperado)
- [ ] Test anti-regresión B7: servicio sin pain ni presencia nunca aparece como comprometido
- [ ] Tests de regresión de las suites tocadas (procesos aislados)

### T4: Greps + docs
**Criterios**:
- [ ] Grep residuos: "sin costo (fallback)" ya no emite promesas comprometidas (o el texto queda explícitamente "sin compromiso, fuera del coverage" — decidir en T2 y documentar)
- [ ] 0 conteos paralelos de coverage/unresolved fuera del helper

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| contrato 3 capas | `tests/quality_gates/` (existente) o nuevo `test_alignment_contract.py` | Estados idénticos propuesta↔matriz↔gate |
| anti-B7 | tests del proposal generator | Sin promesas sin pain/presencia |
| regresión gates | `tests/quality_gates/test_publication_gates*.py` (archivos específicos) | 0 regresiones |

**Comandos** (procesos aislados, salida a archivo):
```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates -k "alignment or proposal" -v > temp/fase_sr_b_tests1.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_v4_proposal_generator_smoke.py -v > temp/fase_sr_b_tests2.txt 2>&1
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```
⚠️ NUNCA correr `pytest tests/commercial_documents` completo (test_proposal_generator.py fuga ~8GB, test_price_consistency.py se cuelga — memoria 2026-08-03).

## Post-Ejecución (OBLIGATORIO — antes de cerrar la sesión)

1. `dependencias-fases.md` §2 → ✅ (con checkpoint). 2. `README.md` del plan → ✅. 3. `06-checklist` → criterios SR-B. 4. `09-documentacion-post-proyecto.md` → B/D/E + Notas. 5. `10-analisis` → fila Resumen + L-PF2 + **decisión D-PF1 confirmada o ajustada con rationale**. 6. `evidence/FASE-SR-B/` → diff + tests. 7. Registro (SIN `--release`):
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-SR-B --desc "Unificacion promesa/matriz/gate: promesa derivada de pain_ledger + present_in_production; NO_BREACH fuera de coverage" --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/asset_generation/proposal_asset_alignment.py,modules/quality_gates/publication_gates.py,modules/quality_gates/delivery_quality_report.py" --tests "<N reales>" --check-manual-docs
```
8. `./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer`

## Criterios de Completitud (CHECKLIST)

- [ ] Tests de contrato pasan; regresiones = 0 en suites tocadas
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] D-PF1 implementada (fuente única; sin criterios paralelos)
- [ ] Docs post-fase completos (1-8 arriba)
- [ ] Evidencia en `evidence/FASE-SR-B/`

## Restricciones

- Máx. 60 iteraciones; NO ejecutar v4complete/v4audit.
- NO modificar `modules/financial_engine/`, detección de pains, ni el fix B7 (D-NC7).
- NO crear una taxonomía/tabla paralela nueva (L-NC10) — reutilizar `actionable`.
- NO delegar a subagente (decisión arquitectónica → directo, lección DT-3).
- NO usar `--release` en log_phase_completion.
- Decisión de diseño: si en T1/T2 aparece un conflicto con D-PF1, documentar la alternativa y SU rationale en `10-analisis` §Decisiones (no improvisar sin registro).
