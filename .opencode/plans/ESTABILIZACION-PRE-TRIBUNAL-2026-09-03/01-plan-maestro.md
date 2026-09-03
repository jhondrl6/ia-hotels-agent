# 01 — Plan Maestro: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03

> **Versión objetivo**: 4.75.0 · **Workflow**: `phased_project_executor.md` v2.18.0
> **Fuente**: `.opencode/context/CONTEXT-AUDITORIA-BRECHAS-VS-MODULOS-SALENTOREAL-2026-09-03.md`
> **Reglas activas**: R1 (una fase/sesión) · R2 (≤60 iteraciones/fase) · R3 (≤4 tareas de fix ó 3 tareas + 1 comando largo)

---

## 1. Secuencia y presupuesto

| # | Fase | Complejidad | Modo | Tareas (R3) | Presupuesto iter. | Depende de |
|---|------|-------------|------|-------------|-------------------|------------|
| 1 | FASE-A | ALTA | DIRECTO | 4 | 55 | — |
| 2 | FASE-B | MEDIA-ALTA | DIRECTO | 3 | 40 | A |
| 3 | FASE-C | **MÁXIMA** | DIRECTO | 4 | **60 (tope R2)** | A, B |
| 4 | FASE-D | MEDIA | MIXTO | 4 | 35 | A |
| 5 | FASE-E | MEDIA | DELEGADO | 4 | 30 | B |
| 6 | FASE-F | MEDIA-ALTA | DIRECTO | 4 | 45 | C, E |
| 7 | FASE-G | MEDIA-ALTA | DIRECTO | 4 | 50 | F |
| 8 | FASE-H | BAJA-MEDIA | DELEGADO | 4 | 35 | B, F, G |
| 9 | FASE-I | BAJA (impl) | MIXTO | 3 + 1 largo | 25 | A-H ✅ |
| 10 | FASE-VERIFY | MEDIA | DIRECTO | 4 | 40 | I |
| 11 | FASE-RELEASE-4.75.0 | BAJA | DELEGABLE | 4 | 25 | VERIFY |

**Total**: 11 sesiones. Presupuesto máximo teórico 440 iteraciones; R2 impone ≤60 por fase (ninguna lo excede).

**Punto de partición predefinido** (no improvisar en la sesión): si FASE-C agota su presupuesto,
partir en **C1** (contrato + propuesta dinámica en `v4_proposal_generator`) y **C2** (propagación a
matriz/gate/`alignment_result` + medición del delta). Las sesiones siguientes se re-numeran y el
cambio se registra en `10-analisis-post-implementacion.md` §Decisiones.

---

## 2. Detalle de tareas por fase

### FASE-A — Fuente única de identidad servicio↔asset↔pain (V2/V3/V14)

**Complejidad: ALTA.** Censo y unificación de ≥9 registros con consumidores vivos en 6 módulos.
El riesgo no es escribir el registro, es migrar sin romper `conditional_generator`,
`v4_diagnostic_generator`, `pain_ledger` y `proposal_asset_alignment` simultáneamente.

