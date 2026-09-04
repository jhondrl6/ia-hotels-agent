# Dependencias entre Fases — ESTABILIZACION-PRE-TRIBUNAL-2026-09-03

> Grafo de dependencias, conflictos de archivo y reglas de paralelización.
> **R1 del executor**: una fase por sesión. Este archivo existe para que cada sesión sepa qué NO puede
> tocar y qué debe esperar.

> ⚠️ **Regla transversal (L-A6, `10-analisis` §8) — aplica a TODAS las fases**: las citas de **número de
> línea** de este plan pueden estar **desfasadas**. Cada fase que edita código desplaza las líneas que las
> fases posteriores citan, y nadie las re-verifica. Medido al cerrar FASE-A: **4 citas falsas**, la peor
> repetida **12 veces en 6 archivos** (V6 citaba `v4_diagnostic_generator.py:3189-3194`, que ya era la
> llamada a `detect_pains`; el `except Exception: return brechas` real estaba en `:3197-3202`). Las 4
> quedaron corregidas el 2026-09-03, pero la **clase** sigue viva.
>
> **Antes de editar una región citada**: `grep`/`Read` para confirmar que la línea contiene lo que el plan
> dice. Si difiere → editar la región **correcta**, corregir la cita en el plan y registrarlo en
> `10-analisis` §5. **Preferir símbolos** (`def _pain_to_brecha`) sobre números de línea al citar: los
> símbolos no se desplazan.

---

## 0. Estado de ejecución

| Fase | Estado | Fecha | Qué desbloquea ahora |
|------|--------|-------|----------------------|
| **A** | ✅ Completada | 2026-09-03 | **B**, **C** (vía B), **D** — el canónico existe en `modules/common/service_identity.py` |
| **B** | ✅ Completada | 2026-09-03 | **C**, **E**, **H** — biyección triple cerrada (DESCARTE REAL 2→0), candado AST en verde |
| **C** | ✅ Completada | 2026-09-03 | **F**, **G**, **I** — punto 8 implementado: `no_breach = 0` por construcción y `is_coherent` False→True. Código en `c1bf5e2`, corrección de S-B11 en `552c190` |
| **D** | ✅ Completada | 2026-09-03 | **F**, **I** — severidad explícita 11 blocking + 2 advisory con única fuente en `publication_gates.py` |
| **E** | ✅ Completada | 2026-09-03 | **F**, **I** — oráculo persistido (`save_site_presence_snapshot`, passthrough) y `asset_path` poblado para LINKED (causa raíz en el caller de `main.py`) |
| **F** | ✅ Completada | 2026-09-03 | **G**, **H**, **I** — oráculo único (`is_present_in_production` decide y narra; el consumo directo de la partición de C reconciliado con el DTO), `NOT_EVALUATED` ≠ passed con defaults G9 unificados, gate de coherencia respeta `is_coherent` (`coherence_verdict_passes()`, decisión (a): respetar), `publication_state.py` eliminado (H8). Código en `23d0978` |
| **G** | ✅ Completada | 2026-09-04 | **H**, **I** — ceguera de gates cerrada (NR1-NR4): `doc_audit_consistency` cableado con `audit_data` y `NOT_EVALUATED` en datos ausentes, `critical_recall` no vacuo (PageSpeed ERROR + banda GEO critical califican), escotillas V5/V9 cerradas sin revertir BUG-6. Código en `c317cda`. ⚠️ **`pain_solution_mapper.py` NO fue tocado por G** (predicción de la matriz §3 era falsa — G2 vive en `v4_comprehensive.py`) ⟹ **H1/H3 sin orden forzoso real** |
| **H** | ✅ Completada | 2026-09-04 | **I** — los seis quirúrgicos del Nivel 3.8 quedaron cerrados (V6/V7/V8/V11/V13 + **V12 documentado, NO editado** — es decisión OPS). `low_ota_divergence` **sí puede disparar** desde esta fase. ⚠️ **El reparto de §4 era falso**: `pain_solution_mapper.py` y `v4_diagnostic_generator.py` estaban compartidos por dos tracks, así que la delegación se re-partió por **archivos disjuntos** (misma clase de defecto que S-E1 en FASE-E → **L-H2**). Código en el árbol de trabajo de la sesión (el commit lo hace el parent al cerrar) |
| I | ⬜ Pendiente | — | VERIFY |
| VERIFY | ⬜ Pendiente | — | RELEASE |
| RELEASE | ⬜ Pendiente | — | — |

**Notas de ejecución de FASE-A** (relevantes para las fases que heredan sus archivos):

- El canónico vive en **`modules/common/service_identity.py`** (no en `asset_generation/`, como predecía
  `09` §A). Motivo: `modules/common/` no importa nada del proyecto, así que `asset_generation`,
  `commercial_documents` y `financial_engine` pueden consumirlo sin ciclo. **Cualquier fase que necesite
  identidad servicio↔asset↔pain importa de ahí; crear otra tabla es L-NC4 y el guardián AST la detecta.**
- Arquitectura de **dos capas**: Capa 1 = `PainSolutionMapper.PAIN_SOLUTION_MAP` (27 pains, universo de
  pain_id, contenido intacto). Capa 2 = `SERVICE_IDENTITIES` (8 entradas). Ningún registro puede declarar
  un pain_id ausente de Capa 1 — eso es lo que fijan los contract tests.
- `PROPOSAL_SERVICE_TO_ASSET` es ahora **derivado** y su **orden de inserción es parte del contrato**
  (ordena la tabla de servicios de la propuesta). FASE-C, que reescribe los dos builders de
  `proposal_asset_alignment.py`, debe preservar ese orden o cambiarlo con decisión registrada.
- `v4_proposal_generator.py:1281-1289` (`service_brecha_candidates`) ya **deriva su identidad** del
  canónico; su **lógica** quedó intacta, como exigía A4. FASE-C reescribe la lógica sobre una identidad
  ya unificada.
- **FASE-B hereda una precondición dura (N-A1, medida en `evidence/FASE-A/faseA_narratives_audit.txt`)**:
  `_pain_to_brecha` descarta pains en silencio en `v4_diagnostic_generator.py:3346-3347`; `narratives`
  (`:3263-3344`) tiene **16** claves frente a las **27** de Capa 1 ⟹ **11 ausentes**, que son
  exactamente **los 9 pains muertos de V1 + 2 que sí se emiten y sí se descartan hoy**
  (`no_ga4_enhanced`, `low_ota_divergence`). ⚠️ **FASE-B midió que esa última afirmación era
  falsa: ninguno de los dos se emitía realmente** (guardias insatisfacibles) — ver las Notas de
  ejecución de FASE-B abajo y S-B7. El resto de la nota sigue vigente.
  `narratives` y `detect_pains` son las dos mitades del mismo
  agujero: **arreglar solo la emisión deja el fix de B inerte** (los 9 rebotan en `:3346`). La biyección
  de AC4 debe ser **triple**: mapa↔emisión↔narrativa. Ver `10-analisis` §5 S6/S12/S13.
- **Orden forzoso nuevo B→H para `low_ota_divergence`**: V7 (FASE-H) arregla el guard `__iter__` que hoy
  impide que dispare. Si H va sin que B le haya dado entrada en `narratives`, el pain pasa de **«nunca
  dispara»** a **«dispara y se desvanece»** — peor para auditabilidad, porque el test de V7 pasa y la
  caída se vuelve invisible en vez de inexistente. **FASE-H debe verificar** (leer
  `evidence/FASE-B/decision-pains-muertos.md`) que B resolvió ese pain **antes** de tocar el guard.
- **FASE-B hereda también el registro #15 (C-5 / S14)**: los pesos de impacto que sirve `narratives`
  viven en `config/regional_benchmarks.yaml::pain_narratives` — **4 copias literales idénticas** (una por
  región, sin anclajes YAML) + **16 fallbacks hardcodeados** en Python = **80 literales para 16 valores**.
  El censo de A no lo contó (corregido como C-5 en `evidence/FASE-A/censo-registros.md` §8.1). Medido en
  `evidence/FASE-A/faseA_yaml_narratives_audit.txt` y `faseA_yaml_region_blind.txt`. Si B rellena
  `narratives` a 27 sin decidir el origen del peso, los 11 pains nuevos heredan un default en silencio
  (familia V6/P11/S7, dinero-adyacente). Ver `10-analisis` §5 S14.
- **FASE-F hereda**: `PAIN_TO_PRESENCE_ASSET` (6 entradas) **no** se derivó — la derivación completa
  produce 13 y cambia la semántica de `apply_site_verification`. Es exactamente el doble oráculo de
  A4/V15. Ver `10-analisis` §5 S8.
- `pain_ledger.py` y `conditional_generator.py` quedan **liberados** (eran A-exclusivos).
  `proposal_asset_alignment.py` y `v4_proposal_generator.py` pasan a C.
  ⚠️ **`v4_diagnostic_generator.py` ya NO pasa limpio a H**: por N-A1, **B necesita la región
  `:3246-3347`** (`_pain_to_brecha` + `narratives`) y **H necesita `:3197-3202`** (V6) y **`:1953`**
  (V11). Son regiones **disjuntas** del mismo archivo ⟹ B y H pueden convivir, pero los cambios de B
  deben confinarse a su región (regla añadida en `05-prompt-inicio-sesion-fase-B.md` §Restricciones).
  `config/regional_benchmarks.yaml` queda asignado a **B** (S14).

