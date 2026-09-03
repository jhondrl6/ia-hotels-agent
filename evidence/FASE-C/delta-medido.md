# FASE-C — Delta medido (C4)

Experimento contrafactual: el **mismo corpus real** (Salento Real, corrida
`2026-08-31T12:28:03`, `output/FASE-D_salentoreal_post_guard/`) reprocesado con
el código vivo antes y después de FASE-C. No es una simulación con datos
inventados: `pain_ledger_resolved.json`, `asset_generation_report.json` y
`coherence_validation.json` del run real alimentan
`evidence/FASE-C/faseC_contrafactual.py`, que llama a las funciones de
producción (`PainSolutionMapper.map_to_solutions`,
`V4AssetOrchestrator._solutions_to_asset_specs`,
`CoherenceValidator._check_assets_are_justified`, `AssetAlignmentMatrix.build`,
`AlignmentResult.from_asset_alignment_matrix`).

- Antes: `evidence/FASE-C/faseC_antes.txt`
- Después: `evidence/FASE-C/faseC_despues.txt`
- Rojo TDD previo al fix: `evidence/FASE-C/tdd-comportamiento-ROJO.txt`,
  `evidence/FASE-C/tdd-colecta-ROJO.txt`

## 1. Las cinco cifras

| # | Magnitud | Antes | Después | AC |
|---|----------|-------|---------|-----|
| 1 | `no_breach` | **6** | **0** | AC5 |
| 2 | `promised_services_total` | 7 | 1 | AC5 |
| 3 | `actionable_total` | 1 | 1 | AC5 |
| 4 | `assets_are_justified` | 0.75 · `passed=False` · `severity=error` | **1.0** · `passed=True` · `severity=info` | AC6 |
| 5 | `is_coherent` | **False** (`overall=0.88`, `errors=[assets_are_justified]`) | **True** (`overall=0.9133`, `errors=[]`) | AC6 |

Umbral de coherencia: **0.8, sin tocar**. AC6 se cierra por la vía del punto 8
(la promesa deja de incluir lo que no se promete por brecha), no relajando el
gate.

## 2. AC5 — la convergencia de denominadores

Antes: `total = 7`, `no_breach = 6`, `actionable = 7 − 6 = 1`, `coverage = 1/1 =
1.000`. El `1.000` era algebraico: el denominador se construía restando lo que
el propio numerador había descartado.

Después: `total = 1`, `no_breach = 0`, `actionable = 1 − 0 = 1`, `coverage =
1/1 = 1.000`.

**`total == actionable` ahora es una identidad estructural, no una resta que se
anula.** `no_breach` no bajó de 6 a 0 por filtrado: la categoría dejó de
emitirse cuando hay ledger resuelto, porque un servicio sin brecha y sin
presencia simplemente no se promete (Punto 8).

Invariante verificado en el run: `effective_total + unresolved + no_breach ==
promised_services_total` → `1 + 0 + 0 == 1` ✔ (y fijado como identidad, no como
valor, en `tests/asset_generation/test_fase_c_propuesta_dinamica.py`).

### Lo que este run NO demuestra

`coverage_ratio` sigue en `1.000`. No es la misma cifra que antes, pero tampoco
es prueba de que el coverage discrimine: este hotel tiene **una sola brecha
mapeable a servicio** (`ai_crawler_blocked` → `llms_txt`) y la cubre, así que
`1/1` es verdadero y no tautológico. Que el ratio *discrimine* se demuestra en
el caso negativo, que sí está testeado: con la brecha de `hotel_schema` presente
y su asset ausente, `coverage = 0.5` y `unresolved = 1`
(`test_brecha_sin_asset_generado_es_deuda_visible`). La corrida C de
`test_alignment_result.py` da `3/4 = 0.75` con `no_breach = 0`.

Las otras dos brechas del run (`no_analytics_configured`,
`low_organic_visibility`) no son servicios del catálogo: son los dos huérfanos
del contrato §3 (S-C2). Siguen generándose y siguen fuera del recuento de
servicios; FASE-C no los convirtió en servicio comercial.

## 3. AC6 — la causa real no era la que decía el dossier

El dossier §9.2 (B5) atribuía el `is_coherent=false` estructural a los dos
cerrojos de `promised_assets_exist`. **Medido: falso.** Ese check pasa en 1.0
tanto antes como después (ver §5). El mecanismo real:

1. `_solutions_to_asset_specs` (`v4_asset_orchestrator.py`) añade por D4-FIX los
   assets con `promised_by=["always"]`, entre ellos `monthly_report`, con
   `pain_ids=[]`.
2. `_check_assets_are_justified` hace `any(pid in problem_ids for pid in
   asset.pain_ids)`: con `pain_ids=[]` el `any()` es **siempre** False.
3. Ese asset nunca puede justificarse ⟹ `3/4 = 0.75 < 0.8` ⟹ `passed=False`,
   `severity="error"` ⟹ `errors` no vacío ⟹ `is_coherent=False` **en toda
   corrida**, independientemente del hotel.