| # | Tarea | Archivos | AC |
|---|-------|----------|-----|
| A1 | **Censo**: inventariar los ≥12 registros con sus derivaciones reales (quién escribe, quién lee, qué copia de qué; los 9 del dossier + 3 añadidos por la auditoría del plan — ver nota bajo la tabla). Salida: tabla en `evidence/FASE-A/censo-registros.md` | `proposal_asset_alignment.py:22` `PROPOSAL_SERVICE_TO_ASSET` · `pain_solution_mapper.py:60` `PAIN_SOLUTION_MAP` + `:311` `ASSET_NAMES` · `v4_diagnostic_generator.py:135-157` `ELEMENTO_KB_TO_PAIN_ID` · `conditional_generator.py:234-257` `PAIN_TO_ASSET` · `v4_proposal_generator.py:1281-1289` `service_brecha_candidates` + `:1365-1372` `ASSET_TO_PAIN_ID` · `pain_ledger.py:52-94` `NORMALIZATION_RULES`/`PAIN_TO_PRESENCE_ASSET` · `service_catalog` · **(auditoría)** `v4_diagnostic_generator.py:3543-3546` `pain_to_type` (fallback silencioso `cms_defaults`) · `opportunity_scorer.py:113-202` tablas de brechas · `gap_analyzer.py:199-201` (legacy) | AC1 |
| A2 | **Registro canónico** + contract tests. Decisión de diseño: dónde vive y cuál es su forma mínima. Guardrail **L-NC4**: NO crear tablas paralelas nuevas — el registro debe ser consumido por la narrativa, no duplicado para ella | Nuevo módulo (ubicación = decisión de A1) + `tests/common/test_service_identity_registry.py` | AC1 |
| A3 | **Migrar consumidores aguas arriba**: que deriven del canónico en vez de mantener copia. Corregir los 6 IDs fantasma de V2 (`no_speakable`, `no_llms_txt`, `ia_crawler_blocked` vs `ai_crawler_blocked`, `weak_brand_signals`, `no_entity_schema`, `no_factual_data`) y la perla de V3 (`ASSET_TO_PAIN_ID["monthly_report"] → "no_faq_schema"`) | `conditional_generator.py:314-326` · `pain_ledger.py:52-94` · `proposal_asset_alignment.py:22,219,609,792` | AC1, AC3 |
| A4 | **Migrar consumidores aguas abajo** + corregir el drift «8 vs 7» en sus **tres** copias, con test de contrato narrativa↔fuente (no valores fijos, L-NC10) | `proposal_asset_alignment.py:35-37` · `service_catalog` · `v4_proposal_generator.py:1332` · `v4_diagnostic_generator.py:160,3067-3086` + **(auditoría)** `v4_diagnostic_generator.py:3543-3546` `pain_to_type` y `opportunity_scorer.py:113-202` (ver nota bajo la tabla) | AC2 |

**Complejidad ALTA porque**: dos de los registros (A3/A4) alimentan narrativa comercial visible; un
error de migración cambia lo que se le promete al cliente, no solo un conteo interno.

> **Nota de auditoría del plan (2026-09-03) — el censo de 9 no era completo.** Existe un tercer universo
> con los mismos nombres fantasma: (1) `opportunity_scorer.py:113-202` mantiene tablas de brechas con
> `no_llms_txt`, `ia_crawler_blocked`, `weak_brand_signals` — verificado contra código vivo; (2)
> `pain_to_type` (`v4_diagnostic_generator.py:3543-3546`) mapea pain_ids con 10 entradas y un
> **fallback silencioso a `cms_defaults`** para cualquier pain no listado — misma familia que V6 y que
> `precision_tier` defaulteando a `"C"`. El scorer es consumidor vivo de v4complete (invocado en
> `v4_diagnostic_generator.py:3536`; sus `opportunity_scores` alimentan la columna «Problema que
> resuelve», hallazgo V4): si FASE-C deriva la propuesta del ledger pero `pain_to_type`/el scorer siguen
> con IDs no canónicos, la columna comercial mostrará scoring equivocado para los pains que FASE-B
> recién active. Por eso: `pain_to_type` + tablas del scorer se **migran en A3/A4** (consumidor aguas
> abajo); `gap_analyzer.py:199-201` (universo spark, deprecado) se **declara legacy** con decisión
> registrada en el censo, no se migra; `asset_responsibility_contract.py` (identidad por filename
> CORE↔GEO, citado en dossier §11) se evalúa en el censo. Consecuencia en AC1: el grep de IDs fantasma
> se aplica a los **universos migrados** (`modules/commercial_documents` + `modules/asset_generation`);
> los registros fuera de alcance requieren decisión explícita (migrar/legacy) en el censo, no grep=0.

---

### FASE-B — Biyección mapa↔emisión de `detect_pains` (V1)

**Complejidad: MEDIA-ALTA.** El código es sencillo; la dificultad es la **decisión de producto** por
cada uno de los 9 pains muertos (implementar la detección ⟹ nueva brecha vendible, o retirarla del
mapa ⟹ dejar de prometerla).

V1 verbatim: además de `missing_llmstxt`, `detect_pains` nunca emite `no_motor_reservas`, `no_ssl`,
`no_schema_reviews`, `missing_alt_text`, `no_monthly_report`, `no_blog_content`, `no_social_links`,
`low_content_length`. El mapa declara **27** (C5), `detect_pains` implementa **~18**.