**Notas de ejecución de FASE-B** (relevantes para las fases que heredan sus archivos):

- **Delta medido** (`evidence/FASE-B/faseB_bijeccion_audit.txt`): Capa 1 **27 → 26** (se retiró
  `no_ga4_enhanced`), emisiones **18 → 20**, `narratives` literal **16 → 16** (sin cambio: el
  complemento se **deriva** de Capa 1, no se escribió a mano — L-NC4), cobertura narrativa
  efectiva **26/26**, **DESCARTE REAL 2 → 0**. AC4 cerrado.
- ⚠️ **La premisa de N-A1 citada arriba («2 que sí se emiten y sí se descartan hoy») era FALSA.**
  Medido en B1: `no_ga4_enhanced` **nunca se emitió** — su guardia `hasattr(status, "is_enhanced")`
  es insatisfacible porque el campo no existe en `AnalyticsStatus` ni se puebla en ningún punto
  del repo. `low_ota_divergence` tampoco: su guard hace `hasattr(float, '__iter__')` (V7). El
  script de FASE-A contaba *puntos de emisión escritos* por regex, no *emisiones alcanzables*.
  Consecuencia: `no_ga4_enhanced` se **retiró** (décimo pain muerto) en vez de narrarse.
  Seguimiento **S-B7**. Ver `evidence/FASE-B/decision-pains-muertos.md` §1.
- ✅ **El orden forzoso B→H para `low_ota_divergence` quedó SATISFECHO.** La nota de FASE-A exigía
  que **H verifique** que B resolvió ese pain antes de tocar el guard `__iter__`: está resuelto.
  Más aún — la capa narrativa es ahora **total sobre Capa 1**, así que cuando H arregle el guard
  la brecha aparece en el diagnóstico **sin editar ninguna segunda tabla**. H ya no puede
  convertir «nunca dispara» en «dispara y se desvanece».
  **(2026-09-04, FASE-H ejecutó el guard)**: V7 lo reemplazó por validación numérica con
  normalización de unidades ⟹ el pain **puede disparar** y, como la narrativa ya era total, la
  brecha llega al documento. El riesgo anunciado por A nunca se materializó.
- **L-A6 — citas desplazadas por B.** B añadió ~50 líneas a `pain_solution_mapper.py`
  (`detect_pains`, antes del `# Sort by severity`) y ~20 a `v4_diagnostic_generator.py`
  (dentro de `_pain_to_brecha`). Posiciones vigentes **(al cierre de B — ver tachado de abajo)**:
  - `pain_solution_mapper.py`: guard de V7 **`:447`** (era `:453`), emisión `low_ota_divergence`
    **`:452`** (era `:457`), `detect_pains` `:333`, `_detect_analytics_pains` `:720`.
  - `v4_diagnostic_generator.py`: **V6 `:3197-3202` y V11 `:1953` SIGUEN SIENDO VÁLIDAS** (los
    edits de B cayeron después). `_pain_to_brecha` sigue en `:3246` y `narratives` en `:3263`,
    pero la región de B ya no termina en `:3347`: el guard derivado ocupa `:3346-3369`.
  - ⚠️ **Estas posiciones quedaron SUPERADAS por FASE-H (2026-09-04)** y se conservan solo como
    registro de la medición de B: el guard `__iter__` de `:447` **ya no existe** (V7 lo sustituyó por
    `_normalize_to_fraction`/`_describe_ota_presence`, región `:443-472`), `_detect_analytics_pains`
    se reescribió en `:740-800`, y en el generador tanto V6 como V11 se movieron (el archivo creció
    **+128** líneas). Quinto caso de la clase: **usar símbolos**.
- **Capa 1 tiene 26 pain_ids, no 27.** Cualquier documento, test o prompt de fase posterior que
  cite «27» quedó desactualizado. El candado **no** fija el conteo (L-NC10): fija la relación.
- **Archivos nuevos que ninguna fase posterior debe duplicar**:
  `tests/commercial_documents/test_pain_map_bijection.py` (candado de la biyección triple, incluye
  el registro `PAINS_DIFERIDOS` con los 6 pains sin señal verificable),
  `tests/commercial_documents/test_detect_pains_emisiones_faseB.py` (18 tests, 9 negativos
  «vacío vs ausente»), `evidence/FASE-B/faseB_narratives_audit.py` (re-ejecutable).
- **S14 / C-5 resuelto**: los 4 pains que dejaron de descartarse tienen peso explícito en las
  **4 regiones** de `config/regional_benchmarks.yaml::pain_narratives` (16 → 20 entradas por
  región) + fallback Python **derivado del `estimated_impact` de Capa 1**, nunca un default mudo.
  `README.md:222` actualizado a «Pain narratives (20)» — lo exige
  `scripts/validate_document_integration.py`, que comparaba contra el YAML. **No se colapsaron las
  4 copias en anclajes YAML**: la estructura de 4 regiones es la costura de regionalización sobre
  configuración dinero-adyacente; el beneficio real (no divergir en silencio) se captura con un
  lint → **S-B8**.
- ⚠️ **FASE-C hereda 7 tests ROJOS preexistentes** en `tests/commercial_documents/`, todos del área
  de propuesta dinámica y todos fuera del diff de B: `test_proposal_dynamic.py` (2) y
  `test_proposal_confidence_disclosure.py::TestAssetQualityTable` (5). Prueba de causalidad y
  detalle en `decision-pains-muertos.md` §6 → **S-B10, S-B11, S-B12**. Dos de ellos viven en
  `proposal_asset_alignment.py`, el archivo que C reescribe.
- **Resto del barrido en verde**: baseline del prompt **848 passed / 2 skipped** (idéntico),
  barrido ancho **1121 passed**, contratos de FASE-A **42 passed** (incluida la precondición dura
  `test_narratives_subset_de_capa1`), `run_all_validations.py --quick` **7/7**.

**Notas de ejecución de FASE-C** (relevantes para las fases que heredan sus archivos):

- **Hay UN solo lugar que decide qué se promete**: `classify_promised_services()` en
  `modules/asset_generation/proposal_asset_alignment.py`. La consumen los **dos** builders
  (`ProposalAssetMatrix.build` y `AssetAlignmentMatrix.build`) y devuelve la tupla
  `(entries, not_promised, unknown_services)`. **Cualquier fase que cambie la semántica de promesa
  edita esa función, no un builder**: añadir lógica en uno solo re-abre A5 (el drift que C curó).
  El orden de inserción de `PROPOSAL_SERVICE_TO_ASSET` se preservó, como exigía la nota de A.
- **`site_presence_report` es ahora parámetro de los dos builders** y de `derive_committed_services`.
  → **FASE-E (A2)**: cuando persista el oráculo, debe alimentar **ese** parámetro con el snapshot
  persistido; la partición ya lo consume, no hace falta cablear nada nuevo.
  → **FASE-F (A4)**: la presencia se resuelve **dentro** de la partición (`_presence_exists`), así que
  el oráculo único debe reconciliarse con ese consumo y no solo con el DTO. La re-clasificación
  `NO_BREACH → PRESENT_IN_PRODUCTION` que hacía `AlignmentResult.from_asset_alignment_matrix` quedó
  **aguas arriba** (el servicio ya nace `PRESENT_IN_PRODUCTION` en la matriz); F1 decide si el
  cross-reference del DTO se retira o se conserva para artefactos pre-C. El comentario de
  `delivery_quality_report.py:232` que afirmaba «la matriz JSON nunca tiene PRESENT_IN_PRODUCTION»
  **ya es falso** y se corrigió en C.
- **Claves nuevas publicadas** en `proposal_asset_matrix.json` / `to_dict()`: `not_promised`,
  `unknown_services` y `summary = {promised, not_promised, unknown}`. **FASE-I**: las aserciones E2E
  sobre la matriz deben leerlas; **FASE-G**: `not_promised` es la señal de que un servicio quedó fuera
  de la promesa, no de que se haya descartado en silencio.
- **`vacío ≠ ausente` es ahora un contrato** (3 sitios corregidos: extracción `or []` y predicado
  `if pain_ledger:` en `publication_gates.py`, y `v4_proposal_generator.py:1201`).
  `None` → catálogo estático legacy (7 servicios, `NO_BREACH` donde no haya pain);
  `[]` → **0 comprometidos**, los 7 en `not_promised`. **Toda fase que lea `pain_ledger` del
  assessment usa `is not None`, nunca truthiness.** ⚠️ **FASE-G (G4/V9) hereda el caso duro**: con
  esta separación, 0 comprometidos ya significa genuinamente «resuelto sin brechas», así que el PASS
  trivial dejó de ser un accidente de confusión y pasó a ser una decisión semántica que G4 debe tomar.
  C **no** cerró V9 (`C1 DEFINE, G4 IMPLEMENTA`).
