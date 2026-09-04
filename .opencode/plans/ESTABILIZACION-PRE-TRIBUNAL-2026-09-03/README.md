# ESTABILIZACION-PRE-TRIBUNAL-2026-09-03

> **Versión publicada**: **4.75.0** «Estabilización pre-tribunal» (2026-09-04) | **Estado**: ✅ **PLAN COMPLETADO — 11/11 sesiones** (A, B, C, D, E, F, G, H, I, VERIFY, **RELEASE** ✅) + **FASE-HOTFIX-PRE-RELEASE ✅** el mismo día, sesión extra fuera del conteo. **Métricas de cierre medidas en RELEASE**: ACs **11 ✅ / 1 ⚠️ (AC10) / 0 ❌** · NRs **10 ✅ / 1 ⚠️ (NR12) / 1 ❌ (NR2)** · suite dirigida `quality_gates`+`asset_generation` **950 passed / 2 skipped** · batería de contratos A+B+C+D+delivery **180 passed / 0 failed** · `run_all_validations.py --quick` **8/8** · `validate_agents_md.py` **6/6** (S11/S-I6 cerrado: AGENTS.md 3.689/284 → **3.934 funciones / 298 archivos**) · **0 regresiones causadas por RELEASE**. **Diferidos con dueño — tribunal, no RELEASE**: **S-HF1** (AC10), mitad estructural de **S-C3** (P12) y **S-I1** (NR2 ❌). El resto del detalle por fase está en la tabla de Progreso de abajo. Detalle histórico por fase: D se ejecutó en **sesión paralela** a B sobre el **mismo working tree**, fuera del camino crítico (su única dependencia dura era A); su código está commiteado en `76e0257`. El código de C está en `c1bf5e2` — **C erradicó la causa raíz del plan** (punto 8: propuesta dinámica ⟹ `no_breach` 6→0, `is_coherent` False→True). El código de E está en `b0ab27a` (A2 oráculo persistido + A6 `asset_path` poblado, AC9). El código de F está en `23d0978` (A4 oráculo único + A1 skipped≠passed + N11/P9 gate respeta `is_coherent`; H8 `publication_state.py` eliminado; AC10/AC11/AC12). El código de G está en `c317cda` (NR1-NR4: `doc_audit_consistency` cableado con `audit_data` + `NOT_EVALUATED`, `critical_recall` no vacuo con PageSpeed ERROR y banda GEO, escotillas V5/V9 cerradas sin revertir BUG-6). El código de **H** (Nivel 3.8, seis quirúrgicos) está en el árbol de trabajo de su sesión: **V6** (`except Exception` silencioso → traceback + estado `NOT_EVALUATED` visible en el documento y el caché ya no se envenena), **V7** (guard `__iter__` → validación numérica con normalización de unidades; `low_ota_divergence` **ya puede disparar**), **V8** (dedup de `low_organic_visibility`: un solo punto de emisión), **V11** (residuos D6 en el documento **y** en la fuente, con criterio compartido en `modules/common/performance_status.py`), **V13** (gemelo `MetadataValidator` **borrado**, −219 líneas) y **V12 documentado, NO editado** (`.env` intacto, es decisión OPS). ⚠️ H tuvo que **re-partir su delegación por archivos disjuntos** porque dos tracks compartían `pain_solution_mapper.py` y `v4_diagnostic_generator.py` (S-E1 otra vez → L-H2). Fuente del estado por fase: la tabla de Progreso de abajo + `06-checklist-implementacion.md`.
>
> ⚠️ **Conflicto de concurrencia registrado (2026-09-03)**: esta línea llegó a afirmar que «FASE-B ✅ era falso, B sigue pendiente», escrita por la sesión de FASE-D cuando el trabajo de B aún no estaba commiteado. Era incorrecto: B está completa y su evidencia es re-ejecutable (`evidence/FASE-B/`, candado `tests/commercial_documents/test_pain_map_bijection.py` en verde). **Dos sesiones editando los mismos documentos de plan producen esta sobrescritura** → seguimiento **S-B15** en `10-analisis-post-implementacion.md` §5.
> **Workflow**: `phased_project_executor.md` v2.18.0 (R1: una fase/sesión, R2: ≤60 iteraciones, R3: ≤4 tareas de investigación/fix ó 3 tareas + 1 comando largo)
> **Contexto fuente**: `.opencode/context/CONTEXT-AUDITORIA-BRECHAS-VS-MODULOS-SALENTOREAL-2026-09-03.md` (dossier de estabilización pre-tribunal, 717 líneas)
> **Anclaje estratégico**: `ROADMAP.md` v4.2 §7.2 (FASE T) y §13 (deudas P9/P10/P12/H7/H9/H10)
> **Paso 0 completado**: 8 fuentes QMind `iah-cli-lecciones` + 3 memorias de proyecto releídas (ver §Reglas transversales)

## Problema (una causa raíz, tres manifestaciones)

El diagnóstico SalenteReal del 2026-08-31 fue auditado contra los artefactos reales del mismo run y
contra código vivo. Veredicto del dossier: **~50 de ~60 afirmaciones confirmadas**, y una causa raíz
única con tres manifestaciones:

| Capa | Manifestación | Evidencia |
|------|---------------|-----------|
| **Aguas arriba** | Módulos que detectan pero no llegan al ledger → 8 caídas silenciosas (ni brecha ni justificación) + 9 pains declarados que `detect_pains` nunca emite (V1) | dossier §4, §12.3 V1 |
| **Medio** | Doc/propuesta tautológicos que **venden lo no diagnosticado**: `no_breach = 6/7` servicios, `coverage_ratio = 1.000` algebraicamente | dossier §9.2 B1-B5 |
| **Aguas abajo** | Gates ciegos: `coverage_no_silent_drop` compara el ledger consigo mismo; `doc_audit_consistency` llegó sin datos y pasó en verde; `critical_recall = 1.0` vacuo; `is_coherent: false` ignorado y aun así salió `READY_FOR_PUBLICATION` con ZIP | dossier §3, §5 |

**Causa raíz nominal** (dossier §12.5, verbatim): *"contrato de detección fragmentado y sin candado —
≥9 registros no canónicos, consumidores derivan de copias parciales, 0 tests fijan la biyección."*

Consecuencia comercial: el paquete salió a entrega con **37 archivos / 46.552 bytes** declarando
coherencia mientras sus **3** artefactos con ese campo (6 copias en disco: raíz + `deliveries/ASSETS`)
decían `is_coherent: false`. Eso es exactamente lo que
P6/P7 del ROADMAP existen para impedir.

## Por qué este orden (no es el orden obvio)

El dossier §10 fija el orden de **precondiciones duras** del tribunal: punto 8 → A2 → A6 → N11/P9 → H10.
ROADMAP §7.2 añade una restricción que el dossier no enuncia: *"decidir cuál registro manda es
precondición de la propuesta dinámica"*.

Ambos se reconcilian así: **la fuente única de identidad va PRIMERO** (FASE-A/B), porque el punto 8
(FASE-C) necesita un registro del que derivar la promesa; de lo contrario la propuesta dinámica se
construiría sobre una de las ≥9 copias parciales y reproduciría el drift que FASE-SR-B ya resolvió
una vez. **Matiz verificado contra el dossier (auditoría del plan)**: el §10 marca un «orden sugerido»
(punto 8 → A2 → A6 → N11/P9 → H10) y este plan **adelanta deliberadamente H10** (FASE-D) a la posición
4, antes de A2/A6/N11 — no lo preserva. Justificación del adelanto: H10 es independiente de B/C, su
semántica de severidad es insumo de F3 (N11) y del tratamiento de ledger vacío (G4), y su corrección
conductual/documental acoplada elimina temprano el régimen contradictorio 10+3/13/11+2. El resto del
orden relativo (A2/A6 → E, N11/P9 → F) sí respeta el §10.

Nivel 3 del dossier (§12.5 puntos 7-8) va **después**: el propio dossier lo califica como
*"completitud del diagnóstico, faseable"* — no es precondición del tribunal.

## Fases (11 sesiones: 9 implementación + VERIFY + RELEASE)