| # | Tarea | Archivos | AC |
|---|-------|----------|-----|
| B1 | **Decisión por pain muerto**: tabla de 9 filas — implementar / retirar / diferir, con justificación y señal de dato necesaria. Salida: `evidence/FASE-B/decision-pains-muertos.md` | — (análisis) | AC4 |
| B2 | **Ejecutar la decisión**: puntos de emisión reales en `detect_pains` para los que se implementan; retiro del mapa para los que no. `missing_llmstxt` es caso confirmado: el asset se genera y el sitio no tiene `llms.txt` (`ia_readiness llms_txt=0`), pero ninguna rama lo emite | `pain_solution_mapper.py:339` `detect_pains` · `:60` `PAIN_SOLUTION_MAP` · `:160-168` `missing_llmstxt` | AC4 |
| B3 | **Candado de biyección**: test que falla fuerte si el mapa declara un `pain_id` que `detect_pains` no puede emitir. Patrón: guardián AST de FASE-SR-A | `tests/commercial_documents/test_pain_map_bijection.py` | AC4 |

**Restricción**: NO agregar el 8º servicio al registro (§8.5 del dossier). La unificación 7→8
**empeora** `coverage_ratio` (0.571 → 0.500) — medido.

---

### FASE-C — Punto 8: propuesta dinámica (cura estructural)

**Complejidad: MÁXIMA.** Es la fase con mayor riesgo del plan y la única con probabilidad real de
agotar R2. Toca una cadena causal de 4 eslabones donde cada uno consume la salida del anterior:
propuesta → matriz → gate → `AlignmentResult`.

**Qué cura**: `no_breach = 6/7` servicios y `coverage_ratio = 1.000` algebraico (B1-B5). Al prometer
solo lo diagnosticado, `no_breach = 0` **por construcción** — no por umbrales ni por relajar gates.

| # | Tarea | Archivos | AC |
|---|-------|----------|-----|
| C1 | **Contrato de propuesta dinámica**: especificar qué significa «servicio con brecha detectada» y de qué fuente única deriva (debe ser el registro canónico de FASE-A, nunca una copia). Definir el comportamiento cuando el ledger está vacío (interacción con V9) | Diseño + `evidence/FASE-C/contrato-propuesta-dinamica.md` | AC5 |
| C2 | **Implementar en la propuesta**: `service_brecha_candidates` derivado del ledger real, no de la lista estática de 7/8 | `v4_proposal_generator.py:1281-1289` · `modules/commercial_documents/templates/propuesta_v6_template.md` (`${dynamic_services_table}` en `:52`; la ruta `templates/` raíz NO contiene este archivo) | AC5 |
| C3 | **Propagar a matriz y gate**: `no_breach` deja de ser categoría poblada; `AlignmentResult.compute_unresolved()` sigue siendo el **único** punto de cómputo (FASE-SR-A N1, sin sumas paralelas — L-NC10) | `proposal_asset_alignment.py:575,748` (los 2 builders) · `alignment_result.py:106-108,175-212,222-276` · `publication_gates.py:842` | AC5 |
| C4 | **Medir el delta** (experimento contrafactual sobre los artefactos reales de SalenteReal): `no_breach`, `coverage_ratio`, `unresolved`, `is_coherent` antes/después. Sin este delta AC5/AC6 no se certifican | `output/FASE-D_salentoreal_post_guard/v4_complete/` (lectura) + `evidence/FASE-C/delta-medido.md` | AC5, AC6 |

**Trampas conocidas que C3 debe esquivar**:
- **A5**: skip silencioso en `ProposalAssetMatrix.build` (`proposal_asset_alignment.py:609-612`,
  comentario literal *"Unknown service — skip silently"*). Un servicio nuevo que no esté en
  `PROPOSAL_SERVICE_TO_ASSET` da Δ = 0 y **parece que el cambio no hizo nada**. Falso negativo.
- El segundo builder (`:748,792-794`) tiene la **misma** ruta de silencio. Los dos builders son
  idénticos en 5/5 variantes medidas — tocar uno sin el otro re-introduce el drift.
- **P12/A3**: `promised_assets_exist` pesa **2.0 de 7.5** y está acotado por `if not generated_assets:`
  (`coherence_validator.py:670`, comentario H6 FIX) ⟹ post-gen P6.3 **no tiene verificación de score**.
  C4 no puede apoyarse en ese check para certificar P6.3.

---

### FASE-D — Severidad explícita de publication gates (H10, §8.4)