- **`ALWAYS_ACTIVE_COMPLEMENT_ASSETS`** (derivado de `counts_in_alignment=False`, hoy solo
  `monthly_report`) está **fuera del denominador** de `assets_are_justified` en
  `coherence_validator.py`. Los complementos **siguen generándose**: la exclusión es del recuento de
  promesa, no de la emisión. → **FASE-F (N11)**: no los re-incluya al tocar `is_coherent`; y note que
  el fix de AC6 **no** relajó nada — el umbral 0.8 y `_coherence_gate`
  (`publication_gates.py:458`) quedaron intactos.
- **Los 7 tests ROJOS que B legó a C (S-B10/S-B11/S-B12) quedaron 2 cerrados y 5 re-asignados**:
  **S-B10 ✅** (se re-incorporó `indirect_traffic_optimization` a `TECHNICAL_ASSET_CATALOG`, la opción
  que B ofrecía; `test_technical_assets_table_shows_both_assets` en verde). **S-B11 ✅** corregido en
  `552c190`: el test contradecía el cerrojo **B7**, que ya estaba fijado en ambos sentidos por
  `TestFaseR0DServiciosAdicionalesWhatsApp` y por `test_alignment_contract.py:133`; la omisión vivía
  en `v4_proposal_generator.py:1561-1565`, **no** en `proposal_asset_alignment.py` como decía S-B11.
  `test_proposal_dynamic.py` pasa de 1 failed/33 passed a **34 passed**, que era el criterio del
  prompt de C para ese archivo. **S-B12 🔴 sigue abierto y se re-asigna a FASE-H**: son 5 tests de
  `TestAssetQualityTable` sobre `_generate_asset_quality_table:1730` (refactor deliberado
  «Momento de entrega» en lugar de «Estado»), una tabla que **no** es la promesa de servicios del
  punto 8 y que C no tocó → **S-C6**. ⚠️ **2026-09-04 — FASE-H NO lo cerró**: su alcance autorizado
  eran los **seis quirúrgicos del Nivel 3.8** (V6/V7/V8/V11/V12/V13) y `v4_proposal_generator.py`
  nunca entró en él; los 5 tests siguen rojos y **VERIFY debe re-asignarlos** → **S-C6 sigue abierta**.
- **Restricciones que C respetó y siguen vigentes para E/F/G**: no se tocó el denominador de
  `coverage_ratio`, no se implementó S2.3, no se añadió el 8º servicio, no se unificó el oráculo de
  presencia (A4→F), no se tocó la severidad de gates (ya es de D), no se cerraron V5/V9 (→G).
- **Lo que C dejó deliberadamente estático**: `_generate_technical_assets_table` sigue listando el
  catálogo técnico completo (el contrato §3 lo pedía dinámico, pero el test existente fija el
  comportamiento estático y necesita su propio contrato) → **S-C4**.

**Notas de ejecución de FASE-D** (relevantes para las fases que heredan sus archivos):

- **Fuente única del régimen de publicación**: `BLOCKING_GATE_NAMES` (11) y `ADVISORY_GATE_NAMES` (2)
  en `modules/quality_gates/publication_gates.py`, más `gate_blocks_publication()` como **único
  predicado** de bloqueo. `check_publication_readiness`, `get_blocking_gates` e
  `is_ready_for_publication` deciden por ese predicado, no por `not r.passed` plano. **Fase que añada
  un gate nuevo**: registrarlo en `self.gates` **y** en una de las dos listas — el `RuntimeError` de
  fail-fast en `__init__` falla si los dos conjuntos no son disjuntos y su unión no es `self.gates`.
- **`is_ready_for_publication` quedó CONECTADA** (no eliminada, como ofrecía el prompt D): hoy la usa
  `main.py`. Era huérfana de producción antes de D.
- **Piso D2 (decisión del usuario)**: un advisory degrada a blocking bajo su corte estructural —
  `content_quality` con `details["blockers"]` no vacío, `proposal_asset_alignment` con `value <`
  `PROPOSAL_ASSET_ALIGNMENT_FLOOR` (0.8). Un advisory que **no se ejecutó** siempre bloquea
  (`details[GATE_EXECUTION_FAILED_KEY]`, señalada por el camino de excepción de `run_all`).
- **`summary` de `check_publication_readiness` creció**: `blocking_gate_names` y `advisory_issues`.
  **F/E/G consumen ese dict, no reconstruyan severidades por su cuenta** (sería el cuarto régimen).
- ⚠️ **`delivery_quality_report.py` NO fue tocado por D** — pertenece al régimen delivery (E→F, aún
  pendiente). La divulgación de advisories va por `HumanChecklistGenerator.generate(report,
  advisory_issues=...)`, cableada en `main.py`. **F7 de FASE-F puede cerrar el otro extremo**
  (meter los gates en el `DeliveryQualityReport`) ahora que existe un canal de consumo.
- **L-A6 — citas desplazadas por D.** `publication_gates.py` creció **2064 → 2181** líneas (+117:
  +70 del bloque de severidad antes de la clase, +47 repartidos en `__init__`, `run_all`,
  `check_publication_readiness` y `_content_quality_gate`). **Todas las citas de línea del archivo en
  los prompts C, D, F y G están desfasadas en +91** para símbolos posteriores a la línea 130.
  Posiciones vigentes medidas: `_coherence_gate` **549** (el plan decía 458) · `_critical_recall_gate`
  **619** (528) · `_content_quality_gate` **751** (660) · `_proposal_asset_alignment_gate` **933**
  (842) · `_JUSTIFIED_STATUSES` **1328** (1237) · `_coverage_gate` **1335** (1244) ·
  `_doc_audit_consistency_gate` **1555** (1464) · `_extract_coherence_score` **1946** (1855) ·
  `check_publication_readiness` **2010** (1919). **Usar símbolos.**
- **Hallazgo colateral**: el bloque «FASE 4.5» de `AGENTS.md` listaba **12** gates, no 13 — faltaba
  `doc_audit_consistency`. Corregido junto con la regrouping por severidad; lo detecta
  `validate_agents_md.py` (`missing_roadmap: []`).
- **Medido, no asumido**: contrafactual sobre la corrida real de SalentoReal ⟹ **0 flips** de `ready`
  (`evidence/FASE-D/faseD_contrafactual.py`). D **no relajó ningún veredicto**: lo que cambia es la
  divulgación (2 advisories antes silenciosos aparecen ahora en `human_checklist.md`) y el estado
  `PASSED → WARNING` de `content_quality` con solo warnings, que antes era invisible para cualquier
  consumidor de warnings. **S24**: la justificación de retirar `content_quality` y
  `proposal_asset_alignment` de blocking no estaba medida en el dossier (solo se midió
  `asset_confidence`) y descansa en que C cierre AC5 → **re-verificar tras FASE-C**.
- 🟡 **Concurrencia L-D1 + L-B5 (se materializó)**: D se ejecutó en una sesión **distinta y simultánea** a la
  de FASE-B sobre el **mismo working tree** (rama `master`, sin worktree). Mitigación aplicada: staging
  de **15 rutas explícitas** (nunca `git add -A`) para no arrastrar el trabajo en vuelo de B, y
  re-validación del baseline sobre el árbol combinado (**872 passed / 2 skipped** = 848 + 24 nuevos).
  Las dos sesiones se corrigieron mutuamente estados de fase en los documentos compartidos.
  → **S23** (tablas de estado duplicadas en los prompts) y **S-B15** (sobrescritura entre sesiones).

**Notas de ejecución de FASE-E** (relevantes para las fases que heredan sus archivos):

- **El oráculo persistido es un passthrough, no una reconstrucción** (DT4-N2): `save_site_presence_snapshot()` en
  `modules/asset_generation/site_presence_adapter.py` serializa el snapshot **tal cual** ya propagado por DT4-R2 —
  no llama `normalize_site_presence` ni reconstruye nada. Envoltorio versionado `{"snapshot_version": "1.0",
  "snapshot": ...}`, UTF-8 explícito, un solo archivo por corrida: `v4_audit/site_presence_snapshot.json`. Un test
  sonda (campos de probe que sobreviven arriba y dentro de `results`) garantiza que una normalización no puede
  colarse en silencio. **FASE-F (A4)**: ese archivo es el insumo del oráculo único; la partición ya consume el
  parámetro (nota de C arriba), no hace falta cablear nada nuevo.
- **Punto de persistencia**: `main.py`, inmediatamente después de crear `v4_audit_dir`. Usa
  **`site_presence_snapshot`** (definido incondicionalmente), NO `site_presence_report` (solo existe dentro de
  `if generate_proposal:` — NameError latente preexistente, registrado abajo). Persistencia en `try/except` con
  `[WARN]`: la evidencia no bloquea la corrida.
- **Causa raíz de A6 — `asset_path` null era culpa del caller, no de la matriz**: `classify_promised_services()`
  ya poblaba `asset_path` correctamente; el caller de `main.py` (`assets_for_quality`) construía los dicts **sin
  la clave `path`**. Fix: `"path": a.path or None` (1 línea). La rama fallback de `asset_plan` sigue **sin** rutas
  a propósito — no se inventan rutas que no hay. Los tests de E2 cubren: LINKED poblado, `path=None` se queda
  null, MISSING_ASSET null, forma pre-E (sin clave) null, y el extremo E2E del consumidor delivery
  (`DeliveryQualityReportGenerator` → `proposal_asset_gate.passed=True` con la ruta real persistida en JSON).
