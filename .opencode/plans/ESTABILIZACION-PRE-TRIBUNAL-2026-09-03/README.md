# ESTABILIZACION-PRE-TRIBUNAL-2026-09-03

> **Versión objetivo**: 4.75.0 | **Estado**: 🟡 EN EJECUCIÓN — 1 de 11 sesiones ejecutadas (FASE-A ✅ 2026-09-03)
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
| FASE-H | 8 | Quirúrgicos (Nivel 3.8): V6 `except Exception` → logging visible, V7 guard `__iter__` → validación numérica, V8 dedup `low_organic_visibility`, V11 residuos D6, V13 dos `MetadataValidator` gemelos, V12 documentar decisión OPS del `.env` | **BAJA-MEDIA** | **DELEGADO** — ediciones localizadas e independientes, replican patrones ya fijados | No |
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
| AC8 | Los docstrings `publication_gates.py:4` y `:162` y `AGENTS.md` (tabla Módulos Activos + bloque FASE 4.5) dicen **11 blocking + 2 advisory**, corregidos **en el mismo commit** que AC7 (nunca por delante) | D | `validate_agents_md.py` + grep | H10 mitad documental |
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
| FASE-H | **SÍ** | 6 quirúrgicos independientes y localizados, cada uno con patrón ya fijado en el dossier §12.3 |
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
  `tests/asset_generation`.
- **`log_phase_completion.py` SIN `--release`** en fases intermedias; bump/CHANGELOG solo en RELEASE
  (anti-deuda §2.5: cada fase cierra su propia documentación, no se difiere).
- **Clasificar fallos de `run_all_validations.py`**: Version Sync → `sync_versions.py`; Document
  Integration → README; NO re-correr la suite completa.
- **V12 (`.env`) es decisión OPS, no de código**: documentar en FASE-H, no editar `.env` en una fase
  de refactorización.
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
| FASE-B | ⬜ Pendiente | — | — | — | Biyección triple mapa↔emisión↔narrativa |
| FASE-C | ⬜ Pendiente | — | — | — | Punto 8 propuesta dinámica |
| FASE-D | ⬜ Pendiente | — | — | — | Severidad 11+2 |
| FASE-E | ⬜ Pendiente | — | — | — | A2 + A6 persistencia |
| FASE-F | ⬜ Pendiente | — | — | — | A4 + A1 + N11 |
| FASE-G | ⬜ Pendiente | — | — | — | Ceguera de gates |
| FASE-H | ⬜ Pendiente | — | — | — | Quirúrgicos |
| FASE-I | ⬜ Pendiente | — | — | — | E2E única Salento Real |
| FASE-VERIFY | ⬜ Pendiente | — | — | — | Certificación + análisis |
| FASE-RELEASE-4.75.0 | ⬜ Pendiente | — | — | — | Cierre documental |

**Métricas acumuladas**: ver `09-documentacion-post-proyecto.md` §D.