**Complejidad: MEDIA.** El patrón a copiar ya existe en el repo y es el único lugar donde la
distinción blocking/advisory está implementada: `commercial_gate.py:99-113`
(`BLOCKING_GATE_IDS` + `WARNING_GATE_IDS`).

**Decisión ya medida y cerrada** (memoria `decision-advisory-gates-2-no-3`): advisory = **2**
(`content_quality`, `proposal_asset_alignment`). **`asset_confidence` conserva su bloqueo.**
Documentación correcta: **"11 blocking + 2 advisory"**.

| # | Tarea | Archivos | AC |
|---|-------|----------|-----|
| D1 | **Estructura de severidad** en `PublicationGateManager`: listas explícitas + `check_publication_readiness` filtrando por severidad en vez de `[r for r in results if not r.passed]` plano | `publication_gates.py:181-195` (`self.gates`, dict plano de 13) · `:1919` `check_publication_readiness` · `:1967` (`blocking_gates = [r for r in results if not r.passed]`) | AC7 |
| D2 | **Piso bajo advisory**: un gate advisory que falla debe degradar el veredicto a un estado visible (no a PASS silencioso) y alimentar al **consumidor nombrado**. **(Auditoría)** el wire no existe hoy para `content_quality`: `human_checklist_generator` consume `DeliveryQualityReport`, que solo expone coverage/specificity/evidence/`proposal_asset_alignment` — exponer el resultado de `content_quality` al checklist es parte de D2 | `publication_gates.py:660` `_content_quality_gate` · `:842` `_proposal_asset_alignment_gate` · `human_checklist_generator.py` · `delivery_quality_report.py` (wire) | AC7 |
| D3 | **Mitad documental MONTADA en D1** (mismo commit, nunca por delante): docstrings + `AGENTS.md` | `publication_gates.py:4` (*"13 publication gates (10 blocking + 3 advisory)"*) · `:162` (*"manages 10 blocking gates and 3 advisory gates"*) · `AGENTS.md` tabla Módulos Activos fila `quality_gates/` + bloque FASE 4.5 | AC8 |
| D4 | **Candado de regresión sobre ambas listas**: hoy hay **0 tests** que fijen la pertenencia. Test que falla si `asset_confidence` aparece en advisory o si las listas no suman 13 | `tests/quality_gates/test_gate_severity_lists.py` | AC7, AC8 |

**Qué NO hacer** (§8.5 del dossier + memoria):
- **NO demoter `asset_confidence`**. Es hoy el único mecanismo que vuelve no-entregable un paquete
  Tier C. Relajarlo dejaría salir el 14% del histórico (4 de 29 corridas, todas
  `hotel_visperas`/`hotel_vísperas`, 2026-03-25 → 2026-04-05) con 100% de assets ESTIMATED y
  `coherence_score_final = None`.
- **NO tocar `delivery_quality_report.py:289` `BLOCKING_GATE_NAMES`**: rige el ZIP, es régimen de
  **delivery**, no de publicación.
- **NO implementar S2.3.**
- **NO corregir los docstrings antes de D1**: hoy afirman 10+3 cuando el código bloquea con los 13;
  escribir 11+2 sin tocar `check_publication_readiness` afirmaría 11+2 cuando siguen bloqueando los 13.

**Baseline a preservar**: 848 passed / 2 skipped en `tests/quality_gates` + `tests/asset_generation`.

---

### FASE-E — Auditabilidad: A2 persistir snapshot + A6 poblar `asset_path`

**Complejidad: MEDIA.** Dos tracks independientes y localizados. Delegable.

| # | Tarea | Archivos | AC |
|---|-------|----------|-----|
| E1 | **A2**: persistir `site_presence_snapshot` junto a `v4_audit/`. Hoy nace en memoria, tiene **seis** consumidores y `find output -iname "*site_presence*"` → **0 resultados**. Sin esto T0.2 del ROADMAP no es retro-testeable | `main.py:2490-2500` (nacimiento) + writer en `v4_audit/` | AC9 |
| E2 | **A6**: poblar `asset_path` en el caller del builder. Hoy llega `null` al reporte de delivery | `delivery_quality_report.py:223` (`asset_path=e.get("asset_path")`) + caller aguas arriba | AC9 |
| E3 | **Tests retro-testeables** de ambos: fixture que carga un snapshot persistido y verifica los 6 consumidores; test de `asset_path` no nulo | `tests/quality_gates/test_delivery_asset_path.py` + `tests/test_site_presence_persistence.py` | AC9 |
| E4 | **Verificar los 6 consumidores**: que lean el snapshot persistido y no reconstruyan uno propio (interacción con A4, que FASE-F unifica) | grep de consumidores + `evidence/FASE-E/consumidores-snapshot.md` | AC9 |