- ⚠️ **Desviación justificada de §4**: el plan declaraba E1 ‖ E2 paralelizables como subagentes, pero **ambos
  tracks editan `main.py`** (regiones ~`:2798` y ~`:3157`) — la misma condición que materializó L-D1/S-B15 en
  FASE-D. Se ejecutaron **secuenciales** (E1 → E2) con verificación `git diff` entre ambos; la verificación de
  consumidores (E4) fue censo de lectura, sin edición. Corregir §4 si H/I reutilizan la fila.
- **Baseline preservado**: 892 passed / 2 skipped → **897 / 2** (+10 tests nuevos: 5 en
  `tests/test_site_presence_persistence.py`, 5 en `tests/quality_gates/test_delivery_asset_path.py`).
  `run_all_validations.py --quick` 7/7. Evidencia: `evidence/FASE-E/faseE_persist.txt`,
  `faseE_baseline_antes.txt`, `faseE_baseline_despues.txt`, `faseE_validaciones.txt`.
- **Censo de consumidores (E4) → insumo duro para F**: `evidence/FASE-E/consumidores-snapshot.md`. Resumen:
  **6 consumidores activos** leen el snapshot propagado (coherence_validator `:410-411`/`:581-597`,
  pain_ledger `:134-145`, proposal_asset_alignment `:446-480`, publication_gates `:980-1078`,
  alignment_result `:62-76`, delivery_quality_report `:244-246`); **1 ruta viva de re-verificación**
  (`conditional_generator.py:64/:111`, por-asset, incluye historial delivery); **3 puntos muertos/degradados**
  heredados de antes de DT4: bloques `presence_lookup` de `v4_proposal_generator.py:1388-1396`/`:1617-1625`/
  `:1685-1693` (guard `hasattr` insatisfacible contra el dict canónico; **inicios re-verificados con grep al
  cierre de E** — esta nota los citaba corridos en 1: `:1389`/`:1618`/`:1686`), instanciación muerta
  `v4_asset_orchestrator.py:240`, y el NameError latente de `main.py` arriba. **Ningún consumidor reconstruye
  el oráculo** — las "4 rutas de reconstrucción" de DT4-N2 quedan en: 1 viva (legítima, per-asset con skip),
  resto muerto → decisión F1.
- **Archivos nuevos que ninguna fase posterior debe duplicar**: `modules/asset_generation/
  site_presence_adapter.py::save_site_presence_snapshot` (único writer del oráculo),
  `tests/test_site_presence_persistence.py`, `tests/quality_gates/test_delivery_asset_path.py`.
  ⚠️ `main.py` y `site_presence_adapter.py` no estaban en la matriz §3 — añadidos vía esta nota; F1 edita
  el writer/lector sobre esta base, no crea otro.
- **L-A6 — posiciones vigentes tras E**: `main.py` creció en dos hunks (E1 tras `v4_audit_dir` en FASE 0E;
  E2 en `assets_for_quality`). Citas de `main.py` en prompts F/G/I posteriores a esas regiones pueden estar
  desfasadas; usar símbolos (`save_site_presence_snapshot`, `assets_for_quality`).

---

---

**Notas de ejecución de FASE-F** (relevantes para las fases que heredan sus archivos):

- **A4 — el segundo oráculo vivía en `proposal_asset_alignment.py`**, no en `alignment_result.py`:
  la clasificación de `verify_proposal_asset_alignment` usaba `== "exists"` (estricto) mientras
  `_presence_resolved` del DTO ya usaba el criterio canónico. F1 cambió la clasificación a
  `is_present_in_production()` y extendió el veto de divergencia FASE-12B a `exists_with_issues`
  (si no, unificar habría debilitado la guardia). `alignment_result.py` no se tocó.
- **V15 — el cross-reference del DTO se conserva**: cubre artefactos pre-C cuya matriz nace
  `NO_BREACH`/`MISSING_ASSET`. Con ambos lados usando el mismo criterio, narrativa y veredicto
  ya no pueden divergir; test anti-A4 fija el invariante (`report.missing ∩ present_assets = ∅`).
- **A1 — estado `NOT_EVALUATED`**: `_not_evaluated_g9()` es el único default de G9
  (el segundo default independiente y la rama `"skipped": True` desaparecieron). El summary
  separa `passed`/`failed`/`not_evaluated` (lista de nombres); un gate no evaluado NO bloquea
  y NO cuenta como pasado. **No re-clasificar severidades** — el `BLOCKING_GATE_NAMES` de
  delivery quedó intacto (régimen distinto del de publicación).
- **N11/P9 — decisión (a): respetar `is_coherent`**. `coherence_verdict_passes(score, threshold,
  declared_is_coherent)` en `coherence_gate.py` es la ÚNICA definición del veredicto; la consume
  `_coherence_gate` (publicación) y `CoherenceGate` (legacy + validator). Un score ≥ umbral con
  `is_coherent=False` ⟹ `BLOCKED`; `None` (vacío ≠ ausente, L-SR5) ⟹ legacy por score. El umbral
  0.8 no se tocó. **coherence_gate.py quedó conectado** (`publication_gates.py:56` importa la
  función) — los 3 referenciadores previos (test de regresión, never-block, validate_context_integrity)
  no se tocaron.
- **H8 — `publication_state.py` ELIMINADO** (decisión conectar/eliminar: cero referencias
  verificadas por grep en modules/, main.py, tests/ y scripts/; sin imports dinámicos). El
  ROADMAP §7.2 conserva la tabla como correspondencia de diseño.
- **F4 — corpus**: `evidence/FASE-F/impacto-corpus.md` (script preservado en la misma carpeta).
  28 primarias + 4 copias delivery. **0 corridas liberadas**; 4 veredictos READY→NOT_READY
  (`final_coherence_report.is_coherent=False` persistido que el gate pre-F ignoraba — familia
  exacta de N11, incluye la repro SalentoReal FASE-D 0.88/False); las ~10-11 ESTIMATED siguen
  bloqueadas (`coherence_score_final=None` ⟹ gate sin score; `asset_confidence` intacto). El
  conteo C2 de 27 se midió sobre `output/` pre-archivo; la medición barre `output/` +
  `archives/outputs/`.
- **Baseline**: 920 passed / 2 skipped (`tests/quality_gates` + `tests/asset_generation`;
  848/2 + delta A–F con 23 tests nuevos de F). Validaciones `--quick` 7/7.
  Evidencia: `evidence/FASE-F/faseF_*.txt` + `impacto-corpus.md`.
- **Citas de línea desfasadas en el prompt F**: `_coherence_gate` estaba en `:549` (no `:458`);
  los defaults de G9 se reubicaron por grep antes de editar (regla del propio prompt). Los
  consumos de `assessment["is_coherent"]` entran por `AssessmentPayload.is_coherent`
  (`assessment_builder.py`, poblado en `with_coherence` desde `final_coherence_report`,
  preferido sobre `coherence_report` — DT4-N4).

**Notas de ejecución de FASE-G** (relevantes para las fases que heredan sus archivos):

- **G2 vive en `modules/auditors/v4_comprehensive.py`, NO en `pain_solution_mapper.py`** — la
  predicción de la matriz §3 («G amplía `_identify_critical_issues` que lo consume») era falsa:
  el detector está en `v4_comprehensive.py:1830`. `pain_solution_mapper.py` quedó intacto
  ⟹ **H1/H3 (V13/V8) pierden el orden forzoso G→H por conflicto de archivo**: pueden correr
  sobre el working tree de G sin esperarlo (los demás quirúrgicos tampoco lo comparten).
- **Cableado G1/G2 — 2 puntos de inyección nuevos**: `AssessmentPayload.audit_data` (campo
  crudo, poblado por `builder.with_audit_data(audit_result.to_dict())` en `main.py` ~:2935) y
  `builder.with_geo_flow(json de `output_dir/hotel_id/v4_audit/geo_flow_result.json`)`.
  El helper **`geo_band_critical_issue`** es módulo-level en `v4_comprehensive.py` (compartido
  por el detector y el builder) — **no duplicarlo** (L-NC4). `main.py` tolera JSON ausente
  (WARN y sigue): GEO crítico solo califica si el artefacto existe.
- **SR-H2 condicionado (G2)**: el atajo favorable (critical_issues=[] + audit ejecutado →
  recall 1.0) solo se mantiene si `audit_data.performance.status != "ERROR"`; con el eje caído
  y sin issues registrados, recall = **0.0** y `_coverage_gate`-análogo BLOCKED. Con PageSpeed
  ERROR + GEO 29/100 (SalentoReal), la corrida FASE-I producirá `critical_recall` BLOCKED —
  **es el perfil esperado post-refactor, no una regresión**; comparar contra esto, no contra
  13/13 en verde.
- **G3 — péndulo BUG-6 resuelto por distinción de estados, no por reversión**: `ASSET_GENERATED`
  SIGUE en `_JUSTIFIED_STATUSES`; la escotilla vive ahora en la regla de mención del loop de
  coverage (mención en `diagnostic_pain_ids`/`proposal_pain_ids` ⟹ covered). El caso
  «existe en producción y basta» es `VERIFIED_IN_SITE` (primera clase FASE-P1-D, preservada por
  el reconciler) — el fixture anti-reversión (`evidence/FASE-G/faseG_anti_reveresion_fixture.py`)
  corre el gate REAL y muestra a VERIFIED_IN_SITE silencioso pasando con `ASSET_GENERATED`
  presente en la lista. **El gate NO re-detecta brechas** (DT4-N2 intacto).