| Fase | Sesión | Objetivo | Complejidad | Modo de ejecución | Comando largo |
|------|--------|----------|-------------|-------------------|---------------|
| FASE-A | 1 | Fuente única de identidad servicio↔asset↔pain: censo de los ≥9 registros, registro canónico, contract tests (guardián AST), migración de consumidores. Corrige V2/V3/V14 | **ALTA** | **DIRECTO** (decisión arquitectónica cross-module: cuál registro manda — no delegable, lección DT-3) | No |
| FASE-B | 2 | Biyección **triple** mapa↔emisión↔narrativa (V1 + N-A1): decidir por cada uno de los **11** pains sin narrativa (9 muertos + 2 que se emiten y se descartan) si se implementa, se narra o se retira del mapa + candado tridireccional | **MEDIA-ALTA** ⚠️ *(alcance agrandado por N-A1, presupuesto igual)* | **DIRECTO** (decisión de producto por pain: implementar vs retirar cambia lo que se vende) | No |
| FASE-C | 3 | **Punto 8 — propuesta dinámica** (cura estructural, §10#1): solo prometer servicios con brecha detectada ⟹ `no_breach = 0` por construcción; disuelve la tautología de coverage y el `is_coherent = false` estructural (B5) | **MÁXIMA** | **DIRECTO** (el núcleo del plan; toca propuesta + matriz + gate + alignment_result) | No |
| FASE-D | 4 | Severidad explícita de publication gates (H10, §8.4, §10#5): advisory = **2** (`content_quality`, `proposal_asset_alignment`); `asset_confidence` **conserva su bloqueo**. Mitad conductual + mitad documental **montadas juntas** | **MEDIA** | **MIXTO** — estructura de severidad DIRECTO; corrección documental + candado de regresión delegables | No |
| FASE-E | 5 | Auditabilidad: **A2** persistir `site_presence_snapshot` junto a `v4_audit/` (§10#2) + **A6** poblar `asset_path` en el caller del builder (§10#3) | **MEDIA** | **DELEGADO** — 2 tracks localizados sin decisión de diseño; parent integra | No |
| FASE-F | 6 | **A4/V15** un oráculo de presencia para decidir *y* narrar + **A1** `skipped ≠ passed` y unificar los dos defaults de G9 + **N11/P9** gate de coherencia que respete `is_coherent` (§10#4) | **MEDIA-ALTA** | **DIRECTO** (N11 es decisión arquitectónica: respetar o eliminar el campo) | No |
| FASE-G | 7 | Ceguera de gates (Nivel 3.7): cablear `doc_audit_consistency` + ampliar `_identify_critical_issues` + cerrar escotillas V5/V9 del coverage gate | **MEDIA-ALTA** | **DIRECTO** (V5 lleva advertencia anti-reversión: `ASSET_GENERATED` fue el fix de BUG-6 del 2026-07-25) | No |
| FASE-H | 8 | Quirúrgicos (Nivel 3.8): V6 `except Exception` → logging visible, V7 guard `__iter__` → validación numérica, V8 dedup `low_organic_visibility`, V11 residuos D6, V13 dos `MetadataValidator` gemelos, V12 documentar decisión OPS del `.env` | **BAJA-MEDIA** | **DELEGADO** (✅ ejecutada 2026-09-04) — 2 subagentes + parent, **pero NO en paralelo sobre archivos compartidos**: `pain_solution_mapper.py` y `v4_diagnostic_generator.py` lo estaban, así que el reparto final fue por **archivos disjuntos** (→ L-H2) | No |
| FASE-I | 9 | **E2E ÚNICA**: corrida `v4complete` Hotel Salento Real + Protocolo de Evidencia Proactiva + comparación contra baseline `output/FASE-D_salentoreal_post_guard/` | **BAJA** (impl) | **MIXTO** — `v4complete` vía subagente (timeout 900, notify); verificación/comparación en parent | **Sí (1)** |
| FASE-VERIFY | 10 | Certificación formal AC1-AC12 contra evidencia real + **análisis post-implementación de que los fixes fueron superados** + lecciones aprendidas | **MEDIA** | **DIRECTO** (no delegable, executor §4.6: requiere juicio y contexto completo del plan) | No |
| FASE-RELEASE-4.75.0 | 11 | Version bump, CHANGELOG, GUIA_TECNICA, DOMAIN_PRIMER (auto-regenerado), validaciones finales | **BAJA** | **DELEGABLE** (solo YAML/MD + scripts, sin imports del proyecto) | No |

**FASE-VERIFY activada** (executor §4.6): ≥3 fases de implementación ✓ (A-H, son 8) · ejecución E2E ✓
(FASE-I) · ACs cross-fase ✓ (AC1-AC12 cruzan A→I).

## Criterios de aceptación (fuente única para todo el plan)

| AC | Descripción | Fase dueña | Verificación | Hallazgo que cierra |
|----|-------------|-----------|--------------|---------------------|
| AC1 | Existe UN registro canónico de identidad servicio↔asset↔pain; los ≥9 registros previos derivan de él o validan contra él; 0 IDs fantasma (`no_speakable`, `no_llms_txt`, `ia_crawler_blocked`, `weak_brand_signals`, `no_entity_schema`, `no_factual_data`) | A | Contract test guardián AST + grep de IDs fantasma → 0 **en los universos migrados** (`modules/commercial_documents` + `modules/asset_generation`; ver nota de auditoría en `01-plan-maestro` §FASE-A: `opportunity_scorer`/`pain_to_type` se migran, `gap_analyzer` queda legacy con decisión registrada) | V2, V3, V14 |
| AC2 | El drift «8 vs 7» está corregido en sus **tres** copias (`proposal_asset_alignment.py:35-37`, `service_catalog`, `v4_proposal_generator.py:1332`) y un contract test falla fuerte si reaparece | A | Test de contrato narrativa↔fuente (no valores fijos, L-NC10) | V14, B3 |
| AC3 | La contradicción `ASSET_TO_PAIN_ID["monthly_report"] → "no_faq_schema"` vs `service_catalog (no_monthly_report)` está resuelta a favor del registro canónico | A | Test de contrato | V3 (perla) |
| AC4 | **Biyección triple** fijada: mapa↔emisión↔narrativa. Cada `pain_id` declarado en `PAIN_SOLUTION_MAP` (27 entradas) o tiene **punto de emisión real en `detect_pains`** *y* **entrada en `narratives`** (`_pain_to_brecha`), o fue retirado del mapa con justificación registrada. 0 pains sin decisión. ⚠️ *Enmendado post-FASE-A (N-A1, medido)*: la biyección doble deja el fix **inerte** — `narratives` tiene 16 claves vs 27 y descarta en silencio en `if pain.id not in narratives: return None`; los **11** ausentes son los 9 pains muertos de V1 **+ 2 que sí se emiten y sí se descartan hoy** (`no_ga4_enhanced`, `low_ota_divergence`) ⟹ **11 decisiones, no 9**. Ver `10-analisis` §5 S6/S12/S13 | B | Test de biyección **tridireccional** (patrón guardián AST de FASE-SR-A) + delta re-medido con `evidence/FASE-A/faseA_narratives_audit.py` | V1, caída #4 de §4 |
| AC5 | La propuesta comercial **solo promete servicios con brecha detectada**: `no_breach = 0` por construcción en una corrida con los 7 servicios actuales; `coverage_ratio` deja de ser algebraicamente 1.0 | C | Experimento contrafactual medido + artefactos de la corrida | B1-B5, §10#1 |
| AC6 | El `is_coherent = false` estructural (B5) desaparece por la vía del punto 8, no por relajar el umbral | C | `asset_generation_report.json` de la corrida FASE-I | B5, §9.2 |
| AC7 | Los 13 publication gates tienen severidad explícita: **11 blocking + 2 advisory**. `asset_confidence` está en la lista blocking. `check_publication_readiness` filtra por severidad, no por `not r.passed` plano | D | Test de las dos listas + inspección de `check_publication_readiness` | H10, §8.4 |
| AC8 | **(a)** Los docstrings de `publication_gates.py` y `AGENTS.md` (tabla Módulos Activos + bloque FASE 4.5) dicen **11 blocking + 2 advisory**, corregidos **en el mismo commit** que AC7 (nunca por delante). **(b)** El piso advisory y su divulgación al consumidor nombrado están fijados **por test** — no por corrida (reformulado por FASE-HOTFIX, H5/S-V4; ver nota en `01-plan-maestro.md` §FASE-D) | D | `test_docstrings_no_prometen_el_regimen_antiguo` + `TestFASEDGateSeverity` (12) + `TestAdvisoryDisclosureFASED` (4) · `validate_agents_md.py` + grep | H10 mitad documental, S-V4 |
| AC9 | `site_presence_snapshot` se persiste en `v4_audit/` y es retro-testeable (A2); `asset_path` deja de ser `null` en el reporte de delivery (A6) | E | `find output -iname "*site_presence*"` → ≥1 resultado; grep `asset_path` en `delivery_quality_report.json` | A2 (§10#2), A6 (§10#3), H7 |
| AC10 | Un único oráculo de presencia decide **y** narra (A4/V15): la narrativa se deriva de la decisión, no de un segundo criterio. `details.missing_count` y el conteo de la matriz ya no divergen | F | Test con fixture de los 6 NO_BREACH de SalenteReal | A4, V15 |
| AC11 | G9 no pasa en verde cuando se salta (A1): `skipped` no cuenta como `passed` en el summary ni en `BLOCKING_GATE_NAMES` | F | Test de gate saltado → no bloquea pero NO figura como passed | A1, H9 |
| AC12 | El gate de coherencia respeta `is_coherent` (N11/P9): un paquete con `is_coherent: false` **no** puede salir `READY_FOR_PUBLICATION`, o el campo se elimina a favor de sus checks con decisión registrada | F | Test de reproducción del caso SalenteReal (score 0.88 + `is_coherent: false`) | N11, P9 (la deuda más grave) |

**ACs de no-regresión** (transversales, verificados en FASE-I contra el baseline; **NR1-NR6 = familia
«de hallazgo»**, cubren los fixes de FASE-G + baseline + corrida. La familia **NR7-NR12 «de producto»**
(no-regresión de entrega: tests, coherence, gates, ZIP, asset_confidence, anomalías) vive definida en
`05-prompt-inicio-sesion-fase-VERIFY.md` §V2 y se replica en `10-analisis` §3):

| AC-NR | Descripción | Verificación |
|-------|-------------|--------------|
| NR1 | `doc_audit_consistency` llega con `audit_data`/`diagnostico_text` y acepta `gbp.reviews` como `int` (986), no solo como dict | FASE-G + artefactos FASE-I |
| NR2 | `_identify_critical_issues` califica PageSpeed `status=ERROR` y banda GEO `critical` (29/100) | FASE-G + artefactos FASE-I |
| NR3 | Escotilla V5 cerrada **sin revertir** el fix BUG-6/N2 de Zione (2026-07-25): distinguir "generado y mencionado" de "generado y silencioso" | FASE-G + test anti-reversión |
| NR4 | Escotilla V9 cerrada: ledger vacío no pasa como PASS cuando debería ser BLOCKED | FASE-G + test |
| NR5 | Suite baseline preservada: 848 passed / 2 skipped en `tests/quality_gates` + `tests/asset_generation` | Cada fase |
| NR6 | La corrida FASE-I produce `coherence_score ≥ 0.80` y los 13 gates con el perfil esperado post-refactor | FASE-I vs baseline |

## Complejidad técnica (detalle → `01-plan-maestro.md`)

Escala: Baja → Baja-Media → Media → Media-Alta → Alta → MÁXIMA.

Riesgo concentrado en **FASE-C** (punto 8, MÁXIMA: toca propuesta + matriz + gate + alignment_result en
cadena causal) y **FASE-A** (ALTA: censo y unificación de ≥9 registros sin romper consumidores).
FASE-E/H/RELEASE delegables; FASE-I comando largo delegado con verificación en parent; VERIFY directo.

**Presupuesto total**: ≤60 iteraciones por fase (R2). FASE-C es la única con riesgo real de agotarlo —
si lo hace, se parte en C1/C2 como dos sesiones y se re-numera el resto (decisión registrada en
`10-analisis-post-implementacion.md`, no improvisada en la sesión).

## Delegación (delegate_task)

| Fase | Delegable | Justificación (regla del executor) |
|------|-----------|------------------------------------|
| FASE-A | **NO** | Decisión arquitectónica cross-module (cuál de ≥9 registros manda) — un subagente carece del contexto completo de los consumidores. Lección DT-3 |
| FASE-B | **NO** | Decisión de producto por pain muerto (implementar vs retirar) cambia lo que se vende al cliente |
| FASE-C | **NO** | MÁXIMA complejidad, cadena causal propuesta→matriz→gate→alignment; es el núcleo del plan |
| FASE-D | **MIXTO** | Estructura de severidad = decisión (DIRECTO). Corrección documental de `AGENTS.md`/docstrings + candado de regresión = replicar patrón `commercial_gate.py:99-113` (DELEGABLE) |
| FASE-E | **SÍ** | 2 tracks de ediciones localizadas (persistir snapshot / poblar campo) que no requieren decisión de diseño; parent integra y valida |
| FASE-F | **NO** | N11 es decisión arquitectónica (respetar `is_coherent` o eliminarlo); A4 unifica dos criterios que hoy divergen |
| FASE-G | **NO** | V5 lleva advertencia anti-reversión explícita (fix BUG-6 del 2026-07-25) — un subagente sin ese contexto re-introduce el bug |
| FASE-H | **SÍ** (✅ ejecutada así) | 6 quirúrgicos independientes y localizados, cada uno con patrón ya fijado en el dossier §12.3. ⚠️ **Independientes en decisión, NO en archivo**: dos pares compartían `pain_solution_mapper.py` y `v4_diagnostic_generator.py`, así que el reparto fue por **archivos disjuntos** y el parent tomó los compartidos → **L-H2** |
| FASE-I | **MIXTO** | Comando largo (`v4complete`, ~3 min) delegado con timeout 900 + notify; comparación contra baseline y Protocolo de Evidencia en parent (executor L30 RC1-RC2) |
| FASE-VERIFY | **NO** | Executor §4.6: requiere juicio y contexto completo del plan |
| FASE-RELEASE | **SÍ** | Solo YAML/MD + scripts, sin imports del proyecto |

## Medios de comprobación de efectividad

1. **Contract tests por fase** (no valores fijos): cada fase entrega al menos un test que falla fuerte
   ante el drift que corrige. Patrón canónico: guardián AST de FASE-SR-A. Anti-lección L-NC10
   (fosilización narrativa) y L-NC4 (no crear tablas paralelas nuevas en Nivel 1.2).
2. **Experimento contrafactual del punto 8** (FASE-C): medir `no_breach`, `coverage_ratio`,
   `unresolved` e `is_coherent` antes/después sobre los artefactos reales de SalenteReal. Sin este
   delta medido, AC5/AC6 no se pueden certificar.
3. **Corrida E2E única** (FASE-I): `v4complete` Hotel Salento Real comparada contra el baseline
   `output/FASE-D_salentoreal_post_guard/` (coherence 0.88, 13/13 gates, 2026-08-31 12:28). Es la
   **única** ejecución del plan — todas las fases previas validan con tests y fixtures, no con corridas.
4. **Certificación formal** (FASE-VERIFY): matriz AC1-AC12 + NR1-NR6 contra evidencia real, con
   análisis explícito de *qué fix fue superado y cómo se demostró*.

## Reglas transversales (Paso 0 — lecciones capitalizadas)

Recuperadas de QMind `iah-cli-lecciones` (8 fuentes) y de 3 memorias de proyecto:

- **TDD: contratos ANTES del fix** (precedente SR-H2). Cada fase escribe el test que expone el defecto
  y lo ve fallar antes de tocar el código de producción.
- **Guardián AST para contratos transversales** (SR-A), no regex. Aplica a AC1-AC4.
- **No crear un tercer sistema** (VALIDADOR-URL-PROPIA): el registro canónico de FASE-A debe ser
  consumido por la narrativa, no duplicado para ella. Guardrail **L-NC4**.
- **Tests de contrato narrativa↔fuente, no valores fijos** (L-NC10): un test que fija `coverage == 1.0`
  fosiliza la tautología en vez de curarla.
- **Unificar conteos en DTOs multi-consumer con helper canónico + contract tests** (lección de
  FASE-SR-A): aplica directo a `AlignmentResult.compute_unresolved()` en FASE-C/F.
- **No colapsar «vacío» con «ausente»** (SR-H2, familia D6/L-SR5): aplica a A1 (`skipped ≠ passed`),
  V9 (ledger vacío), V6 (`except Exception`).
- **Anti-reversión V5**: `ASSET_GENERATED` en `_JUSTIFIED_STATUSES` fue el fix de BUG-6/N2 (Zione,
  2026-07-25). No quitarlo sin distinguir «generado y mencionado» de «generado y silencioso».
- **Revalidar citas de código NO revalida premisas**: probar contra salidas reales. Los validadores en
  verde verifican **forma**, no premisas — la lección exacta del ROADMAP v4.0→v4.1.
- **Mitad documental de H10 nunca por delante de la conductual**: corregir solo los docstrings cambia
  una falsedad (10+3) por otra (11+2 con los 13 bloqueando). AC7 y AC8 van en el mismo commit.
- **`asset_confidence` NO se demote a advisory**: es hoy el único mecanismo que vuelve no-entregable un
  paquete Tier C. Relajarlo dejaría salir el 14% del histórico con 100% de assets ESTIMATED.
- **Pytest seguro**: lotes pequeños, salida a archivo (`> temp/x.txt 2>&1`), NUNCA la suite
  `tests/commercial_documents` completa (fuga ~8GB).
- **Línea base**: re-verificar al inicio de FASE-A los tests rojos preexistentes y NO atribuirlos al
  plan. Baseline declarado por el dossier §8.6: **848 passed / 2 skipped** en `tests/quality_gates` +
  `tests/asset_generation`. ⚠️ **Es el número pre-plan, no el vigente**: medido al cierre de cada fase
  quedó **944 passed / 2 skipped** tras FASE-G, y **FASE-H encontró el «848/2» aún en su propio prompt**
  — lo re-verificó en su árbol y cerró con **944/2 intacto** (S26: la métrica literal ya estaba mal
  formulada; medir el delta sobre el árbol propio es lo único que funciona).
- **`log_phase_completion.py` SIN `--release`** en fases intermedias; bump/CHANGELOG solo en RELEASE
  (anti-deuda §2.5: cada fase cierra su propia documentación, no se difiere).
- **Clasificar fallos de `run_all_validations.py`**: Version Sync → `sync_versions.py`; Document
  Integration → README; NO re-correr la suite completa.
- **V12 (`.env`) es decisión OPS, no de código**: documentar en FASE-H, no editar `.env` en una fase
  de refactorización. ✅ **Cumplido el 2026-09-04**: FASE-H midió y documentó (longitudes de las dos
  claves + la cadena de fallback) **sin tocar `.env`** (`git diff --stat .env` = vacío) → detalle en
  `09-documentacion-post-proyecto.md` §E (nota OPS) y recomendación pendiente para OPS.
- **E2E con `--output` alternativo**: grep de símbolos no definidos en ramas nuevas antes del run
  (FASE-I T1).
- **Protocolo de Evidencia Proactiva**: copiar los artefactos críticos a `evidence/FASE-I/`
  INMEDIATAMENTE después del `v4complete`, antes de cualquier análisis.

## Qué NO está en este plan (límites explícitos)

- **El tribunal multi-bot** (`modules/quality_gates/tribunal/`). Este plan es su **precondición** —
  el dossier y las memorias coinciden: *"plan de estabilización PRIMERO, tribunal DESPUÉS"*.
- **S2.3** del dossier (§8.5: qué NO hacer).
- **Agregar el 8º servicio** al registro (§8.5). La unificación 7→8 empeora `coverage_ratio`
  (0.571 → 0.500) aunque en coherence cueste exactamente 0.0000 — medido.
- **Cambiar el denominador de `coverage_ratio` como fix aislado**: es un interruptor global que
  bloquea en 10/10 configuraciones medidas y es insatisfacible por medios honestos. Se resuelve por
  la vía del punto 8 (FASE-C), no tocando la fórmula.
- **Onboarding real del hotel (Capa 3) y deploy (Capa 4)**: tramo externo de FASE T (T3/T5/T6),
  fuera del tramo offline que este plan habilita.
- **Tocar `delivery_quality_report.py:289` `BLOCKING_GATE_NAMES` como parte de H10**: rige el ZIP, es
  régimen de **delivery**, no de publicación. FASE-F lo toca solo por A1 (`skipped ≠ passed`).
- **Editar `.env`** (V12).

## Archivo índice

| Archivo | Propósito |
|---------|-----------|
| `README.md` | Este índice: problema, fases, ACs, delegación, reglas transversales |
| `01-plan-maestro.md` | Fases, complejidad, tareas detalladas, presupuesto de iteraciones |
| `05-prompt-inicio-sesion-fase-A.md` … `fase-I.md` | Prompts de implementación (1 por sesión, 9 archivos) |
| `05-prompt-inicio-sesion-fase-VERIFY.md` | Certificación formal AC1-AC12 + análisis post-implementación |
| `05-prompt-inicio-sesion-fase-RELEASE.md` | Cierre documental v4.75.0 |
| `06-checklist-implementacion.md` | Estado maestro de fases |
| `09-documentacion-post-proyecto.md` | Datos acumulativos para RELEASE (secciones A-E) |
| `10-analisis-post-implementacion.md` | Lecciones, matriz de verificación, decisiones arquitectónicas |
| `dependencias-fases.md` | Grafo de dependencias y conflictos de archivo |

## Progreso

| Fase | Estado | Fecha | Iteraciones | Tests nuevos | Notas |
|------|--------|-------|-------------|--------------|-------|
| FASE-A | ✅ Completada | 2026-09-03 | 55/55 | 21 func. test (37 casos) | Canónico en `modules/common/service_identity.py` (dos capas); 6 registros derivados, 6 validados contra Capa 1; 0 IDs fantasma; drift «8 vs 7» disuelto en sus 3 copias; AC1/AC2/AC3 ✅ |
| FASE-B | ✅ Completada | 2026-09-03 | **345 medidas hasta el commit de código** / ≤40 ⚠️ *(excedido 8,6×; ver nota abajo)* | 29 func. test (46 casos) | Biyección triple cerrada: **DESCARTE REAL 2→0**, Capa 1 27→26, emisiones 18→20, `narratives` literal **16→16** (complemento derivado, L-NC4), cobertura narrativa **26/26**. 3 pains implementados con señal verificable, 1 retirado (`no_ga4_enhanced`), 6 diferidos con motivo+seguimiento. **Premisa de N-A1 corregida** (S-B7). Baseline 848 intacto, validaciones 7/7. AC4 ✅ |
| FASE-C | ✅ Completada | 2026-09-03 | **142 medidas hasta el commit de código** / ≤60 ⚠️ *(excedido 2,4×; ver nota abajo)* | 14 func. test (17 casos) + 3 netos en archivos existentes | **Punto 8 — propuesta dinámica**: la propuesta solo promete servicios con brecha mapeada o presencia verificada. Partición canónica **única** (`classify_promised_services()`) consumida por los **dos** builders de la matriz ⟹ A5 curada de raíz, no esquivada. `not_promised` y `unknown_services` publicados en el JSON. Delta medido sobre la corrida real de SalentoReal: `no_breach` **6→0**, `promised_services_total` **7→1**, `total == actionable` por construcción, `assets_are_justified` **0.75/error → 1.0/info**, `overall_score` **0.88 → 0.9133**, `is_coherent` **False → True** con el **umbral 0.8 intacto**. **vacío ≠ ausente** en 3 sitios. **El dossier §9.2-B5 acertó la causa**; lo falsificado fue el **parafraseo que C hizo de él** (S-C1) — y lo que el dossier **no previó** es que una promesa dinámica de *servicios* no saca a `monthly_report` de la lista de *assets* que coherence cuenta, así que AC6 exigió una segunda decisión (complementos fuera del denominador). Baseline 872→**892**, validaciones 7/7. AC5/AC6 ✅ |
| FASE-D | ✅ Completada | 2026-09-03 | **114 medidas hasta el commit de código** / ≤35 ⚠️ *(excedido 3,3×; ver nota abajo)* | 24 func. test (8 candado de listas + 12 severidad conductual + 4 divulgación) | Severidad explícita **11 blocking + 2 advisory** con única fuente (`BLOCKING_GATE_NAMES`/`ADVISORY_GATE_NAMES`/`gate_blocks_publication()`) y fail-fast en `__init__`. `asset_confidence` **sigue bloqueando**. Piso D2 por naturaleza del fallo (`content_quality` con blockers, `proposal_asset_alignment` < 0.8) + un gate que no se ejecutó siempre bloquea. Divulgación: `summary["advisory_issues"]` → `human_checklist.md`. `content_quality` con solo warnings pasa de `PASSED` a `WARNING` (antes invisible). **0 flips de `ready`** en el contrafactual real ⟹ no se relajó ningún veredicto. AC7/AC8 ✅ *(AC8: mismo commit)* |
| FASE-E | ✅ Completada | 2026-09-03 | **72 medidas hasta el commit de código** / ≤30 ⚠️ *(excedido 2,4×; ver nota abajo)* | 10 func. test (10 casos) | **A2 oráculo persistido** (`v4_audit/site_presence_snapshot.json`, writer passthrough versionado en `site_presence_adapter.py`, punto en FASE 0E con `[WARN]` no-bloqueante) + **A6 `asset_path` poblado** — causa raíz en el caller (`assets_for_quality` en `main.py` no incluía la clave `path`), la matriz no se tocó. Baseline 892→**897** (+5), validaciones 7/7. ⚠️ Desviación de §4: tracks E1/E2 **secuenciales** — ambos editan `main.py` (**S-E1**); censo E4 de consumidores → insumo duro de F (**S-E2**: 3 bloques muertos + NameError latente). AC9 ✅ *(evidencia aportada; presencia del archivo en corrida real la certifica FASE-I)* |
| FASE-F | ✅ Completada | 2026-09-03 | **182 medidas hasta el commit de código** / ≤45 ⚠️ *(excedido 4×; ver nota abajo)* | 23 func. test (23 casos) + 2 tests reescritos al nuevo contrato | **A4/V15 oráculo único**: `verify_proposal_asset_alignment` decide y narra con `is_present_in_production` (H7/L-SR3 intacto); veto FASE-12B extendido a `exists_with_issues`; anti-A4 y `missing_count==matriz` candados. **A1 skipped≠passed**: `NOT_EVALUATED` + defaults G9 unificados en `_not_evaluated_g9()`, visible en summary/`human_review_items`, no bloquea. **N11/P9**: decisión (a) **respetar** `is_coherent` — `coherence_verdict_passes()` única definición, consumida por `_coherence_gate` y por `CoherenceGate` (conectado; H8: `publication_state.py` eliminado, 0 referencias). Umbral 0.8 intacto. **F4 corpus** (`evidence/FASE-F/impacto-corpus.md`): 28 primarias + 4 copias re-evaluadas — **0 liberadas**, 4 READY→NOT_READY (is_coherent=False persistido, dirección segura), las ~10 ESTIMATED siguen bloqueadas. Baseline **920/2** (848/2 + delta A–F), validaciones 7/7. AC10/AC11/AC12 ✅ |
| FASE-G | ✅ Completada | 2026-09-04 | **154 medidas hasta el commit de código** / ≤50 ⚠️ *(excedido 3,1×; ver nota abajo)* | 40 func. test netas (16 detector + 14 V5/V9 en 2 archivos nuevos + 3 netas doc_audit + 7 netas publication_gates; 12 reescritas al contrato post-G de doc_audit) | **NR1-NR4 cerradas.** NR1: `audit_data` llega al gate vía `AssessmentPayload.audit_data` + `with_audit_data()` en `main.py`; datos ausentes → `NOT_EVALUATED` (coherente con A1), contradicciones → FAILED; `gbp.reviews` acepta int (986). NR2: `_identify_critical_issues` califica PageSpeed `status=ERROR` y banda GEO `critical` (29/100) vía helper `geo_band_critical_issue` + `with_geo_flow()`; SR-H2 condicionado (atajo favorable solo con performance ≠ ERROR). NR3: V5 cerrada por **regla de mención** — `ASSET_GENERATED` SIGUE en `_JUSTIFIED_STATUSES` (BUG-6 intacto, fixture anti-reversión corre el gate REAL), «existe en producción» es `VERIFIED_IN_SITE`. NR4: V9 unificada tras normalización — `reconciler_dropped_entries` BLOCKED, vacío legítimo PASSED con traza `ledger_present_zero_entries`. ⚠️ **`pain_solution_mapper.py` NO fue tocado** (predicción de §3 falsa — G2 vive en `v4_comprehensive.py`): H1/H3 sin orden forzoso. Baseline 920→**944** (+24 netos), validaciones 7/7, 1 fallo preexistente en HEAD (`test_gate_presence_with_skipped_assets`, verificado con worktree — no se atribuye a G) |
| FASE-H | ✅ Completada | 2026-09-04 | **PRESUPUESTO INCUMPLIDO** (ver `evidence/FASE-H/faseH_iteraciones.txt`: ≥155 llamadas de herramienta; `measure_iterations.py` no es ejecutable bajo el sandbox de esta sesión) / ≤35 | 46 func. test (74 casos) | **Seis quirúrgicos del Nivel 3.8 cerrados** (V6/V7/V8/V11/V13 + **V12 documentado, `.env` NO editado**). **V7**: el guard `hasattr(direct_field.value, '__iter__')` se reemplazó por validación numérica con **normalización de unidades** (`_normalize_to_fraction`: `0.2`, `20`, `"0.2"`, `"20"` y `"20 %"` son todos 20 %) ⟹ `low_ota_divergence` (high, priority 1) **ya puede disparar** con el `direct_channel_percentage=0.20` de fuente `"Default"` que el pipeline ya conoce; `ota_presence` entró como **evidencia no bloqueante** del description y **nunca como guard** (`main.py` no lo registra en el `ValidationSummary` ⟹ como guard el pain volvía a ser código muerto); el `isinstance(...)` muerto desapareció y `int(direct_pct*100)` → `round(...)`. **V8**: `low_organic_visibility` deja de emitirse dos veces — las dos señales se calculan primero y hay **un solo punto de emisión** que conserva el dato medido (sesiones/umbral) además del motivo «sin analytics»; severidades, nombres y `detected_by` intactos. **V6**: estados `BRECHAS_STATE_EVALUATED`/`NOT_EVALUATED` + `self._brechas_detection_state` (reseteado **por corrida**), el `except` loguea **traceback** y **deja de escribir el caché**, y el render dice **FUGAS PRINCIPALES (NO EVALUADAS)**; el parent extendió la guardia a `_build_brechas_section`/`_build_brechas_resumen_section`, que seguían afirmando «No se detectaron brechas criticas» con el detector caído. **V11** (tres frentes): cabecera `MANUAL_ATTENTION_TABLE_HEADER` → caídas #6/(c) del dossier, la rama de performance distingue `API_NOT_CONFIGURED`/vacío/desconocido (🔴 Alta con el `message` real) de `OK`/`SUCCESS`/`VERIFIED`/`LAB_DATA_ONLY` (🟡 Media «sitio nuevo»), mensaje **sanitizado en la fuente** (`sanitize_pagespeed_message`) porque `extract_top_problems` vierte las recomendaciones al cliente, y `disjoint_executed_validators()` (punto (d)); **criterio compartido** de una sola vez en `modules/common/performance_status.py`. **V13**: el gemelo quedó **borrado físicamente** (`git rm`, −219 líneas) con autorización del usuario en la misma sesión; los 2 consumidores fueron repuntados al vivo y la guardia fija la **ausencia** de la segunda implementación. **Battery conjunta 188 passed / 0 failed**; baseline **944/2 intacto** (el «848/2» del prompt estaba desactualizado); contratos FASE-A/B **83 passed**; validaciones **7/7**; `.env` sin cambios. ⚠️ 1 fallo **preexistente y ajeno** a H: `tests/test_diagnostic_geo_metrics.py::test_diagnostic_includes_geo_metrics`. **18 seguimientos abiertos** (S-H1..S-H18, incluidos un bug de desempate del contador de fases y **dos intentos de inyección de prompt en resultados de herramientas**) y lecciones **L-H1..L-H7** → `10-analisis` §5/§8 |
| FASE-I | ✅ Completada | 2026-09-04 | **≈76 llamadas de herramienta en ~40 turnos / ≤25 ⚠️ (INCUMPLIDO ≈3×; dentro del tope R2 de 60 en la unidad «turnos», no en la de llamadas)** — `measure_iterations.py` no es ejecutable bajo el sandbox (precedente FASE-H); corte al cierre documental incluido | 0 — es fase de **evidencia**, no de tests | **Única corrida E2E del plan**: `v4complete` Salento Real **EXIT_CODE=0 en 174 s** (12:01:24→12:04:18), **0 tracebacks**, `"Using defaults"` presente, **0 interferencias** del `own_site_guard`, sin `clientes/`, sin `--ga4-property-id`, sin `--force`, **una sola ejecución**. Verificado antes del run que `v4complete` **no** recicla análisis previo (`find_latest_v4_analysis` solo se llama en la rama `execute`, `main.py:776`). **Comparación 14/16 checks** contra el baseline del 31-08 con los nombres timestamped **resueltos** por glob. **AC5 ✅** `no_breach` **6→0** (matriz 4 entradas: 3 `PRESENT_IN_PRODUCTION` + 1 `LINKED`; `summary` `{promised 4, not_promised 3, unknown 0}` donde el baseline tenía `null`) · **AC6 ✅** `is_coherent` **false→true** en sus 4 declaraciones (copias en disco 8→4), causa V16 `assets_are_justified` **0.75→1.0** · **AC9 ✅** `site_presence_snapshot.json` **existe (1.421 B) y viaja dentro del ZIP** (38 vs 37 archivos; el diferencial normalizado es ese archivo) + `asset_path` de la LINKED poblado · **AC12 ✅** ZIP con veredicto coherente (el baseline empaquetó con `is_coherent=false`). **NR1 ✅** `doc_audit_consistency` `value` **null→0** con mensaje real · **NR6 ✅** coherence **0.8333 ≥ 0.80**, 11 PASSED + 2 WARNING, `READY_FOR_PUBLICATION`. **AC7 ❌ y NR2 ❌ sobre artefactos**: la severidad 11+2 **no se serializa** en `gate_report_*.json` (**S-I2**) y `critical_recall` queda en **1.0 con `details={}`** (**S-I1**) — con causa raíz medida: el registro V6 de FASE-H (`PageSpeed API ERROR` en `overall.critical_issues`) hace `covered=True` en `_evident_critical_missed`, así que el detector G2 **nunca se ejerce en producción**; el repro aislado (`faseI_repro_g2.py`) sí da 0.5/BLOCKED ⟹ **la predicción de FASE-G fue falsada por la medición**. Coherence **0.88→0.83 explicada y atribuida**: `problems_have_solutions` 1.0→0.6 porque el ledger pasó de **3 a 5 pains** (`low_ota_divergence` HIGH reactivado por V7, `missing_llmstxt` LOW) ⟹ **el sistema bajó su nota por decir más verdad**; `coverage_no_silent_drop` 5/5 con `uncovered: []`. **8 caídas del dossier §4: 3 cerradas en sustancia (#1 PageSpeed divulgado y registrado como crítico, #4 `missing_llmstxt`, #8 `low_ota_divergence`), 3 parciales (#2 GEO — conviven 79/85/29; #3 visibilidad LLM — el doc sigue diciendo «Visibilidad en IA: Alta» sobre `mention_rate 0.0`; #6 — solo mejoró el **render**: la cabecera `Atención manual` que añadió V11(c) está, pero `fotos=10` sigue sin pain y coexiste con `✅ fotos_gbp(15%)`), 2 intactas y fuera del alcance A-H (#5 schema warnings, #7 `title=""`/`description=""` — idénticos en ambas corridas, luego **no** es variación del sitio)**. **Cero** diferencias cerradas como «variación natural» (fotos 10, `metadata.title=""`, competidores y los 3 escenarios financieros **idénticos**; única variación real: `research_id`). Financiera **idéntica** al baseline ($4.042.752 esperados). Suite **944 passed / 2 skipped intacta** pre y post run; validaciones **7/7** en ambos puntos. ⚠️ Pre-flight: `validate_agents_md.py` **5 PASS / 1 FAIL** (`test_count` 3689 vs 3889 = 5.1 % > ±5 %, deriva **documental preexistente** en HEAD, S-I6). Nuevos seguimientos **S-I1..S-I8** → `10-analisis` §5.7 |
| FASE-VERIFY | ✅ Completada | 2026-09-04 | **≈65 llamadas de herramienta / ≤40** ⚠️ **(INCUMPLIDO ≈1,6×)** *(auto-reporte en unidad `tool_use`; el instrumento canónico sigue sin ser ejecutable bajo sandbox — S22/DA-V6. La fase publicó primero «≈36» y lo corrigió: subestimar el propio conteo es el defecto de S22/L-B3 reproduciéndose en la fase que debía resolverlo)* | 0 — no escribe código ni tests | **8 AC ✅ / 4 AC ⚠️ (AC6, AC7, AC8-b, AC10) / 0 ❌** y **10 NR ✅ / 1 ⚠️ (NR12) / 1 ❌ (NR2)**, medidos con **sonda propia** sobre los artefactos de la corrida I y el árbol vivo (no re-usando los logs de fase). Baterías re-ejecutadas: suites tocadas **944 passed / 2 skipped / 0 failed**; contratos A+B+C+D+delivery **170 passed / 1 failed**; `run_all_validations.py --quick` **7/7**. **El 1 failed es un hallazgo nuevo — S-V1**: un test rojo que FASE-F dejó al cambiar el contrato A1, indetectable para NR5 porque su ventanilla no incluye `tests/delivery`. Nueve seguimientos nuevos **S-V1…S-V10**; seis re-asignaciones con dueño real (**S-C3/C4/C6/E2/F2/S9** → hotfix/tribunal, **ninguna a RELEASE** → DA-V5); **S22/S23/S24/S25/S26/S-F1 resueltos**; **cuatro sobre-afirmaciones corregidas con medición** (AC3, AC5, AC6, AC7); **14 de 16 citas de línea de los ACs caducadas** (S-V6) ⟹ regla de citar símbolos para el executor (L-V4). Veredicto §4.6: la causa raíz está curada y fijada por contract tests, **pero el plan movió la clase de defecto en vez de erradicarla** (3 instancias nuevas, visibles solo sobre artefactos reales) → `evidence/FASE-VERIFY/ESTABILIZACION-PRE-TRIBUNAL/` |
| FASE-RELEASE-4.75.0 | ✅ Completada | 2026-09-04 | **≈65 llamadas de herramienta / ≤25** ⚠️ **(INCUMPLIDO ≈2,6×; dentro del tope R2 de 60 en la unidad «turnos», no en la de llamadas)** *(auto-reporte en unidad `tool_use`; `evidence/FASE-D/measure_iterations.py` sigue sin ser ejecutable bajo esta política de permisos ⟹ **R2.1 del executor v2.19.0**: se reporta en la unidad usada y se declara. Quinto caso consecutivo — S22/DA-V6 no cerrado por escribir la regla)* | 0 — fase documental: no escribe código ni tests | **Cierre documental v4.75.0 publicado.** R1 `VERSION.yaml` 4.74.1→**4.75.0** con codename y fecha, **0** ocurrencias de `4.74.1` en código Python. R2 `CHANGELOG.md` con las 5 subsecciones del formato, copiado de `09` **§C.2** (no §C.1) y publicando **1 AC ⚠️ + 1 NR ❌ como tales**. R3: `log_phase_completion.py --fase FASE-RELEASE-4.75.0 --release 4.75.0` (**Version Sync Gate PASSED**) → `sync_versions.py` (**6 cabeceras**, grep `4.74.1` = **0**) → **11 notas técnicas** en `GUIA_TECNICA.md` (una por fase A-I + VERIFY + HOTFIX, con Módulos/Problema/Solución/Retrocompatibilidad) → `DOMAIN_PRIMER.md` **regenerado por script** (197 archivos, 375 clases, 25 módulos). **Halla y corrige en la causa raíz un defecto del sync**: la regla `agents_version_comment` de `scripts/sync_config.yaml` no aceptaba el prefijo `v` que **exige** `validate_document_integration.py`, así que la cabecera de `AGENTS.md` llevaba **releases** quedándose stale y el script respondía «in sync» ⟹ patrón con `v?` opcional y template emitiendo `v`; y `README.md` conservaba la fecha legible de la release anterior (audit E8b). R4: **S11/S-I6 cerrado** — `AGENTS.md` 3.689/284 → **3.934/298** (medido, con la tabla por módulo rehecha para que **sus filas sumen el total**: antes sumaba 3.129 y omitía `_archived_broken_tests/`). Validaciones **8/8** · `validate_agents_md.py` **6 PASS / 0 FAIL** (`agents_md_count` 3.934 vs `pytest_count` 3.932, 0,1 %) · `validate_document_integration.py` sin errores · **0 regresiones**: re-ejecutados los contratos **180 passed / 0 failed** y la suite dirigida **950 passed / 2 skipped** *después* de editar los documentos ⟹ `test_count` y los candados de docs pasan con el árbol nuevo. Evidencia en `evidence/FASE-RELEASE/` (pareja pre/post de los 3 validadores + suites + `git show --stat`). **No tocó** S-HF1 / P12 / S-I1 (tribunal, DA-V5) |

**Nota sobre las iteraciones de FASE-B** — el número es **medido**, no auto-reportado: conteo de
ids de mensaje de asistente únicos en el transcript de la sesión
(`…/5216df39-6b41-44a2-afc7-c3dd8802ec04.jsonl`), con `evidence/FASE-D/measure_iterations.py`.
Supera el presupuesto de ≤40 (tope R2: 60) bajo cualquier unidad de conteo razonable. **No es
estrictamente comparable con el «55/55» de FASE-A**, que coincide exactamente con su presupuesto y
por tanto parece un tope alcanzado y no una medición.

⚠️ **Corrección (2026-09-03)**: esta nota publicaba **151**. Esa cifra era una **foto tomada a las
16:38 locales, antes de terminar el cierre documental** — no el total de la fase. Re-medida con corte
en el commit de código de B (`e6d28b8`), la cifra es **345 ids únicos / 380 `tool_use`**: el
presupuesto se excedió **8,6×**, no 3,8×. Lo detectó la **sesión paralela de FASE-D**, que en
`evidence/FASE-D/faseD_iteraciones.txt` dejó escrito «la cifra de B al cierre real de su fase es mayor
que 151»; B lo confirmó después reproduciendo el corte de las 16:38 (145 ids) y verificando la unidad
de conteo (842 registros `assistant` → 358 ids únicos, `isSidechain=false` en todos: no hay
subagentes inflando). Medición completa en `evidence/FASE-B/faseB_iteraciones.txt`.
El corte «hasta el commit de código» es el que hace comparables a B (345) y D (114); con el cierre
documental incluido ambas crecen (B 359+ y D 247+ al momento de medir, y siguen creciendo mientras
la otra sesión trabaje).

Lo que el presupuesto pretendía proteger **no se perdió**: la fase no se particionó, el candado de B3
nunca quedó en rojo en master, B1 se completó antes de tocar código y todo el barrido está en verde.
El sobrecosto vino de B1 (11 decisiones con evidencia por señal: cada una exigió rastrear el detector,
su guard y su alcanzabilidad) y del barrido de regresión archivo-por-archivo que exige la prohibición
de correr `tests/commercial_documents` completo.

**Brecha de proceso expuesta**: el presupuesto no tenía instrumento de medida, así que cada fase se
auto-reportaba y la cifra no era auditable — y la de B resultó ser, además, una foto prematura.
FASE-D construyó el instrumento (`measure_iterations.py`). Falta adoptarlo como **canónico del plan**
(y no utilidad de una fase), fijar el corte comparable, y resolver qué hacer con A, cuya cifra no es
reconstruible con ese método. → `10-analisis` §5 S22.

**Nota sobre las iteraciones de FASE-D** — medidas con la **misma unidad** que la nota de B (ids de
mensaje de asistente únicos en el transcript `…/55618cbe-69e4-486f-8ad7-4ec64fc12bcf.jsonl`):
**114 hasta el commit de código** (`76e0257`, 21:47:30Z) sobre un presupuesto de ≤35 ⟹ **3,3× de
exceso**; ~160 incluyendo el cierre documental. La brecha que señaló B queda **parcialmente
cerrada**: el conteo es ahora un artefacto re-ejecutable,
`evidence/FASE-D/measure_iterations.py <transcript> [corte-ISO]`, no una afirmación auto-reportada.

El sobrecosto de D no vino del código (D1/D2/D3 son ~170 líneas en un archivo) sino de tres cosas
que el presupuesto no contemplaba: **(a)** verificar el estado real de A/B/C contra `06-checklist` y
git porque el prompt afirmaba que B y C estaban cerradas y **era falso** (y a la vez falso en el
sentido inverso: B sí estaba cerrada en paralelo); **(b)** el barrido archivo-por-archivo que exige
la prohibición de correr suites completas, más diagnosticar que los fallos de `tests/e2e` y el
`ImportError` de selenium son **preexistentes** y no de D; **(c)** la concurrencia con la sesión de
B (rieles de `git add`, edición de los mismos documentos). Lo que el presupuesto protegía **no se
perdió**: la fase no se particionó, `content_quality` y `proposal_asset_alignment` no se relajaron
contra el mundo real (0 flips de `ready`), y D3 quedó en el **mismo commit** que D1/D2 como exigía
AC8.

⚠️ **Colisión de nombres en `evidence/FASE-D/`** (misma clase que registró B para `evidence/FASE-B/`):
el directorio ya contenía **6 archivos** de la FASE-D de **otro plan** (commit `04fe193`, «ZIP sin
gate reports + fallback loader + occupancy label»), con prefijo `fase_d_*` (snake_case). Los de este
plan usan `faseD_*` (camelCase). **VERIFY debe distinguirlos.**

**Nota sobre las iteraciones de FASE-C** — medidas con la **misma unidad** que las notas de B y D (ids
de mensaje de asistente únicos en el transcript de la sesión,
`evidence/FASE-D/measure_iterations.py`): **142 hasta el commit de código** (`c1bf5e2`,
2026-09-03T18:22:55-05:00) sobre un presupuesto de ≤60 ⟹ **2,4× de exceso**, el menor de las tres
fases medidas pero igualmente fuera de presupuesto. Medición en
`evidence/FASE-C/faseC_iteraciones.txt`.

El sobrecosto no vino de escribir la partición (~120 líneas) sino de tres cosas que el presupuesto no
contemplaba: **(a)** revalidar las premisas del prompt contra el código vivo — dos resultaron falsas
(el archivo de tests citado no existe con ese nombre; el baseline «7 archivos / 141 tests» no es
reproducible) y **una tercera resultó falsa en dirección inversa**: C parafraseó mal el §9.2-B5 del
dossier y escribió dos secciones de evidencia sobre esa paráfrasis antes de releer el original, que
**acertaba** la causa (`_check_assets_are_justified` 3/4 = 0.75, `monthly_report` always-on sin
pain); **(b)** una **regresión que C introdujo y tuvo que corregir dentro de la
fase**: pasar `site_presence_report` al build del gate sin pasarlo al del delivery report volvió a
divergir los dos reportes del mismo run (AC3), y lo expuso
`test_gate_matches_delivery_report_same_run`; **(c)** el barrido archivo-por-archivo que exige la
prohibición de correr `tests/commercial_documents` completo, más demostrar con `git stash` que los 14
failed / 9 errors del árbol ancho son **preexistentes en HEAD**.

Lo que el presupuesto pretendía proteger **no se perdió**, y aquí importa más que en B o D porque C
tenía un **punto de partición predefinido** (`C1' = C1+C2`, `C2' = C3+C4`): **no se usó, con motivo.**
C2 y C3 resultaron ser **una sola cadena causal** — el mismo concepto de «promesa» vivido en tres
superficies — así que la partición prescrita habría dejado exactamente el **estado intermedio
prohibido** por el prompt (propuesta dinámica + matriz estática ⟹ artefactos que se contradicen). Se
ejecutó la fase entera y se registra el exceso en vez de cortar por un punto que no era una costura
real → `10-analisis` §6 **DA-C4**. El candado (`test_fase_c_propuesta_dinamica.py`, 17 casos) se
escribió **antes** de tocar producción y su rojo quedó capturado
(`tdd-colecta-ROJO.txt`, `tdd-comportamiento-ROJO.txt`); master nunca tuvo el candado en rojo.

✅ **Sin colisión de nombres en `evidence/FASE-C/`**: a diferencia de `evidence/FASE-B/` y
`evidence/FASE-D/`, el directorio **no existía** antes de este plan — los 20 archivos los creó el
commit `c1bf5e2` y `git log --all -- evidence/FASE-C/` no devuelve ningún otro commit. Verificado, no
asumido.

**Nota sobre las iteraciones de FASE-E** — medidas con la **misma unidad** que las notas de B, D y C
(ids de mensaje de asistente únicos del transcript, `evidence/FASE-D/measure_iterations.py`): **72
hasta el commit de código** (`b0ab27a`, 2026-09-03T20:14:26-05:00) sobre un presupuesto de ≤30 ⟹
**2,4× de exceso**, igual que C. Medición en `evidence/FASE-E/faseE_iteraciones.txt`.

El sobrecosto de E no vino del código (el writer es ~30 líneas passthrough; el fix de A6 es una clave
en 5 dicts) sino de lo que el presupuesto no contemplaba: **(a)** revalidar las citas del prompt contra
el código (L-A6) — la premisa de paralelizabilidad de §4 era **falsa** (ambos tracks editan `main.py` →
S-E1) y el punto de persistencia correcto requirió trazar `site_presence_snapshot` vs
`site_presence_report` en `main.py`; **(b)** el censo E4 de consumidores del snapshot (6 activos + 1
ruta viva + 3 muertos) que dejó el insumo duro de F; **(c)** escribir 10 tests con dos sondas no
triviales (passthrough de campos de probe; e2e `DeliveryQualityReportGenerator` → `proposal_asset_gate`).

**Nota sobre las iteraciones de FASE-G** — medidas con la **misma unidad** que las notas de B, D,
C y E (ids de mensaje de asistente únicos del transcript, `evidence/FASE-D/measure_iterations.py`):
**154 hasta el commit de código** (`c317cda`, corte 2026-09-04T08:13:19-05:00; 158 con el cierre
incluido) sobre un presupuesto de ≤50 ⟹ **3,1× de exceso**. Medición en
`evidence/FASE-G/faseG_iteraciones.txt`. El sobrecosto: (a) 3 archivos de tests ya existentes
codificaban el contrato pre-G (doc_audit WARNING-mode, integración de reconciler, mensaje) y hubo
que actualizarlos con registro; (b) verificación de que el único fallo del batch era preexistente
en HEAD (worktree temporal) antes de atribuirlo; (c) el fixture anti-reversión corre el gate REAL
(en vez de un mock), que fue el criterio de aceptación de NR3. ⚠️ **Nota faltante de FASE-F
registrada por G (2026-09-04)**: la fila de F dice «ver nota abajo» pero su nota de iteraciones
nunca se escribió en este README — su cifra (182) solo vive en la fila y en `10-analisis` §7.

**Nota sobre las iteraciones de FASE-H** — cifra publicada en
`evidence/FASE-H/faseH_iteraciones.txt`: **≥155 llamadas de herramienta contra presupuesto ≤35**
(tope R2: 60) ⟹ **≈4,4× de exceso, PRESUPUESTO INCUMPLIDO y reportado como tal**. ⚠️ **Es la
primera fase cuya cifra NO pudo producirla el instrumento canónico**
(`evidence/FASE-D/measure_iterations.py`, ids de mensaje de asistente únicos del transcript, corte
en el commit de código): el transcript vive fuera del workspace y la política de permisos bloquea
su lectura bajo sandbox. El número es **auto-reporte auditable por partes** (parent ~58 +
Subagente 2 97 `tool_use` + Subagente 1 sin reporte del runtime) en unidad **`tool_use`, no ids
únicos** ⟹ **no es la misma métrica** de las fases anteriores (**S22**). Lo que cualitativamente
costó la fase, y que VERIFY debe pesar al recalibrar:
(a) **re-partir la delegación** cuando §4 declaraba tracks que compartían archivo (**L-H2**);
(b) **re-verificar citas fósiles** del propio prompt — cinco números de línea desplazados y un
archivo de test que no existe con el nombre citado (**L-H4**, sexto caso de la clase L-A6);
(c) **barrer hasta la fuente** el hallazgo V11, que resultó tener dos residuos y un criterio
compartido, no un texto viejo en un sitio (**L-H6**);
(d) un track delegante que reportó dos veces con cifras contradictorias entre sí — resolvió el
árbol de trabajo, no su informe (**L-H1**).

**Nota de FASE-VERIFY (2026-09-04)** — dos cosas que el encabezado de este README afirmaba y que la
verificación midió distinto: **(1)** «C **erradicó la causa raíz** del plan» es correcto para la **cadena
causal** (punto 8, `no_breach`, `is_coherent`) y **no** para la **clase de defecto**: VERIFY encontró tres
instancias nuevas de «dos representaciones del mismo hecho sin oráculo» que solo se ven sobre artefactos
reales (S-I2 severidad no serializada, S-V3 `coverage_ratio` no publicado, S-I7 mensaje↔`details`).
**(2)** El presupuesto por fase se excedió en **las nueve fases medibles** y **VERIFY tampoco pudo medir el
suyo con el instrumento canónico** ⟹ la recomendación formal al executor (**DA-V6** / S22) es **recalibrar
×3 o retirar la métrica**, fijando el corte «hasta el commit de código»; y queda la regla nueva de
certificación: **un AC no legible en el artefacto se marca ⚠️, no ✅** (**L-V1** / DA-V3).

**Conflicto de nombres en `evidence/FASE-VERIFY/`** (misma clase que L-B4 registró para `FASE-B/` y
`FASE-D/`): el directorio ya contenía evidencia de la **FASE-VERIFY del plan SR-PIPELINE-FIXES**
(`matriz_ac_final.md`, `diff_baseline_vs_h2.md`, `tests_regresion.txt`, `validaciones_quick.txt`,
`tests_guardian_estatico.txt`). La evidencia de **este** plan quedó aislada en
`evidence/FASE-VERIFY/ESTABILIZACION-PRE-TRIBUNAL/` para que ninguna cifra de un plan se lea como la del otro.

**Write-back a QMind ejecutado (2026-09-04, tras confirmación del usuario)**: el notebook `iah-cli-lecciones`
recibió **una** fuente — `10-analisis: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03 (lecciones aprendidas y
decisiones)`, id `01a06dae-b1f5-7a7b-9159-9b2f163b07a2`, vehiculada por
`evidence/FASE-VERIFY/ESTABILIZACION-PRE-TRIBUNAL/QMIND-WRITE-BACK.md`. Esa es la granularidad que el notebook
ya tenía (**una fuente consolidada por plan**), no «una por lección». Clasificación definitiva: **41 = 32 con
texto propio + 7 fusionadas en 4 destinos + 2 excluidas**. Al ejecutar la ingestión la medición rectificó dos
afirmaciones que la propia pasada de VERIFY había escrito en `10-analisis` §9: el balance **33/5/2 sumaba 40
sobre 41**, y la recuperación por formato literal `keywords: *…*` se afirmaba para todas las lecciones cuando
eran **6 de 41** (`10-analisis` §9.1). Instancias 7.ª y 8.ª de la clase que persigue el plan.

**Métricas acumuladas**: ver `09-documentacion-post-proyecto.md` §C.1 y §D y `10-analisis` §7.2.