**Delegación**: 2 subagentes en paralelo (E1 ‖ E2), parent integra E3/E4. Justificación: replican un
patrón de persistencia ya existente en el repo, sin decisión de diseño.

---

### FASE-F — A4 oráculo único + A1 `skipped ≠ passed` + N11 `is_coherent`

**Complejidad: MEDIA-ALTA.** N11 es la deuda **más grave** abierta (P9) y es decisión arquitectónica.

| # | Tarea | Archivos | AC |
|---|-------|----------|-----|
| F1 | **A4/V15 — un oráculo de presencia para decidir Y narrar**. Hoy dos criterios divergen: `_presence_resolved` (permisivo) absorbió 3 de los 6 NO_BREACH moviéndolos a `present`, por eso `details` dice «2 missing» (oráculo estricto) mientras la matriz dice otra cosa. La narrativa debe derivarse de la decisión, no de un segundo criterio | `alignment_result.py:62` `_presence_resolved` · `:222-276` `_from_entries` | AC10 |
| F2 | **A1 — `skipped ≠ passed`**. G9 se salta **en verde**: el summary cuenta skipped como passed y `BLOCKING_GATE_NAMES` decide con `not passed` ⟹ nunca bloquea. Unificar también el segundo default | `delivery_quality_report.py:251-255` (`"skipped": True`) · `:310-319` (summary) · `:325` (segundo default) · `:289,292,296` | AC11 |
| F3 | **N11/P9 — el gate de coherencia respeta `is_coherent`**. Hoy `_coherence_gate` decide con **solo** `coherence_score >= threshold`; el módulo que sí lee `is_coherent` está **huérfano** (sin importadores fuera de sí mismo). Los **3** artefactos de SalenteReal con ese campo (6 copias: raíz + `deliveries/ASSETS`) dicen `is_coherent: false` y el paquete salió `READY_FOR_PUBLICATION` con ZIP de 46.552 B / 37 archivos | `publication_gates.py:458` `_coherence_gate` · `:1855` `_extract_coherence_score` · `coherence_gate.py` (huérfano: conectar o eliminar) | AC12 |
| F4 | **Verificación de que el cambio no voltea veredictos indebidamente**: reproducir el caso SalenteReal (score 0.88 + `is_coherent: false`) y confirmar el nuevo comportamiento; correr el corpus de 27 corridas para medir cuántas cambian de veredicto | Test de reproducción + `evidence/FASE-F/impacto-corpus.md` | AC12 |

**Decisión arquitectónica de F3** (registrar en `10-analisis` §Decisiones): respetar `is_coherent`
**o** eliminarlo a favor de sus checks. No dejar la doble fuente. Nota del dossier: agregar errores al
reporte de coherence **no bloquea nada** hoy, y ningún acta que se alimente de ese reporte hereda el
veredicto real.

**Advertencia medida**: el cambio de denominador de `coverage_ratio` **no es un fix, es un interruptor
global** — bloquea en 10/10 configuraciones medidas y es insatisfacible por medios honestos. F1 NO
debe tocar esa fórmula; el veredicto bloqueante queda en `unresolved`.

---

### FASE-G — Ceguera de gates (Nivel 3.7)

**Complejidad: MEDIA-ALTA.** V5 lleva advertencia anti-reversión explícita.