Es el mismo defecto conceptual que AC5, en la tercera superficie de promesa:
contar como "prometido por brecha" algo que se entrega por modelo de servicio.
El fix excluye del denominador los complementos siempre-activos, derivados del
registro canónico (`ALWAYS_ACTIVE_COMPLEMENT_ASSETS`, proyección de
`counts_in_alignment=False`), no listados a mano. Los dientes quedan: un asset
sin `pain_id` que **no** sea complemento sigue restando
(`test_asset_sin_pain_que_no_es_complemento_sigue_restando`, score 0.5,
`passed=False`).

Es la tercera aplicación en este plan de *"revalidar citas de código no
revalida premisas"*: la cita era correcta, la premisa no.

## 4. vacío ≠ ausente

Tres sitios colapsaban un ledger **vacío** (resuelto, 0 brechas) con un ledger
**ausente** (sin fuente). Los tres corregidos:

| Sitio | Antes | Después |
|---|---|---|
| `publication_gates.py` extracción | `assessment.get("pain_ledger") or []` | `assessment.get("pain_ledger")` |
| `publication_gates.py` derivación | `if pain_ledger:` | `if pain_ledger is not None:` |
| `v4_proposal_generator.py:1201` | `if not pain_ledger: return None` | `if pain_ledger is None: return None` |

Semántica resultante: `None` → catálogo estático legacy (7 servicios,
`NO_BREACH` donde no haya pain); `[]` → 0 servicios comprometidos, los 7
declarados en `not_promised`. Testeado en ambos sentidos
(`test_gate_empty_ledger_is_not_static_catalog`,
`test_committed_empty_ledger_is_not_legacy`,
`test_ledger_ausente_conserva_catalogo_estatico`).

Este cambio **no** cierra la escotilla V9 (0 comprometidos → PASS trivial):
`C1 DEFINE, G4 IMPLEMENTA`. FASE-C sólo garantiza que el PASS trivial ya no se
dispara por confusión entre vacío y ausente.

## 5. Límite P12/A3 — declarado, no ocultado

`promised_assets_exist` **no puede certificar nada en post-generación**:

- `coherence_validator.py:670` acota el cross-check estático con
  `if not generated_assets:` (comentario H6 FIX), así que con assets reales el
  bucle sobre `PROPOSAL_SERVICE_TO_ASSET` no se ejecuta.
- `coherence_validator.py:689-700` hardcodea `score=1.0` en la rama de éxito.

Medido en el run: `passed=True score=1.0` con mensaje *"7 servicios verificados
via PROPOSAL_SERVICE_TO_ASSET"* — un 7 que FASE-C ya no emite en la matriz. El
mensaje cita el catálogo estático, no la promesa dinámica. **Ninguna de las dos
ACs se apoya en este check**; se reporta como límite y como deuda: el mensaje
quedó desincronizado de la propuesta dinámica y su score post-gen no es
verificable. Se registra como **S-C3** para FASE-G/F.

## 6. Regresión introducida y corregida dentro de la fase

Pasar `site_presence_report` al `AssetAlignmentMatrix.build` del gate sin pasarlo
a la construcción equivalente del delivery report **rompió AC3** (los dos
reportes del mismo run volvieron a divergir: `effective_total` 3 vs 2,
`coverage` 0.75 vs 0.667). Lo expuso
`test_alignment_contract.py::test_gate_matches_delivery_report_same_run`.
Corregido construyendo ambas rutas con los mismos insumos; la presencia ahora se
resuelve **dentro** de la partición canónica, así que un servicio comprometido
por presencia nace `PRESENT_IN_PRODUCTION` en la matriz en vez de nacer
`NO_BREACH` y ser re-clasificado después por el DTO.

## 7. Superficies de promesa: estado al cierre

El contrato §1.1 identificó tres superficies que prometían en estático:

| Superficie | Estado |
|---|---|
| Tabla de servicios de la propuesta | Ya era dinámica (FASE-SR-B / D-PF1). Sin cambio. |
| Matriz `proposal_asset_matrix.json` + gate | **Dinámica** (FASE-C). `no_breach=0`, `not_promised` publicado en el JSON. |
| Lista de assets entregada a coherencia | **Dinámica** (FASE-C). Complementos fuera del denominador. |
| Tabla de assets técnicos (`TECHNICAL_ASSET_CATALOG`) | **Sigue estática.** Fuera del alcance ejecutado → S-C4. |

## 8. Baselines de tests

| Conjunto | Antes de FASE-C | Después |
|---|---|---|
| `tests/asset_generation` + `tests/quality_gates` | 872 passed, 2 skipped | **892 passed, 2 skipped** |
| `tests/` completo salvo `tests/commercial_documents` | 14 failed, 9 errors (pre-existentes) | 14 failed, 3348 passed, 32 skipped, 9 errors |

Delta +20 = 17 tests nuevos de contrato (`test_fase_c_propuesta_dinamica.py`) +
3 netos añadidos al actualizar los existentes.

Los 14 failed / 9 errors del árbol ancho **no son de FASE-C**: se verificó
reproduciéndolos con `git stash` de `modules/` sobre HEAD. Son
`test_gate_presence_with_skipped_assets`, `test_cop_cop_regression`
(`publication_gates.py:170`, comentario con el literal "COP COP", fuera de mis
hunks 982/997/1007), `test_proposal_alignment`, `test_evidence_tier`,
`test_diagnostic_geo_metrics`, `test_pricing_resolution_wrapper` y los e2e de
onboarding (`output/clientes/donalfonsohotel_onboarding.yaml` inexistente).