- **G4 — unificación vacío tras normalización**: el gate normaliza ledger dict/lista antes de
  decidir, así que hay UNA rama por semántica, no una por forma: `resolved` vacío + `original`
  no vacío ⟹ BLOCKED `coverage_basis=reconciler_dropped_entries`; vacío legítimo ⟹ PASSED con
  traza `ledger_present_zero_entries` + `reconciler_ran`. `None` sigue siendo «no evaluado por
  el reconciler» → fallback.
- **Archivos nuevos que ninguna fase posterior debe duplicar**:
  `tests/auditors/test_v4_comprehensive.py` (13 tests del detector: PageSpeed ERROR, GEO banda,
  criterios legacy intactos), `tests/quality_gates/test_coverage_gate_v5.py` (15 tests V5+V9,
  incluye el anti-reversión), `tests/quality_gates/test_doc_audit_consistency_gate.py`
  (REESCRITO: 12 tests, contrato FAILED/NOT_EVALUATED sustituye al WARNING-mode pre-G).
- **L-A6 — citas desplazadas por G**: `publication_gates.py` creció (NOT_EVALUATED en `__init__`
  /`run_all`/summary, `_doc_audit_consistency_gate` reescrito ~:1654-1837, G4 en
  `_coverage_gate` ~:1487-1521, G3 en el loop ~:1549, `_evident_critical_missed` ~:2073,
  `_extract_critical_recall` ~:2099). **Usar símbolos**, no números.
- **Lo que G NO tocó y H cerró/NO cerró**: ✅ **H sí cerró `pain_solution_mapper.py`** (guard `__iter__`
  de V7 + dedup de V8, 2026-09-04). ❌ **H NO tocó** `coherence_validator.py`, `delivery_quality_report.py`
  (F7 divulgación de gates en el `DeliveryQualityReport`), ni `v4_proposal_generator.py`
  (`_generate_asset_quality_table:1730`, S-B12→S-C6): el alcance autorizado de H eran los **seis
  quirúrgicos del Nivel 3.8**, no las re-asignaciones acumuladas de C/E/F/G. Los seguimientos
  **S-C3 / S-C4 / S-C6 / S-E2 / S-F2** siguen abiertos y **VERIFY debe re-asignarlos** (quedan
  registrados, sin tocar, en `10-analisis` §5).
- **Deuda del fixture citado**: el plan y el prompt G citaban
  `audit_report_20260831_122803.json`; el real es `audit_report_20260831_122757.json`
  (`output/v4_complete/*/v4_audit/`). Los tests usan fixtures sintéticos alineados al `to_dict()`
  real del auditor.

**Notas de ejecución de FASE-H** (relevantes para las fases que heredan sus archivos):

- **La delegación fue por ARCHIVOS DISJUNTOS, no por regiones del mismo archivo.** §4 predecía
  «Subagente 1 (H1+H2) ‖ Subagente 2 (H3+H4)», pero H1/H3 comparten `pain_solution_mapper.py` y
  H2/H3 comparten `v4_diagnostic_generator.py`. Reparto real: **Subagente 1** (mapper) = V7 + V8 ·
  **Subagente 2** (generador) = V6 + V11-lado-documento · **Parent** = V11-lado-audit
  (`v4_comprehensive.py`), V13 y V12. La verificación de solapamiento quedó a cargo del parent y
  **no hubo conflicto de regiones**. Es la segunda vez que §4 declara tracks paralelizables falsos
  (la primera: E1/E2 sobre `main.py` → S-E1) → **L-H2**.
- **V7 cerró el `low_ota_divergence` y el orden forzoso B→H quedó cumplido en sus términos**: el
  guard `hasattr(direct_field.value, '__iter__')` se reemplazó por validación numérica con
  normalización de unidades (`_normalize_to_fraction`, `_describe_ota_presence`). `ota_presence`
  entró como **evidencia no bloqueante del description**, **nunca** como guard: `main.py` no
  registra ese campo en el `ValidationSummary`, así que usarlo de guard devolvía el pain a código
  muerto. Consecuencia para **I**: un pain `high`/priority 1 puede ahora derivar del
  `direct_channel_percentage = 0.20` de fuente `"Default"` — un dato que el hotel nunca informó
  (`main.py:1865`, `main.py:1890`, `main.py:2306-2314`, `modules/financial_engine/calculator_v2.py:481`).
- **V6 introduce un estado de fase, no un valor**: `BRECHAS_STATE_EVALUATED` /
  `BRECHAS_STATE_NOT_EVALUATED` + `self._brechas_detection_state`, reseteado **por corrida** en
  `generate()`. El `except Exception` de `_identify_brechas` loguea traceback, fija NOT_EVALUATED y
  **deja de escribir el caché** (`_cached_brechas` / `_cached_brechas_key`) — antes un fallo
  envenenaba el caché de la corrida. El `NOT_EVALUATED` **se replica, no se importa** de
  `GateStatus`: el import top-level de `modules.quality_gates.publication_gates` desde
  `commercial_documents` produce `ImportError` por ciclo (`publication_gates → coherence_gate →
  commercial_documents.coherence_validator → __init__` del paquete, verificado empíricamente). La
  deriva queda cerrada por `test_v6_estado_not_evaluated_reutiliza_literal_canonico_del_gate`.
- **Archivos nuevos que ninguna fase posterior debe duplicar**:
  **`modules/common/performance_status.py`** (`PERFORMANCE_OK_STATUSES` +
  `is_performance_api_unavailable()`) — es la **única** definición del criterio «¿el eje PageSpeed
  quedó medido?», y la consumen tanto el documento (`v4_diagnostic_generator.py`) como el audit
  (`v4_comprehensive.py`). Es lista **blanca** a propósito: vacío ≠ ausente (SR-H2). Quien necesite
  ese predicado importa de ahí; re-decidirlo en un consumidor es L-NC4 (misma familia H10/A1 que
  denuncia el dossier).
- **V13: el gemelo `MetadataValidator` quedó BORRADO**: el primer `git rm` lo bloqueó la política de
  permisos del entorno, así que quedó un shim de delegación explícita (219 → **26** líneas, la opción
  que admite el AC); con autorización del usuario se ejecutó el **borrado físico el mismo 2026-09-04**.
  Solo existe `data_validation/metadata_validator.py` (el vivo: lo importa
  `modules/auditors/v4_comprehensive.py:33` y lo re-exporta `data_validation/__init__.py`) y la guardia
  fija su **ausencia** (`find_spec(...) is None`) → **S-H14 cerrado en la fase**.
  `metadata=None` cuando el audit crashea **no** era parte de V13 y sigue abierto → **S-H4**.
- **V12 se documentó y `.env` NO se tocó** (`git diff --stat .env` vacío), como exigía la regla
  transversal del README y DA5. Hoy la cadena de fallback de `pagespeed_client.py` resuelve la clave
  válida; **eliminar `PAGESPEED_API_KEY` reintroduce el síntoma** porque el fallback cae en el
  placeholder de 3 caracteres. Detalle y recomendación OPS en `09-documentacion-post-proyecto.md` §E.
- **L-A6 — posiciones desplazadas por H** (medido con `wc -l` contra `HEAD`):
  `pain_solution_mapper.py` **1202 → 1297** (+95), `v4_diagnostic_generator.py` **3715 → 3843**
  (+128), `v4_comprehensive.py` **1945 → 2025** (+80). **Todas las citas de línea de los prompts de
  I/VERIFY sobre esos tres archivos están desfasadas**; usar símbolos
  (`_normalize_to_fraction`, `_identify_brechas`, `_brechas_detection_failed`,
  `sanitize_pagespeed_message`, `disjoint_executed_validators`). H re-verificó sus propias citas antes
  de editar y encontró **cinco fósiles** y **un archivo de test inexistente** en su prompt → **L-H4**.
- **Lo que H NO tocó y fases previas le habían re-asignado**: `coherence_validator.py` (**S-C3**),
  `_generate_asset_quality_table` y los 5 tests rojos de `TestAssetQualityTable` (**S-B12/S-C6**),
  la tabla técnica estática (**S-C4**), los bloques `presence_lookup` muertos + el NameError latente
  (**S-E2**) y **G6-delivery score-only** (**S-F2**). El alcance autorizado de H eran **los seis
  quirúrgicos del Nivel 3.8**, no las re-asignaciones acumuladas de C/E/F/G → **VERIFY debe
  re-asignarlas** (quedan registradas en `10-analisis` §5, sin tocar).
- **Baseline y contratos**: `tests/quality_gates` + `tests/asset_generation` **944 passed / 2 skipped**
  (idéntico al cierre de G — el «848/2» del prompt de H estaba desactualizado); contratos A/B
  **83 passed**; `run_all_validations.py --quick` **7/7**. **Fallo preexistente NO corregido y ajeno
  a H**: `tests/test_diagnostic_geo_metrics.py::test_diagnostic_includes_geo_metrics` → **S-H16**.

**Notas de ejecución de FASE-I** (la última fase con producto que VERIFY hereda):