| # | Tarea | Archivos | AC |
|---|-------|----------|-----|
| G1 | **Cablear `doc_audit_consistency`**: único gate doc-vs-audit; llegó sin `audit_data`/`diagnostico_text` en el assessment → PASSED con `value=null` pese a que `audit_report` existía en disco. Además su Check 2 espera `gbp.reviews` como dict `{"total":...}` y el audit trae `986` int | `publication_gates.py:1464-1514` · caller en `main.py` / `assessment_builder.py` | NR1 |
| G2 | **Ampliar `_identify_critical_issues`**: hoy solo consulta schema/whatsapp/`geo_score<50`/perf con `field_data`. Ni PageSpeed `status=ERROR` ni banda GEO `critical` (29/100) califican ⟹ `critical_recall = 1.0` vacuo | `v4_comprehensive.py:1789-1814` · `publication_gates.py:528` `_critical_recall_gate` · `:1864` `_extract_critical_recall` | NR2 |
| G3 | **Cerrar escotilla V5** — `ASSET_GENERATED` en `_JUSTIFIED_STATUSES` deja pasar un asset generado pero **no mencionado** en el doc. ⚠️ **Anti-reversión**: ese estatus fue el fix de **BUG-6/N2 (Zione, 2026-07-25)**. La corrección debe **distinguir** «generado y mencionado» de «generado y silencioso», NO quitar `ASSET_GENERATED` | `publication_gates.py:1244` `_coverage_gate` · `_JUSTIFIED_STATUSES` | NR3 |
| G4 | **Cerrar escotilla V9** — ledger vacío pasa como PASS cuando debería ser BLOCKED. Interacción directa con C1 (comportamiento del punto 8 ante ledger vacío) | `publication_gates.py:1244-1373` | NR4 |

**Tautología que G3/G4 NO pueden curar sollas**: `coverage_no_silent_drop` compara
`len(pain_ledger_resolved)` contra brechas del doc, y **ambos salen de la MISMA llamada `detect_pains`**
(`v4_asset_orchestrator.py:280`; `v4_diagnostic_generator.py:3178`, DEP-03). La brecha que no entra al
ledger es **invisible** por construcción. La cura real es FASE-A/B/C; G3/G4 cierran las escotillas que
quedan.

---

### FASE-H — Quirúrgicos (Nivel 3.8)

**Complejidad: BAJA-MEDIA.** Seis ediciones independientes y localizadas. Delegable.

| # | Tarea | Archivos | Hallazgo |
|---|-------|----------|----------|
| H1 | **V7** — reemplazar el guard `hasattr(direct_field.value, '__iter__')` por validación numérica con normalización de unidades y uso de `ota_field`. Hoy `low_ota_divergence` (HIGH, priority 1) **no puede disparar** con valor numérico: el guard excluye float/int y el pipeline conoce `direct_channel=0.2` ("default"). Triple defecto | `pain_solution_mapper.py:453` | V7 |
| H2 | **V6** — `except Exception: return brechas` de `_identify_brechas` + caché → logging + estado visible. Hoy degrada en silencio (misma familia que el NameError de `tier_c` y que `precision_tier` defaulteando a `"C"`) | `v4_diagnostic_generator.py:3189-3194` | V6 |
| H3 | **V8** — deduplicar `low_organic_visibility` + **V11** — residuos D6 de la cadena de presentación de PageSpeed | `pain_solution_mapper.py:677-701` · `v4_diagnostic_generator.py:1945-1952` | V8, V11 |
| H4 | **V13** — unificar los dos `MetadataValidator` gemelos + **V12** — **documentar** (no editar) la decisión OPS del placeholder inválido en `.env` | `data_validation/metadata_validator.py` · `modules/data_validation/metadata_validator.py` · `09-documentacion-post-proyecto.md` | V13, V12 |

**V12 es decisión OPS, no de código**: el placeholder inválido de 3 caracteres sigue en `.env` como
trampa latente — si se elimina `PAGESPEED_API_KEY`, el fallback vuelve a resolver la inválida y el
síntoma reaparece. Se documenta; no se edita `.env` en una fase de refactorización.

**Contexto que H3 debe respetar**: la corrida auditada (2026-08-31 **12:28**) es **anterior** al cierre
del fix OPS de PageSpeed (~**15:08**, commits `f914e0e`/`f77f8ae`, release v4.74.0). Por eso el doc aún
muestra el error de la key — la corrección de credenciales llegó después, no falta por hacer. Lo que
**sí** sigue abierto y ningún ciclo previo abordó: (a) la capa de pain descarta el ERROR sin pain ni
justificación (`poor_performance` exige `mobile_score is not None`, `pain_solution_mapper.py:416-417`);
(b) el doc inserta el string crudo en inglés del API en vez del mensaje sanitizado que CONTEXT-H
especificó; (c) esa fila vive en una tabla sin header ni separador; (d) `execution_trace` lista
`pagespeed_api` en `executed` Y en `skipped` simultáneamente.

---

### FASE-I — E2E ÚNICA: Hotel Salento Real

**Complejidad: BAJA (implementación).** Es la **única** ejecución de `v4complete` de todo el plan —
por diseño explícito del usuario. Todas las fases A-H validan con tests y fixtures.

**Objetivo de negocio**: demostrar sobre una corrida real que los fixes fueron superados.

| # | Tarea | Detalle |
|---|-------|---------|
| I1 | **Pre-flight** (parent) | grep de símbolos no definidos en ramas nuevas antes del run · validadores en verde (`run_all_validations.py --quick`, `validate_agents_md.py`) · confirmar que `.env` tiene `PAGESPEED_API_KEY` canónica sembrada (si no, el run reproducirá el error de PageSpeed y contaminará la comparación) |
| I2 | **Comando largo** (subagente, timeout 900, notify) | `./venv/Scripts/python.exe main.py v4complete --url https://www.hotelsalentoreal.com/ --output output/FASE-I_salentoreal_post_estabilizacion` |
| I3 | **Protocolo de Evidencia Proactiva** (parent, INMEDIATO) | Copiar a `evidence/FASE-I/`: `v4_complete_report.json`, `asset_generation_report.json`, `gate_report_*.json`, `commercial_gates_report.json` **Y** `commercial_gates_report_diagnostic_*.json`, `pain_ledger*.json`, `proposal_asset_matrix.json`, `delivery_quality_report.json`, `coherence_validation.json`, `01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md`, `02_PROPUESTA_COMERCIAL_*.md`, el ZIP si se genera, y el **nuevo** `site_presence_snapshot` de A2 |
| I4 | **Comparación contra baseline** (parent) | Baseline: `output/FASE-D_salentoreal_post_guard/v4_complete/` (coherence **0.88**, 13/13 gates, 2026-08-31 12:28). Verificar AC5/AC6 (no_breach, coverage_ratio, is_coherent), AC9 (snapshot persistido + asset_path), AC12 (veredicto coherente con `is_coherent`), NR1-NR6 |

**Restricciones de I2**:
- Correr **CON DEFAULTS**, sin poblar `clientes/` — el baseline H2 corrió con defaults
  (`direct_channel_percentage: "default"`, Tier B evidence) y no existe YAML de onboarding de Salento
  Real en el repo. Fabricar onboarding rompería la equivalencia (lección F5 de VALIDADOR-URL-PROPIA).
- Rutas explícitas en los `cp` (Git Bash sin globstar; la estructura es anidada `v4_complete/...`).
- Si el run falla por infraestructura (gemini 403, PageSpeed key), clasificar como **anomalía
  preexistente** y no como regresión del plan — igual que FASE-D del plan anterior.

**Nota sobre el nombre del sitio**: el usuario lo identificó como *"Hotel Salento Real | Quindio,
Colombia - Web Oficial"* (título de la ficha). La URL canónica verificada en el baseline y en el estado
persistido (escrito en `main.py:1433` vía `MemoryManager().save_state`; reinyección en `main.py:226-227`;
el string `last_url` no aparece en `agent_harness/memory.py`) es `https://www.hotelsalentoreal.com/`. El guard
`own_site_guard` de v4.74.0 la acepta (sitio propio, no OTA).

---

### FASE-VERIFY — Certificación formal + análisis post-implementación

**Complejidad: MEDIA.** **DIRECTO y no delegable** (executor §4.6: requiere juicio y contexto completo
del plan).

| # | Tarea | Salida |
|---|-------|--------|
| V1 | Certificar **AC1-AC12** uno por uno contra evidencia real de `evidence/FASE-*/` — no contra citas de código | Matriz en `10-analisis-post-implementacion.md` §Verificación |
| V2 | Certificar **NR1-NR6** (no-regresión) contra la corrida FASE-I y el baseline | Ídem |
| V3 | **Análisis post-implementación explícito de que los fixes fueron superados**: por cada hallazgo del dossier (8 caídas silenciosas, 3 candados rotos, A1-A6, V1-V16, H10/P9/P10/P12/H7/H9) → estado final + evidencia + qué test lo fija | `10-analisis-post-implementacion.md` §Fixes superados |
| V4 | **Lecciones aprendidas** (formato: qué pasó / por qué / qué lo previene + pertinencia INCLUIR/EXCLUIR) y write-back a QMind `iah-cli-lecciones` si alguna es durable | `10-analisis-post-implementacion.md` §Lecciones |