- **La corrida única salió bien**: `EXIT_CODE 0` en **174 s**, 0 tracebacks, `"Using defaults"`,
  0 interferencias del `own_site_guard`, **sin** `clientes/`, **sin** `--ga4-property-id`, **sin**
  `--force`/`--force-new`, y **sin re-corrida**. Verificado antes de ejecutar que `v4complete` **no**
  recicla análisis previo — `find_latest_v4_analysis` se llama solo en la rama `execute` (`main.py:776`)
  y los `research_*.json` no se leen de caché (único hit: `autonomous_researcher.py:86`). Sin esa
  comprobación, una corrida sobre análisis del 31-08 habría parecido un éxito sin serlo.
- **Modo MIXTO respetado**: el subagente **solo ejecutó y capturó**; toda la interpretación quedó en el
  parent (executor L30 RC1-RC2). El parent **no tocó código** — la restricción de alcance se cumplió:
  `git status` al cerrar solo muestra `evidence/FASE-I/` y los 5 archivos del plan.
- **Los nombres timestamped se RESOLVIERON, no se asumieron** (deuda H7): `audit_report_20260904_120404`,
  `financial_scenarios_20260904_120404`, `gate_report_20260904_120413`,
  `commercial_gates_report_diagnostic_20260904_120413` — tabla completa en `evidence/FASE-I/MANIFIESTO.md` §3.
- **Se leyeron los DOS archivos de commercial gates**: el conteo real es **12 CG-*** (3 + 9) y el único
  fallo (`CG-WHATSAPP-LEAD`, `passed:false`) es **idéntico al baseline** ⟹ clasificado (iii), no regresión.
- **Pre-flight con un fallo que NO es de código**: `validate_agents_md.py` **5 PASS / 1 FAIL**
  (`test_count` 3689 AGENTS vs 3889 pytest = 5.1 % > ±5 %). Preexistente en HEAD; el prompt esperaba 6/0.
  → **S-I6**, le toca a RELEASE.
- **Los dos FAIL de la comparación son el producto real de la fase** y ambos traen causa raíz medida, no
  supuesta: **S-I1** (`critical_recall` 1.0 con `details={}`; el detector G2 queda a la sombra del registro
  V6 de H — falsada la predicción de `dependencias-fases.md:353`) y **S-I2** (la severidad 11+2 no se
  serializa en `gate_report_*.json` ⟹ AC7 no verificable sobre artefactos). Ninguno se corrigió aquí.
- **Dos premisas propias que hubo que corregir midiendo**: (a) el script de comparación leía `asset_path`
  en `v4_complete_report.assets_generated[]` cuando la clave real es **`path`** — habría sentenciado «A6
  sigue nulo» en ambas corridas (**S-I3**); (b) el «848/2» que citaba su propio prompt estaba desactualizado
  (es **944/2** desde G), mismo defecto que S26 predice.
- **La coherencia BAJÓ (0.88 → 0.8333) y está atribuida**: `problems_have_solutions` 1.0→0.6 porque el
  ledger pasó de 3 a 5 pains. **Ninguna diferencia se cerró como «variación natural»**: fotos 10,
  `metadata.title=""`, competidores y los 3 escenarios financieros son numéricamente idénticos. → **S-I4**.
- **Hereda de VERIFY**: S-I1..S-I7 (`10-analisis` §5.7) más el residuo que I no podía cerrar —
  **S-C3, S-E2, S-F2, S-H2, S-B12/S-C6, S-B13, S-B14, S-H16, S-H18** (esta última con resultado negativo
  documentado: FASE-I leyó 41 artefactos de producción y no apareció ninguna cadena imperativa; el barrido
  sigue **sin automatizar**).

## 1. Grafo de dependencias

```
                        ┌──────────────┐
                        │   FASE-A     │  Fuente única de identidad
                        │    (ALTA)    │  V2/V3/V14 · AC1-AC3
                        └──────┬───────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
      ┌──────────────┐  ┌─────────────┐  ┌──────────────┐
      │   FASE-B     │  │  FASE-D     │  │              │
      │ (MEDIA-ALTA) │  │   (MEDIA)   │  │              │
      │ V1 · AC4     │  │ H10 · AC7-8 │  │              │
      └──────┬───────┘  └─────────────┘  │              │
             │                ▲          │              │
             │                │          │              │
             ▼                │          │              │
      ┌──────────────┐        │          │              │
      │   FASE-C     │────────┘          │              │
      │  (MÁXIMA)    │  (C1 documenta la │              │
      │ Punto 8      │  interacción con  │              │
      │ AC5-AC6      │  V9/G4 p/ ledger  │              │
      └──────┬───────┘  vacío — spec en  │              │
             │          C, severidad en  │              │
             │          G4; SIN dep. dura│              │
             │                           │              │
             ▼                           │              │
      ┌──────────────┐                   │              │
      │   FASE-E     │◀──────────────────┘              │
      │   (MEDIA)    │  E depende de B (biyección       │
      │ A2 + A6      │  fija qué pain emite el ledger   │
      │ AC9          │  que E persiste/consuma)         │
      └──────┬───────┘                                  │
             │                                          │
             ▼                                          │
      ┌──────────────┐                                  │
      │   FASE-F     │◀─────────────────────────────────┘
      │ (MEDIA-ALTA) │  F depende de C (no_breach=0 cambia
      │ A4+A1+N11    │  el insumo del oráculo) y de E
      │ AC10-AC12    │  (snapshot persistido es el insumo
      └──────┬───────┘   del oráculo único)
             │
             ├──────────────────────────┐
             ▼                          ▼
      ┌──────────────┐          ┌──────────────┐
      │   FASE-G     │          │   FASE-H     │
      │ (MEDIA-ALTA) │─────────▶│ (BAJA-MEDIA) │
      │ Nivel 3.7    │ (orden   │ Nivel 3.8    │
      │ NR1-NR4      │  forzoso │ V6/V7/V8/    │
      └──────┬───────┘  por     │ V11/V12/V13  │
             │         conflicto└──────┬───────┘
             │         de archivo)     │
             └──────────┬──────────────┘
                        ▼
                ┌───────────────┐
                │    FASE-I     │  E2E ÚNICA v4complete
                │  (BAJA impl)  │  Hotel Salento Real
                │  NR6 + deltas │  ← requiere A-H ✅
                └───────┬───────┘
                        ▼
                ┌───────────────┐
                │  FASE-VERIFY  │  DIRECTO · no delegable (§4.6)
                │ AC1-12 + NR1-6│
                └───────┬───────┘
                        ▼
                ┌───────────────┐
                │ FASE-RELEASE  │  DELEGABLE · v4.75.0
                │   4.75.0      │
                └───────────────┘
```

> ⚠️ **Aclaración post-EJECUCIÓN (2026-09-04)**: la arista G→H dibujada como «orden forzoso por
> conflicto de archivo» **nunca existió** — G no tocó `pain_solution_mapper.py` (ver Notas de FASE-G).
> H se ejecutó después de G igualmente, pero por **R1 (una fase por sesión)**, no por conflicto. Lo que
> sí existió fue un conflicto **interno** de H: dos tracks sobre el mismo archivo ⟹ la paralelización de
> §4 se re-emplementó por **archivos disjuntos** (ver Notas de FASE-H y L-H2).

---

## 2. Matriz de dependencias

| Fase | Depende de (duro) | Razón de la dependencia | Bloquea a |
|------|-------------------|-------------------------|-----------|
| **A** | — | Es la base: decide cuál registro manda | B, C, D, E, F, G, H |
| **B** | A | El candado de biyección (B3) valida contra el registro canónico de A2; sin él, fijaría una copia parcial | C, E, H |
| **C** | A, B | El punto 8 deriva la promesa del registro canónico (A) y de los pains que realmente se emiten (B). Construirlo antes produciría una propuesta dinámica sobre IDs fantasma | F, G, I |
| **D** | A | La severidad explícita clasifica gates cuyo insumo (`proposal_asset_alignment`) deriva del registro canónico | F, I |
| **E** | B | A2 persiste el snapshot que los consumidores usan para resolver presencia; A6 puebla `asset_path` de assets cuya identidad fija la biyección | F, I |
| **F** | C, E | F1 (oráculo único) consume el snapshot persistido por E1 y opera sobre una matriz donde C ya hizo `no_breach = 0`. F3 (N11) interactúa con la severidad de D | G, H, I |
| **G** | F | G3/G4 cierran escotillas del `_coverage_gate` cuyo criterio de presencia ya unificó F1; cerrarlas antes fijaría el criterio doble | H, I |
| **H** | B, F, ~~G~~ | ✅ **Ejecutada 2026-09-04**. ⚠️ **Predicción corregida**: el orden forzoso G→H era por conflicto de archivo (H1 toca `pain_solution_mapper.py` que se predecía también tocado por G) — **G no lo tocó** (G2 vive en `v4_comprehensive.py`), así que nunca hubo orden forzoso por archivo. Lo que H **sí** consumió de sus predecesoras: la **biyección de B** (V7 quedó sobre un pain que ya tiene narrativa derivada + peso `0.20` en las 4 regiones ⟹ al arreglar el guard la brecha **aparece en el documento**, no se desvanece; V8 es dedup dentro del mismo `_detect_analytics_pains` que B agrandó), el **estado `NOT_EVALUATED` de F/A1** (replicado como `BRECHAS_STATE_NOT_EVALUATED` para V6, no importado — ciclo de paquetes) y el **`v4_comprehensive.py` de G** (V11-lado-fuente y `disjoint_executed_validators()` caen sobre el archivo que G había crecido +60 líneas) | I |
| **I** | A-H ✅ | Es la validación integrada; correrla antes mediría un sistema a medio refactorizar | VERIFY |
| **VERIFY** | I | Certifica contra evidencia real de la corrida | RELEASE |
| **RELEASE** | VERIFY | El CHANGELOG y GUIA_TECNICA se alimentan de `09` y `10`, que VERIFY completa | — |