**Regla de oro de V1** (lección ROADMAP v4.0→v4.1): *la verificación formal da falsa confianza* — los
validadores en verde verifican **forma**, no premisas. Cada AC se certifica contra una **salida real**,
no contra la presencia de un string en el código.

---

### FASE-RELEASE-4.75.0 — Cierre documental

**Complejidad: BAJA.** **DELEGABLE** (solo YAML/MD + scripts, sin imports del proyecto).

| # | Tarea | Herramienta |
|---|-------|-------------|
| R1 | Version bump `4.74.1 → 4.75.0` + codename + `release_date` | `VERSION.yaml` |
| R2 | CHANGELOG con formato CONTRIBUTING (`### Objetivo / ### Cambios / ### Archivos Nuevos / ### Archivos Modificados / ### Tests`) desde `09-documentacion-post-proyecto.md` | manual + datos de 09 |
| R3 | `log_phase_completion.py --release` + `sync_versions.py` (6 archivos) + GUIA_TECNICA con nota técnica por fase + DOMAIN_PRIMER **auto-regenerado** (`doctor.py --regenerate-domain-primer`) | scripts |
| R4 | Validaciones finales: `run_all_validations.py --quick` (7/7) + `validate_agents_md.py` (6 PASS / 0 FAIL) + `validate_document_integration.py` | scripts |

**Regla**: NO ejecutar planes de documentación directamente — SIEMPRE el flujo
`log_phase_completion.py` → `sync_versions.py` → CHANGELOG → GUIA_TECNICA → `run_all_validations.py`
(AGENTS.md §Flujo Documental Obligatorio).

---

## 3. Análisis de complejidad — justificación por fase

| Fase | Complejidad | Justificación | Riesgo principal | Mitigación |
|------|-------------|---------------|------------------|------------|
| A | ALTA | ≥9 registros, consumidores en 6 módulos, dos alimentan narrativa comercial visible | Romper un consumidor y cambiar lo que se promete al cliente | A1 censo antes de escribir; contract tests primero (TDD) |
| B | MEDIA-ALTA | Código sencillo, decisión de producto por pain (9 filas) | Implementar detecciones sin señal de dato real ⟹ pains que disparan en falso | B1 tabla de decisión con señal de dato exigida |
| C | **MÁXIMA** | Cadena causal de 4 eslabones; cura la causa raíz estructural | Agotar R2; o que A5 (skip silencioso) produzca Δ = 0 y parezca que no hizo nada | Punto de partición C1/C2 predefinido; C4 mide el delta explícitamente |
| D | MEDIA | Patrón existente en el repo (`commercial_gate.py:99-113`) | Corregir docstrings antes que el comportamiento (cambia una falsedad por otra) | D3 montada en D1, mismo commit |
| E | MEDIA | 2 tracks localizados de persistencia | Persistir en un formato que los 6 consumidores no puedan leer | E4 verifica los 6 consumidores |
| F | MEDIA-ALTA | N11 es la deuda más grave (P9); A4 unifica dos criterios vivos | Voltear veredictos indebidamente en el corpus histórico | F4 mide impacto sobre 27 corridas antes de cerrar |
| G | MEDIA-ALTA | V5 lleva anti-reversión de un fix de 2026-07-25 | Re-introducir BUG-6 al cerrar la escotilla | G3 distingue «generado y mencionado» de «generado y silencioso» |
| H | BAJA-MEDIA | 6 ediciones independientes con patrón fijado | Conflicto de archivo con G en `pain_solution_mapper.py` | `dependencias-fases.md` fija el orden G→H |
| I | BAJA | Comando largo + comparación | Run contaminado por infraestructura (PageSpeed/gemini) | I1 pre-flight verifica `.env` |
| VERIFY | MEDIA | Juicio sobre 18 criterios | Certificar por forma y no por premisa | Regla de oro V1 |
| RELEASE | BAJA | YAML/MD + scripts | Olvidar pasos obligatorios de CONTRIBUTING | R3/R4 con checklist de AGENTS.md |