**Camino crítico**: A → B → C → F → G → H → I → VERIFY → RELEASE (9 sesiones).
D y E están fuera del camino crítico y pueden ejecutarse en cualquier hueco tras A y B respectivamente.

---

## 3. Conflictos de archivo (quién toca qué)

| Archivo | Fases que lo tocan | Orden forzoso | Naturaleza del conflicto |
|---------|--------------------|---------------|--------------------------|
| `modules/commercial_documents/pain_solution_mapper.py` | **B**, **H** | B → ~~G~~ → H | ✅ **Cerrado 2026-09-04 con H.** ⚠️ **Predicción corregida 2026-09-04**: la matriz decía «B, G, H» porque se esperaba que G amplía `_identify_critical_issues` aquí — pero el detector vive en `modules/auditors/v4_comprehensive.py:1830` y **G no tocó este archivo** (verificado en `git show --stat c317cda`). B edita `PAIN_SOLUTION_MAP` (`:60`) y `detect_pains` (`:339`) — ✅ cerrado; **H1 (V7)** reemplazó el guard `__iter__` en la región **`:443-472`** por validación numérica con `_normalize_to_fraction` (definida en `:1235`) y `_describe_ota_presence` (`:1271`), y degradó `ota_presence` a **evidencia no bloqueante** del description; **H3 (V8)** unificó la emisión de `low_organic_visibility` en `_detect_analytics_pains` (**`:740-800`**, un solo punto de emisión). Archivo **1202 → 1297 líneas** (+95). ⚠️ El `:447` que medimos al cerrar B era el guard; tras H la región arranca en **`:444`** (L-A6 otra vez: usar símbolos) |
| `modules/quality_gates/publication_gates.py` | **D**, **C**, **F**, **G** | D → C → F → G | ✅ **Cerrado 2026-09-04 con G.** D reestructura `self.gates` (`:181-195`) y `check_publication_readiness` (`:1919`) — ✅ cerrado; F3 modifica `_coherence_gate`; G1/G3/G4 modificaron `_doc_audit_consistency_gate` y `_coverage_gate` (posiciones post-F en las Notas de ejecución de G) y añadieron NOT_EVALUATED a `__init__`/`run_all`/summary. ⚠️ **C también lo editó, fuera de la predicción** (la matriz no lo listaba): **3 hunks `:979-1011`**, todos dentro de `_proposal_asset_alignment_gate` — (1) `assessment.get("pain_ledger") or []` → sin `or []`, que era el sitio de colapso **aguas arriba** y el que convirtió «sin ledger» en «resuelto con 0 brechas» (27 fallos en cadena hasta quitarlo), (2) `if pain_ledger:` → `if pain_ledger is not None:`, (3) el build de la matriz recibe `site_presence_report` (sin esto, gate y delivery report divergían y rompían AC3) |
| `modules/asset_generation/proposal_asset_alignment.py` | **A**, **C** | A → C | ✅ **Cerrado 2026-09-03.** A3 migró `PROPOSAL_SERVICE_TO_ASSET` (`:22`) al canónico; C3 modificó los dos builders (`:575`, `:748`) — pero **no parcheó sus rutas de skip silencioso** (`:609-612`, `:792-794`): las **eliminó** extrayendo una única `classify_promised_services()` que ambos consumen, así que ya no existen dos caminos que puedan divergir (A5 curado, no esquivado). Diff real: 359 líneas |
| `modules/quality_gates/alignment_result.py` | ~~**C**~~, **F** | — | ⚠️ **Predicción corregida 2026-09-03**: se esperaba que C3 tocara `_from_entries` (`:222-276`) y `compute_unresolved` (`:175-212`), pero **C no modificó este archivo de producción** — verificado con `git show --stat c1bf5e2` (solo actualizó su test, `tests/quality_gates/test_alignment_result.py`). La región queda **libre para F1**, que ya no tiene conflicto con C. Lo que F1 **sí** hereda: la presencia ahora se resuelve **aguas arriba**, dentro de `classify_promised_services()` (`_presence_exists`), así que `_presence_resolved` (`:62`) puede haber quedado redundante para artefactos post-C → decidir en F1 junto a A4 |
| `modules/quality_gates/delivery_quality_report.py` | **C** (comentario), ~~**E**~~, **F** | C → F | ⚠️ **Predicción corregida 2026-09-03**: se esperaba que E2 editara este archivo, pero la causa raíz del `asset_path` null estaba en el **caller** (`main.py`, dicts de `assets_for_quality` sin clave `path`) — E no tocó este archivo; su consumo de `asset_path` (`:244-246`) ya funcionaba y se verificó E2E en `tests/quality_gates/test_delivery_asset_path.py`. F2 modifica la región de skip (`:251-255`), el summary (`:310-319`) y los defaults (`:325`) — adyacentes. C dejó un hunk `:230-243` sin cambio de comportamiento (comentario «la matriz JSON nunca tiene `PRESENT_IN_PRODUCTION`» corregido, cross-reference conservado para artefactos pre-C). F hereda esa región ya reescrita |
| `modules/commercial_documents/v4_proposal_generator.py` | **A**, **C** | A → C | A4 corrige el drift «8 vs 7» (`:1332`) — ✅ cerrado. ⚠️ **C NO reescribió `service_brecha_candidates` (`:1281-1289`)** como predecía esta fila: ese dict ya **deriva** su identidad de Capa 2 desde A y su **lógica** es la que produce V4 (atribución ciega al pain real), que **sigue abierta** → **S-C5**. Los 2 hunks reales de C (verificados con `git show c1bf5e2`): **`:696-702`** (el build de la matriz pasa `site_presence_report`, sin el cual gate y delivery report divergían — AC3) y **`:1199-1208`** (`_derive_committed_services`: `if not pain_ledger` → `if pain_ledger is None`, vacío ≠ ausente). Diff total: 6 líneas. ⚠️ **Corregido 2026-09-03**: esta fila atribuía a H2 «el `except Exception` de `_identify_brechas`», pero ese método **solo existe en `v4_diagnostic_generator.py:3116`** (`grep -rn "def _identify_brechas"` = 1 resultado) y el prompt de FASE-H no menciona este archivo. H2 ya está correctamente asignado en la fila siguiente |
| `modules/commercial_documents/v4_diagnostic_generator.py` | **A**, **B**, **H** | A → B → H | ✅ **Cerrado 2026-09-04 con H.** A3/A4 migran `ELEMENTO_KB_TO_PAIN_ID` (`:135-157`, `:160`, `:3067-3086`) — ✅ cerrado; **B editó `_pain_to_brecha` + `narratives` por N-A1** — ✅ cerrado; **H2 (V6)** reemplazó el `except Exception: return brechas` + caché (región real **`:3296-3314`** al momento de editar; el dossier citaba `:3189-3194`, cita fósil verificada y corregida el 2026-09-03 en los 6 archivos del plan que la repetían) y añadió los estados `BRECHAS_STATE_EVALUATED`/`NOT_EVALUATED` (`:65-66`), el atributo `self._brechas_detection_state` (`:553`, reseteado por corrida en `:623`), el aviso de render `_FUGAS_NOT_EVALUATED_NOTICE` (`:2786-2796`) y el helper `_brechas_detection_failed()` (`:2739`); **H3 (V11-lado-documento)** limpió los residuos D6 de la rama de performance y añadió `MANUAL_ATTENTION_TABLE_HEADER` (`:77`) para que `${manual_attention_table}` renderice como tabla (caída #6). Regiones **disjuntas** con las de A y B ⟹ convivieron como predecía la matriz ✅. Archivo **3715 → 3843 líneas** (+128) ⚠️ **las citas `:3197-3202` / `:1953` de cualquier documento posterior quedaron desfasadas — usar símbolos** |
| `config/regional_benchmarks.yaml` | **B** | — | B decide el origen de los pesos `pain_narratives` (4 copias literales idénticas + 16 fallbacks Python = 80 literales para 16 valores). Hallazgo C-5 / S14, post-censo de A |
| `modules/asset_generation/pain_ledger.py` | **A** | — | A3 migra `NORMALIZATION_RULES` / `PAIN_TO_PRESENCE_ASSET` (`:52-94`) |
| `modules/asset_generation/conditional_generator.py` | **A** | — | A3 migra `PAIN_TO_ASSET` (`:234-257`) y el import de `ELEMENTO_KB_TO_PAIN_ID` (`:314-326`) |
| `modules/commercial_documents/coherence_validator.py` | **C** (~~lectura~~ **escritura**), **F** (decisión) | C → F | ⚠️ **Desviación registrada 2026-09-03**: esta fila declaraba a C como **solo lectura**, y C **editó** el archivo. Motivo: la causa real de AC6 resultó ser `_check_assets_are_justified` (no `promised_assets_exist` como decía B5), y ese método vive aquí. La edición es **un solo hunk `:278-320`** (`_check_assets_are_justified`, 35 líneas) y **la región de F3 quedó intacta**: ni `is_coherent` (`:185-188`) ni `promised_assets_exist` (`:670-700`) fueron tocados — verificado con `git show c1bf5e2 -- …coherence_validator.py \| grep "^@@"`. C4 **no** se apoyó en `promised_assets_exist` (P12/A3, acotado por `if not generated_assets:`), como exigía la fila. **F3 hereda**: el denominador de `assets_are_justified` excluye `ALWAYS_ACTIVE_COMPLEMENT_ASSETS`; no re-incluirlo al decidir sobre `is_coherent` |
| `modules/auditors/v4_comprehensive.py` | **G**, **H** | G → H (secuencial, mismo archivo) | ⚠️ **No estaba en esta matriz** (añadido por la nota de G y cerrado por H, mismo precedente de `main.py`/`site_presence_adapter.py` en E). G añadió `geo_band_critical_issue` + los 2 criterios de `_identify_critical_issues` (`1885 → 1945`). **H (V11-lado-fuente)** añadió `PAGESPEED_KEY_MESSAGE`/`PAGESPEED_GENERIC_MESSAGE`/`PAGESPEED_NOT_CONFIGURED_MESSAGE` + `sanitize_pagespeed_message()` (`:47-79`), publicó el mensaje ya sanitizado desde `_audit_performance` (el crudo del `PageSpeedClient` queda solo en `logger`), hizo que `_generate_recommendations` lea `status`/`message` reales y definió `disjoint_executed_validators()` para que `execution_trace.executed` y `.skipped` sean excluyentes (punto **(d)**, `pagespeed_api` figuraba en ambos). **1945 → 2025 líneas** (+80). Importa porque `extract_top_problems` (`modules/commercial_documents/data_structures.py:532-536`) vierte esas recomendaciones textuales en el diagnóstico del cliente |
| `data_validation/metadata_validator.py` + `modules/data_validation/metadata_validator.py` | **H** | — | ⚠️ **V13 (dos gemelos) no estaba en la matriz**: 219 líneas **byte a byte idénticas** (verificado con `diff`/`md5sum`). El **vivo** es `data_validation/metadata_validator.py` (lo importa `modules/auditors/v4_comprehensive.py:33` y lo re-exporta `data_validation/__init__.py`); el gemelo solo lo consumían **2 tests**. H **lo borró físicamente** (`git rm`, −219 líneas) tras repuntar los dos consumidores al vivo (`tests/data_validation/test_metadata_validator.py:15`, `tests/test_hotel_visperas_regression.py:22`) ⟹ los checks (CRITICAL `title`, HIGH `description`) siguen cubiertos. **S-H14 cerrado en la fase**: el primer `git rm` lo bloqueó la política de permisos y quedó un shim de delegación; con la autorización del usuario el archivo fue borrado |
| `modules/common/performance_status.py` | **H** (nuevo) | — | Archivo **nuevo** de la fase (27 líneas): `PERFORMANCE_OK_STATUSES` + `is_performance_api_unavailable()`. **Única** definición del criterio «¿el eje PageSpeed quedó medido?», consumida por el documento **y** por el audit — antes cada uno decidía por su cuenta (la deriva que denuncia el dossier, familia H10/A1). Lista blanca a propósito: vacío ≠ ausente (SR-H2). **Ninguna fase posterior lo duplica** (L-NC4) |
| `.env` | **H** (documentación) | — | ⚠️ **NO EDITADO** (regla transversal del README + DA5: V12 es decisión **OPS**, no de código). `git diff --stat .env` = **vacío**. Lo que hizo H fue **medir y documentar**: `PAGESPEED_API_KEY` = 39 chars (válida), `GOOGLE_PAGESPEED_API_KEY` = 3 chars (`xxx`, placeholder inválido), `GOOGLE_API_KEY` ausente; cadena de fallback en `modules/data_validation/external_apis/pagespeed_client.py:25`. Ver `09-documentacion-post-proyecto.md` §E (nota OPS) |
| `AGENTS.md` | **D**, **RELEASE** | D → RELEASE | D3 corrige la tabla Módulos Activos y el bloque FASE 4.5; RELEASE corre `sync_versions.py` sobre el mismo archivo |
| `VERSION.yaml` | **RELEASE** únicamente | — | Ninguna fase intermedia toca la versión |

**Regla**: ninguna sesión puede editar un archivo cuya fase dueña anterior no esté ✅ en
`06-checklist-implementacion.md`. Si una fase necesita tocar un archivo "protegido", lo registra como
seguimiento abierto en `10-analisis-post-implementacion.md` y NO lo edita.

---

## 4. Paralelización permitida (dentro de una fase)

R1 prohíbe paralelizar **fases**. Dentro de una fase, la delegación paralela es:

| Fase | Tracks paralelos | Integración |
|------|------------------|-------------|
| **D** | Track 1 (D1+D2 estructura de severidad, DIRECTO) ‖ Track 2 (D3 corrección documental, DELEGADO) | Parent hace D4 (candado) y verifica que D3 y D1 queden en el **mismo commit** |
| **E** | ~~Subagente 1 (E1 snapshot) ‖ Subagente 2 (E2 asset_path)~~ **Secuencial E1 → E2** | ⚠️ Corregido 2026-09-03: ambos tracks editan `main.py` → no paralelizables (L-D1/S-B15). E1/E2 delegados en secuencia; parent hace E3 (tests) + E4 (censo de los 6 consumidores, solo lectura) |
| **H** | ~~Subagente 1 (H1+H2 en `pain_solution_mapper`/`v4_proposal_generator`) ‖ Subagente 2 (H3+H4 en `v4_diagnostic_generator`/`metadata_validator`)~~ **Re-partido por ARCHIVOS DISJUNTOS** | ⚠️ **Corregido 2026-09-04**: la predicción de esta fila era imposible de ejecutar tal como estaba — **H1 (V7) y H3 (V8) comparten `pain_solution_mapper.py`**, y **H2 (V6) y H3 (V11) comparten `v4_diagnostic_generator.py`**; `v4_proposal_generator.py` nunca entró en el alcance de H (lo dice su propio prompt). Reparto real: **Subagente 1** = mapper (**V7 + V8**) · **Subagente 2** = generador (**V6 + V11-lado-documento**) · **Parent** = **V11-lado-audit** (`v4_comprehensive.py`) + **V13** (`metadata_validator.py`) + **V12** (documentación OPS, sin editar `.env`). La verificación de solapamiento quedó a cargo del parent y **no hubo conflicto de regiones** (S23: la fila se corrigió en el sitio, no en el prompt, que quedó histórico). Misma clase de defecto que E1/E2 → **S-E1 / L-H2** |
| **I** | Subagente único para I2 (comando largo, timeout 900, notify) | Parent hace I1 (pre-flight), I3 (evidencia) e I4 (comparación) |

Fases **A, B, C, F, G, VERIFY**: sin paralelización (decisión arquitectónica o juicio de plan).

---

## 5. Puntos de no-retorno

| Punto | Qué se cierra | Consecuencia si se rompe |
|-------|---------------|--------------------------|
| Fin de **FASE-A** | El registro canónico existe y los ≥9 derivan de él | Cualquier fase posterior que cree una tabla paralela re-fosiliza el drift (L-NC4) |
| Fin de **FASE-C** | ✅ **Alcanzado 2026-09-03** (`c1bf5e2` + `552c190`) — `no_breach = 0` por construcción **y** complemento siempre-activo fuera del denominador de `assets_are_justified` | Volver a la lista estática re-introduce **las dos** caídas a la vez: la tautología de coverage (`total − no_breach` se auto-anula) y el `is_coherent = false` estructural. ⚠️ **Mecanismo corregido**: no era el que decía B5 (`promised_assets_exist`, que pasa en 1.0) sino `assets_are_justified = 0.75` → `severity="error"` → `errors` no vacío → `is_coherent=False` en **toda** corrida. Revertir C vuelve a dejar el denominador con un asset que **nunca** puede justificarse (`pain_ids=[]` ⟹ `any()` siempre False) |
| Fin de **FASE-D** | Severidad 11+2 en código **y** en docs, mismo commit | Docs y código vuelven a divergir (estado actual: docstrings dicen 10+3, código bloquea con 13) |
| Fin de **FASE-F** | `is_coherent` respetado o eliminado con decisión registrada | La deuda P9 (la más grave) sigue abierta y ningún acta futura hereda el veredicto real |
| **FASE-I** | Única corrida E2E del plan | Si falla, no hay segunda oportunidad presupuestada: se registra la anomalía, se clasifica (regresión vs infraestructura) y se decide en VERIFY · **✅ corrida 2026-09-04 sin fallo: EXIT_CODE 0 en 174 s, comparación 14/16, 2 FAIL con causa raíz medida (S-I1/S-I2) y 0 diferencias cerradas como «variación natural»** |
