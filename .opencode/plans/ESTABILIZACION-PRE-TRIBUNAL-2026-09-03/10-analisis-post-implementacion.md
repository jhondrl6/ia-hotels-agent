# 10 — Análisis Post-Implementación

> **Plan**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03
> **Estado**: 🟡 EN CURSO — archivo creado **desde la concepción** del plan (executor §4), no al final.
> **Propósito**: capitalizar la experiencia (lecciones), certificar los ACs contra evidencia real y dar
> trazabilidad de que los fixes del dossier fueron superados. Lo llena principalmente **FASE-VERIFY**.
> **Regla**: cada fase actualiza su fila de Resumen de Ejecución al cierre; VERIFY consolida el resto.

---

## 1. Resumen de Ejecución

> Una fila por fase. Se actualiza al cierre de cada sesión (Post-Ejecución punto 4).

| # | Fase | Objetivo | Complejidad | Modo | Iter (presup./usadas) | Estado | Notas |
|---|------|----------|-------------|------|----------------------|--------|-------|
| 1 | FASE-A | Fuente única identidad servicio↔asset↔pain | ALTA | DIRECTO | 55 / **55** | ✅ Completada (2026-09-03) | Canónico en `modules/common/service_identity.py` (dos capas). Censo real: **14** registros, no ≥9 → 6 derivados, 6 validados contra Capa 1, 2 fuera de alcance. 21 funciones test / 37 casos, TDD visto en ROJO (27 fallados) antes de implementar. Baseline 848/2 preservado byte-idéntico. **Desvíos**: `opportunity_scorer.py` figuraba en A4 y NO se tocó (namespace `brecha_type` distinto — DA8); el censo corrigió 3 datos del dossier (N-A2, tamaño de `ASSET_TO_PAIN_ID`, registro #14 no censado) |
| 2 | FASE-B | Biyección mapa↔emisión `detect_pains` | MEDIA-ALTA | DIRECTO | 40 / — | ⬜ Pendiente | |
| 3 | FASE-C | **Punto 8** propuesta dinámica | **MÁXIMA** | DIRECTO | 60 / — | ⬜ Pendiente | Punto de partición predefinido C1'/C2' si R2 se agota |
| 4 | FASE-D | Severidad 11 blocking + 2 advisory | MEDIA | MIXTO | 35 / — | ⬜ Pendiente | D3 documental delegable, mismo commit |
| 5 | FASE-E | A2 snapshot + A6 `asset_path` | MEDIA | DELEGADO | 30 / — | ⬜ Pendiente | 2 tracks paralelos |
| 6 | FASE-F | A4 oráculo único + A1 skipped≠passed + N11 | MEDIA-ALTA | DIRECTO | 45 / — | ⬜ Pendiente | |
| 7 | FASE-G | Ceguera de gates (Nivel 3.7) | MEDIA-ALTA | DIRECTO | 50 / — | ⬜ Pendiente | V5 anti-reversión BUG-6 |
| 8 | FASE-H | Quirúrgicos (Nivel 3.8) | BAJA-MEDIA | DELEGADO | 35 / — | ⬜ Pendiente | 2 subagentes, regiones distintas |
| 9 | FASE-I | E2E única `v4complete` Salento Real | BAJA | MIXTO | 25 / — | ⬜ Pendiente | 1 comando largo |
| 10 | FASE-VERIFY | Certificación + análisis post-implementación | MEDIA | DIRECTO | 40 / — | ⬜ Pendiente | No delegable (§4.6) |
| 11 | FASE-RELEASE-4.75.0 | Cierre documental | BAJA | DELEGABLE | 25 / — | ⬜ Pendiente | |

**Total presupuestado**: ≤440 iteraciones (R2 tope por fase: 60).

---

## 2. Verificación de Criterios de Aceptación (AC1-AC12)

> La llena **FASE-VERIFY** (V1). Regla de oro: certificar contra **salida real**, no contra la presencia de
> un string en el código (lección `revalidar-citas-de-c-digo-no-revalida-premisas`).

| AC | En una línea | Estado | Evidencia (archivo + campo + valor) | Test que lo fija | Fase |
|----|--------------|--------|-------------------------------------|------------------|------|
| AC1 | Una fuente canónica de identidad servicio↔asset↔pain | 🟡 Evidencia aportada por A — VERIFY certifica | `modules/common/service_identity.py` → `SERVICE_IDENTITIES` (8 `ServiceIdentity` congeladas). 14 registros censados: 6 derivados, 6 validados contra Capa 1, 2 fuera de alcance. Grep de los 6 IDs fantasma en `modules/commercial_documents` + `modules/asset_generation` → **0** (`temp/faseA_validations.txt`) | `test_canonico_existe_y_es_integral`, `test_cero_ids_fantasma_*`, `test_registro_derivado_no_es_una_copia_literal` (guardián AST), `test_canonico_no_redeclara_tablas_paralelas` (L-NC4) | A |
| AC2 | Drift «8 vs 7» corregido en sus **tres** copias + contract test | 🟡 Evidencia aportada por A — VERIFY certifica | Las 3 copias **eliminadas físicamente** (no comparadas): `proposal_asset_alignment.py:35-40`, `service_catalog.py` (+ su mutación post-hoc borrada), `v4_proposal_generator.py:1332`. Contrafactual (`temp/faseA_contrafactual.txt`): contenido **y orden** idénticos al literal previo | `test_narrativa_no_hardcodea_conteo_de_servicios` — prohíbe la **forma numeral** `\b\d+\s+servic` en los 7 módulos de narrativa, sin comparar contra un número (L-NC10) | A |
| AC3 | `ASSET_TO_PAIN_ID["monthly_report"]` resuelto a favor del registro canónico | 🟡 Evidencia aportada por A — VERIFY certifica | `ASSET_TO_PAIN_ID` derivado ⟹ `monthly_report → no_monthly_report`. La perla `no_faq_schema` no existe ya en ningún registro del repo | `test_un_asset_no_se_atribuye_a_pains_distintos_entre_registros` (esperado **computado** desde el canónico) + `test_divergencias_trigger_atribucion_declaradas_y_justificadas` (bidireccional, no vacuo) | A |
| AC4 | Biyección mapa↔emisión (9 pains muertos resueltos) | ⬜ | *(pendiente)* | *(pendiente)* | B |
| AC5 | Punto 8: `no_breach = 0` por construcción | ⬜ | *(pendiente)* | *(pendiente)* | C |
| AC6 | Tautología de coverage + `is_coherent` estructural disueltas | ⬜ | *(pendiente)* | *(pendiente)* | C+F |
| AC7 | Severidad 11 blocking + 2 advisory | ⬜ | *(pendiente)* | *(pendiente)* | D |
| AC8 | Advisory con piso explícito + WARNING a `human_checklist` | ⬜ | *(pendiente)* | *(pendiente)* | D |
| AC9 | A2 snapshot persistido + A6 `asset_path` poblado | ⬜ | *(pendiente)* | *(pendiente)* | E |
| AC10 | A4 oráculo único decide y escribe el mensaje | ⬜ | *(pendiente)* | *(pendiente)* | F |
| AC11 | A1 `skipped != passed` (`NOT_EVALUATED`) | ⬜ | *(pendiente)* | *(pendiente)* | F |
| AC12 | N11/P9 gate respeta `is_coherent` | ⬜ | *(pendiente)* | *(pendiente)* | F |

**Estados posibles**: ✅ CERTIFICADO · ⚠️ PARCIAL · ❌ NO CERTIFICADO. Todo ⚠️/❌ abre un seguimiento (§5).

---

## 3. Verificación de No-Regresión (NR7-NR12 — familia «de producto»)

> La llena **FASE-VERIFY** (V2) con delta medido contra el baseline `FASE-D_salentoreal_post_guard`.
> Hay **dos familias** de NRs: **NR1-NR6 «de hallazgo»** (doc_audit_consistency con datos, critical_issues,
> escotillas V5/V9, suite 848, perfil de corrida — definidas en `README.md` §ACs de no-regresión) y
> **NR7-NR12 «de producto»** (tabla siguiente — lo que el plan no debe romper). VERIFY certifica ambas.

| NR | En una línea | Baseline | Corrida I | Delta | Estado |
|----|--------------|----------|-----------|-------|--------|
| NR7 | Conteo de tests no regresó | 848 passed / 2 skipped | *(pendiente)* | *(pendiente)* | ⬜ |
| NR8 | `coherence` no cayó por causa del plan | 0.88 | *(pendiente)* | *(pendiente)* | ⬜ |
| NR9 | Los 13 gates siguen ejecutándose (11+2) | 13 | *(pendiente)* | *(pendiente)* | ⬜ |
| NR10 | ZIP de delivery sigue generándose | generado | *(pendiente)* | *(pendiente)* | ⬜ |
| NR11 | `asset_confidence` sigue blocking | blocking | *(pendiente)* | *(pendiente)* | ⬜ |
| NR12 | Sin nuevas anomalías vs baseline | — | *(pendiente)* | *(pendiente)* | ⬜ |

**Anomalías preexistentes** (NO cuentan como regresión): gemini 403, PageSpeed key inválida (V12),
cualquier otra que ya estuviera en el baseline. FASE-I las clasifica; VERIFY las confirma.

---

## 4. Fixes superados — análisis post-implementación

> **Petición literal del usuario**: *«análisis post implementación de que los diferentes fixes fueron
> superados»*. La llena **FASE-VERIFY** (V3). Una tabla por familia del dossier.

### 4.1 §9.1 — Huecos vivos A1-A6

| Hallazgo | Qué era | Estado final | Evidencia | Test que lo fija |
|----------|---------|--------------|-----------|------------------|
| A1 | `skipped` contaba como `passed` en delivery_quality_report (`:250-257`) | ⬜ | *(pendiente)* | *(pendiente)* |
| A2 | `site_presence_snapshot` nunca persistido en disco (0 resultados en historial) | ⬜ | *(pendiente)* | *(pendiente)* |
| A3 | `promised_assets_exist` solo pre-gen (`:670`), peso 2.0, `score=1.0` hardcode | ⬜ | *(pendiente)* | *(pendiente)* |
| A4 | Dos oráculos de presencia: permisivo decide, estricto escribe (V15) | ⬜ | *(pendiente)* | *(pendiente)* |
| A5 | Dos builders silenciosamente distintos; skip sin estado `NO_ASSET_MAPPED` | ⬜ | *(pendiente)* | *(pendiente)* |
| A6 | `asset_path = null` en entradas LINKED de proposal_asset_matrix | ⬜ | *(pendiente)* | *(pendiente)* |

### 4.2 §9.2 — Mecanismos del síntoma B1-B5

| Hallazgo | Qué era | Estado final | Evidencia | Test que lo fija |
|----------|---------|--------------|-----------|------------------|
| B1 | Matriz 7 servicios: 6 NO_BREACH + 1 LINKED; ledger resolved = 3 | ⬜ | *(pendiente)* | *(pendiente)* |
| B2 | Registro estático 7/7 vs runtime 4 assets; intersección {llms_txt} | ⬜ | *(pendiente)* | *(pendiente)* |
| B4 | Palancas de coverage 0.125-0.714; 7 permisivo = 0.571 | ⬜ | *(pendiente)* | *(pendiente)* |
| B5 | Δcoherence +0.0000 exacto; 2 candados (`score=1.0` + unión `:703`) | ⬜ | *(pendiente)* | *(pendiente)* |

### 4.3 §4 — 8 caídas silenciosas · §3 — 3 candados rotos

| Hallazgo | Qué era | Estado final | Evidencia | Test que lo fija |
|----------|---------|--------------|-----------|------------------|
| §4 caídas | 8 pains detectados que nunca llegan al ledger | ⬜ | *(pendiente)* | *(pendiente)* |
| §3 biyección | 0 tests fijan la biyección mapa↔emisión | ⬜ | *(pendiente)* | *(pendiente)* |
| §3 narrativa | Doc/propuesta venden lo no diagnosticado | ⬜ | *(pendiente)* | *(pendiente)* |
| §3 severidad | Estructura de severidad declarada ≠ implementada | ⬜ | *(pendiente)* | *(pendiente)* |

### 4.4 §12.3 — Validaciones externas V1-V16

| Hallazgo | Qué era | Estado final | Evidencia |
|----------|---------|--------------|-----------|
| V1 | 9 pains muertos (mapa declara 27, `detect_pains` ~18) | ⬜ | *(pendiente)* |
| V2 | 6 IDs fantasma en `ELEMENTO_KB_TO_PAIN_ID` | ✅ Superado (FASE-A 2026-09-03) | `v4_diagnostic_generator.py:126-166`: los 6 pain_id inexistentes y 1 asset inexistente → `None`/asset real. Comportamiento preservado, verificado consumidor por consumidor: `conditional_generator.py:325-326` es ruta muerta (`generate_for_faltantes` sin llamadores), `ELEMENTOS_MONETIZABLES` tiene 0 consumidores, `:3083/:3086` solo iteran `.keys()`. Grep de AC → **0**. Lo fija `test_cero_ids_fantasma_en_modulos_migrados` |
| V3 | ≥9 registros no canónicos | ✅ Superado (FASE-A 2026-09-03) | Censo real: **14** registros (`evidence/FASE-A/censo-registros.md`). Arquitectura de dos capas: Capa 1 `PainSolutionMapper.PAIN_SOLUTION_MAP` (27 pains, universo de pain_id, contenido intacto) + Capa 2 `SERVICE_IDENTITIES` (8). **6 derivados**, **6 validados contra Capa 1** con razón registrada, 2 fuera de alcance. La perla `monthly_report → no_faq_schema` ya no existe en ningún registro. Lo fijan `test_registro_derivado_no_es_una_copia_literal` (AST, fixpoint transitivo), `test_un_asset_no_se_atribuye_a_pains_distintos_entre_registros` y los `test_*_valida_contra_capa_1` |
| V5 | `_JUSTIFIED_STATUSES` incluye `ASSET_GENERATED` (anti-reversión BUG-6) | ⬜ | *(pendiente)* |
| V6 | `except Exception: return brechas` + caché (`v4_diagnostic_generator.py:3189-3194`) | ⬜ | *(pendiente)* |
| V7 | Guard `__iter__` hace `low_ota_divergence` no-disparable (triple defecto) | ⬜ | *(pendiente)* |
| V8 | `low_organic_visibility` emitido dos veces | ⬜ | *(pendiente)* |
| V9 | `pain_ledger` vacío = PASS pero `pain_ledger_resolved` vacío = BLOCKED | ⬜ | *(pendiente)* |
| V10 | G8 «some below threshold» → WARNING → ZIP procede (confirmación, sin acción) | ➖ No aplica | Confirmado en FASE-G |
| V11 | Residuos D6 en `v4_diagnostic_generator.py:1952` y `v4_comprehensive.py:1841` | ⬜ | *(pendiente)* |
| V12 | `.env`: `GOOGLE_PAGESPEED_API_KEY` 3 chars inválido (trampa) | ➖ No aplica (OPS) | Documentado, `.env` no editado |
| V13 | Dos `MetadataValidator` gemelos | ⬜ | *(pendiente)* |
| V14 | Drift «8 vs 7» tercera copia en `v4_proposal_generator.py:1332` | ✅ Superado (FASE-A 2026-09-03) | Las **tres** copias eliminadas por derivación, no por comparación. Contrafactual medido (`temp/faseA_contrafactual.txt`): `PROPOSAL_SERVICE_TO_ASSET`, `service_brecha_candidates` y `SERVICE_CATALOG` idénticos en contenido **y orden** al literal previo; las tablas renderizadas siguen teniendo 7 filas. Lo fija `test_narrativa_no_hardcodea_conteo_de_servicios`, que prohíbe la **forma numeral** `\b\d+\s+servic` en 7 módulos de narrativa sin comparar contra un número (L-NC10). **Detalle del censo**: un primer regex `\b\d+\s+servicio` halló solo 2 de las 3 copias porque no casaba con el inglés «8 services» |
| V15 | Matriz 6 NO_BREACH pero gate reporta 3 (`_presence_resolved` absorbió 3) | ⬜ | *(pendiente)* |
| V16 | `is_coherent: false` en 3 artefactos / 6 copias (`assets_are_justified 3/4 = 0.75`) | ⬜ | *(pendiente)* |

### 4.5 ROADMAP §13 — Deudas

| Deuda | Qué era | Estado final | Evidencia |
|-------|---------|--------------|-----------|
| P9 | Gate ignora `is_coherent` (la más grave) | ⬜ | *(pendiente)* — AC12 |
| P10 | Registros dispersos sin fuente única | ✅ Superado (FASE-A) — **extensión A5 abierta → FASE-C** | `modules/common/service_identity.py` es la fuente única; 14 registros censados, 6 derivados, 6 validados contra Capa 1 con razón registrada, 2 fuera de alcance. La parte de P10 que extendía A5 (los 2 builders que hacen skip silencioso en `proposal_asset_alignment.py:609-612`/`:792-794`) **no se tocó** — era restricción explícita de A4 y pertenece a C3 |
| P11 | `precision_tier` degrada a «C» en silencio | ➖ No aplica (diferido) | Seguimiento abierto |
| P12 | `promised_assets_exist` solo pre-gen | ⬜ | *(pendiente)* — A3 |
| H7 | Nombres timestamped + oráculo no persistido | ⬜ | *(pendiente)* — A2 |
| H8 | `publication_state.py` huérfano | ⬜ | *(pendiente)* — FASE-F |
| H9 | 3 rutas blocking + G9 green skip | ⬜ | *(pendiente)* — A1 |
| H10 | Docstrings 10+3 vs código 13 | ⬜ | *(pendiente)* — AC7 |

### 4.6 Veredicto global sobre la causa raíz §12.5

> *«contrato de detección fragmentado y sin candado — ≥9 registros no canónicos, consumidores derivan de
> copias parciales, 0 tests fijan la biyección»*

**Estado**: 🟡 Parcial — 1 de los 3 cláusulas de la causa raíz cerrada y fijada por contract tests.

| Cláusula de la causa raíz | Estado tras FASE-A | Qué la fija |
|---------------------------|--------------------|-------------|
| «≥9 registros no canónicos» | ✅ Cerrada — 14 censados, 1 canónico, 6 derivados, 6 validados contra Capa 1 con razón registrada | `tests/common/test_service_identity_registry.py` (guardián AST de derivación + validación contra Capa 1 + L-NC4 anti-tabla-paralela) |
| «consumidores derivan de copias parciales» | 🟡 Cerrada en los 6 universos migrados; los 6 validados siguen siendo literales **por decisión registrada**, no por descuido | Ídem, sección 6 del suite |
| «0 tests fijan la biyección» | ⬜ Abierta — es **FASE-B** (AC4). A no la tocó: era restricción explícita del prompt | *(pendiente)* `tests/commercial_documents/test_pain_bijection.py` |

*(VERIFY redacta aquí el juicio final justificado con los contract tests de A y B y el guardián AST de B.)*

---

## 5. Seguimientos abiertos

> Temas detectados que requieren acción futura pero **no** bloquean el cierre del plan. Todo AC ⚠️/❌ y
> todo «No aplica — diferido» del §4 aterriza aquí con causa y próximo paso.

| # | Tema | Origen | Por qué se difiere | Próximo paso |
|---|------|--------|--------------------|--------------|
| S1 | Tribunal multi-bot | Fuera de alcance del plan | Plan paralelo anclado en P6 (memoria `plan-tribunal-bots-anclado-en-p6`) | Retomar tras estabilización |
| S2 | Premisa de brecha de analytics (57% de $4.04M/mes deriva de nuestra credencial faltante) | FASE-H V8 | V8 es solo dedup; reescribir la premisa excede el alcance | Evaluar en plan financiero |
| S3 | P11 `precision_tier` degrada a «C» | ROADMAP §13 | No es causa raíz del dossier | Plan de degradación silenciosa |
| S4 | `.env` placeholder inválido de PageSpeed | V12 | Decisión OPS, no de código | OPS: sembrar clave canónica |
| S5 | **2 tests rojos preexistentes en `test_proposal_dynamic.py`** — NO son regresión del plan | FASE-A (verificados byte-idénticos contra `temp/faseA_predinamico.txt`, evidencia pre-cambio) | (1) `TestTechnicalAssetsTable::test_technical_assets_table_shows_both_assets` espera «Optimización de Tráfico Indirecto» en `TECHNICAL_ASSET_CATALOG`; (2) `TestFase3ConditionalServicesFiltering::test_no_assets_no_presence_all_excluded` choca con el footnote D-PF1 (territorio de FASE-C). Ambos ya fallaban antes de tocar nada | **No atribuirlos al plan.** FASE-C decide sobre el segundo al reescribir la promesa; el primero es de catálogo técnico, fuera de este plan |
| S6 | **N-A1 — precondición dura de FASE-B**: `narratives` descarta 11 pain_id en silencio | FASE-A (`v4_diagnostic_generator.py:3338-3339`) | `missing_llmstxt` está **a la vez** en los 9 pains muertos de V1 y en esa lista de descarte. Darle punto de emisión en B sin tocar `narratives` deja el fix **inerte**: el pain llegaría al ledger pero no a la narrativa | FASE-B debe tratar `narratives` como parte de la biyección, no solo `detect_pains` |
| S7 | 7 entradas inalcanzables del scorer + fallback silencioso `'cms_defaults'` en `pain_to_type` | FASE-A (censo de `opportunity_scorer.py`) | El puente `pain_to_type` tiene 10 entradas y cae a `'cms_defaults'` **sin avisar**; 7 de sus claves no son alcanzables desde el canónico. Es dinero-adyacente y rompería `tests/financial_engine/test_opportunity_scorer*.py` | Misma familia que V6 (`except Exception`) y P11 (`precision_tier` → `"C"`). Plan de degradación silenciosa (ver S3) |
| S8 | **`PAIN_TO_PRESENCE_ASSET` 6 vs 13** — no derivado a propósito | FASE-A (`pain_ledger.py`) | La derivación completa desde el canónico produce 13 entradas frente a sus 6 actuales y **cambia la semántica de `apply_site_verification`**. Es exactamente el doble oráculo de A4/V15 | **Insumo directo de FASE-F** (F1 oráculo único). No derivarlo en otra fase |
| S9 | **Registro #14 no censado por el dossier**: `modules/quality/asset_semantics_validator.INVALID_MAPPINGS` | FASE-A | Su propio comentario `:23-25` documenta una auditoría FASE-2 que halló sus claves **invertidas** (asset_type donde iba pain_id). Eso prueba que la perla de V3 (`monthly_report → no_faq_schema`) es un fósil **no corregido** de esa misma inversión | Fuera de alcance de A (módulo `modules/quality/`). FASE-H lo evalúa junto a V13 (los gemelos `MetadataValidator`, mismo módulo) |
| S10 | Bug latente corregido de paso: `monthly_report` ya valida como IMPLEMENT | FASE-A (contrafactual) | Antes quedaba bloqueado por un guard anti-alucinación que lo comparaba contra `no_faq_schema`. Hoy el consumidor único (`:1410`) nunca lo alcanza (`iterado=False`), así que **no hay cambio observable**; si FASE-C llega a incluir Informe Mensual en el conjunto iterado, ya funcionará correctamente | Ninguno — registrar para que FASE-C no lo redescubra como anomalía |
| S11 | **Conteos de tests documentados quedaron desactualizados por +21** | FASE-A (memoria `conteos-tests-documentados-metodo-def_test`) | `AGENTS.md` y `README.md` declaran **3,689 funciones / 284 archivos**; el real tras A es **3,710 / 285**, y la fila `common` de la tabla de cobertura por módulo dice 16 cuando ahora es 37. **No se editaron**: `dependencias-fases.md` §3 asigna `AGENTS.md` a **D → RELEASE**, y la regla del plan es registrar el seguimiento y NO tocar un archivo cuya fase dueña anterior no está ✅ | **FASE-RELEASE** lo cierra (ya es dueña del sync documental y corre `sync_versions.py` sobre esos mismos archivos). FASE-D debe recordarlo al editar `AGENTS.md` por AC8: actualizar los conteos **en el mismo commit**, no por delante |
| S12 | *(agregar los que abran VERIFY y las fases)* | | | |

---

## 6. Decisiones Arquitectónicas

> Decisiones no triviales tomadas durante el plan, con rationale y alternativas rechazadas.

| # | Decisión | Rationale | Alternativa rechazada | Fase |
|---|----------|-----------|----------------------|------|
| DA1 | Fuente única (A/B) **antes** que punto 8 (C) | ROADMAP §7.2: «decidir cuál registro manda es precondición de la propuesta dinámica»; reconcilia con §10 del dossier (un «orden sugerido», no mandatorio) **adelantando deliberadamente H10** (independiente de B/C, insumo de F3 y del tratamiento de ledger vacío — ver matiz en `README.md` §Por qué este orden) | Ejecutar §10 literal (punto 8 primero) — rechazado porque el punto 8 sobre registros fragmentados reproduciría el drift | Concepción |
| DA2 | H10 documental y conductual en el **mismo commit** (AC7+AC8) | Memoria `decision-advisory-gates-2-no-3`: los docstrings sueltos se desincronizan del código | Commits separados — rechazado | D |
| DA3 | Punto de partición C1'/C2' **predefinido** | C es la única fase con riesgo real de agotar R2 (60); un C a medias produce artefactos que se contradicen (patrón de los 3 artefactos SalenteReal con `is_coherent: false`) | Improvisar la partición — rechazado | C |
| DA4 | V5 se cierra **sin reversar** BUG-6 | Anti-reversión Zione 2026-07-25: cerrar la escotilla exige distinguir «asset generado y mencionado» de «generado y silencioso», no revertir el status | Revertir `ASSET_GENERATED` de `_JUSTIFIED_STATUSES` — rechazado (segundo péndulo D2→tautología) | G |
| DA5 | V12 se **documenta**, no se edita `.env` | Es decisión OPS; editar `.env` en una fase de refactorización mezcla responsabilidades | Editar `.env` — rechazado | H |
| DA6 | **Arquitectura de dos capas**: Capa 1 = `PainSolutionMapper.PAIN_SOLUTION_MAP` (27 pains) como **universo de pain_id**, contenido intacto. Capa 2 = **nuevo** `SERVICE_IDENTITIES` (8 entradas) como identidad servicio↔asset↔pain | El dossier pedía «decidir cuál registro manda». La respuesta honesta es que **mandan dos, preguntas distintas**: `PAIN_SOLUTION_MAP` responde «qué pains existen y cómo se narran» (27, universo de detección); `SERVICE_IDENTITIES` responde «qué se vende, qué asset lo entrega y qué pain lo hace vendible» (8). Un solo registro no puede servir a las dos sin arrastrar 19 pains no vendibles a la propuesta ni podar el universo de detección. Regla que queda fijada: **ningún registro del repo puede declarar un pain_id ausente de Capa 1** | (a) Promover `PAIN_SOLUTION_MAP` a único canónico y derivar todo de él — rechazado: obliga a la propuesta a recorrer 27 pains y re-introduce por otra vía el `no_breach` que C debe llevar a 0. (b) Promover `PROPOSAL_SERVICE_TO_ASSET` — rechazado: es un dict plano `service→asset` sin pain_id ni descripción, habría que ensancharlo y romper su consumidor de alignment. (c) Crear el canónico dentro de `asset_generation/` y que los demás importen de ahí — rechazado: `commercial_documents` ya importa de `asset_generation` y `financial_engine` también; un canónico ahí convierte una hoja en raíz de ciclo | A |
| DA7 | Ubicación: **`modules/common/service_identity.py`**, con **cero imports del proyecto** | `modules/common/` ya es el hogar de loaders compartidos sin dependencias (YAML/fallback). Un canónico sin imports puede ser consumido por `asset_generation`, `commercial_documents` y `financial_engine` a la vez sin crear un solo ciclo — que es exactamente lo que impediría la adopción y empujaría a alguien a re-copiar la tabla (L-NC4) | Ponerlo en `modules/asset_generation/` (lo que predecía `09` §A) — rechazado por DA6(c). Ponerlo en `data_models/` — rechazado: son modelos Pydantic de dominio, no registros de identidad, y ya tienen sus propios consumidores | A |
| DA8 | **`opportunity_scorer.py` NO se modifica**, aunque figuraba en A4 | Sus claves `no_llms_txt`, `ia_crawler_blocked`, `weak_brand_signals` **no son pain_id**: pertenecen al namespace `brecha_type` (17 entradas propias del scorer), puenteado a pain_id por `pain_to_type` (10 entradas). El grep de AC1 está acotado a `commercial_documents` + `asset_generation` precisamente por eso. Borrarlas rompería `tests/financial_engine/test_opportunity_scorer*.py`, es código dinero-adyacente, y no curaría nada: son dos universos legítimamente distintos | Tratarlos como IDs fantasma y eliminarlos — rechazado: confundir dos namespaces es el mismo error de categoría que produjo la perla `monthly_report → no_faq_schema`. Unificar `brecha_type` y `pain_id` en un solo enum — rechazado para A: es decisión de producto sobre priorización de brechas, excede el presupuesto de la fase y toca dinero; queda como S7 | A |
| DA9 | Criterio **derivar vs validar**: 6 registros se **derivan** del canónico; 6 se **mantienen literales y se validan contra Capa 1** con razón registrada en el propio código y en el suite | Derivar todo es falso rigor: un registro que responde **otra pregunta** no puede derivarse sin cambiar esa respuesta. Ejemplos medidos: `PAIN_TO_ASSET` (11) enruta qué asset *generar* — derivarlo haría que `poor_performance` generara `optimization_guide` en vez de `performance_audit`; `ELEMENTO_KB_TO_PAIN_ID` responde «qué elemento del KB dispara qué pain»; `PAIN_TO_PRESENCE_ASSET` (6) derivado produce 13 y cambia `apply_site_verification`. **Validar contra Capa 1 es suficiente** para impedir el próximo ID fantasma, que es el defecto real de V2/V3 | Derivar los 14 — rechazado: 4 cambios de comportamiento no pedidos en una fase cuyo éxito se mide por delta cero. Dejarlos literales sin validación — rechazado: es el estado que produjo V2 (6 IDs fantasma vivieron años porque nada los contrastaba) | A |
| DA10 | `counts_in_alignment=False` para `informe_mensual` en vez de excluirlo del canónico | BUG-10/FASE-3 excluyó `monthly_report` de `PROPOSAL_SERVICE_TO_ASSET` a propósito: es complemento siempre-activo, no pain-driven. La exclusión vivía como **una omisión en un literal** — invisible e indistinguible de un olvido. Como campo explícito del canónico, la decisión queda **declarada y testeada**, y `PROPOSAL_SERVICE_TO_ASSET` se deriva filtrando por ella | Seguir excluyéndolo del canónico — rechazado: `SERVICE_CATALOG` y `ASSET_TO_PAIN_ID` sí lo necesitan, y esa asimetría era justamente la que fabricó la perla de V3 | A |
| DA11 | **Trigger ≠ atribución**, expresado en dos campos (`pain_id` vs `brecha_candidates`) + un conjunto explícito `REVIEWED_TRIGGER_DIVERGENCES` | Dos mitades de una decisión que ningún registro previo expresaba: `pain_id` es lo que hace **vendible** un servicio; `brecha_candidates` es lo que se le **imputa** en la tabla con su costo. Divergen en 2 de 8 (`seo_local`, `optimizacion_ia_generativa`) y la divergencia es **correcta**. El conjunto declarado la vuelve revisable: el test es bidireccional y falla tanto si aparece una divergencia no declarada como si se declara una que ya no existe | Un solo campo `pain_id` usado para ambas cosas — rechazado: es la causa directa de V4 («la atribución de brechas excluye por diseño el pain real») que C debe curar. Dejar la divergencia implícita — rechazado: el próximo lector la «corrige» y rompe la atribución | A |
| DA12 | **El orden de inserción es parte del contrato** — documentado en el canónico y verificado por contrafactual | `PROPOSAL_SERVICE_TO_ASSET` se recorre en orden de inserción para construir la tabla de servicios de la propuesta. Una dict-comprehension sobre una tupla ordenada preserva el orden, pero nada lo **garantizaba**: si el canónico hubiera sido un `set` o un `dict` reordenado, la propuesta cambiaría el orden de sus filas sin que ningún test fallara. Se verificó midiendo: contenido **y orden** idénticos al literal previo | Usar `frozenset` para las identidades — rechazado por esto mismo. Fijar el orden con un test de valores — rechazado (L-NC10): se probó por contrafactual y se documentó la invariant en el canónico | A |
| DA13 | Cura de AC2: **prohibir la forma numeral** `\b\d+\s+servic` en la narrativa, no comparar contra un número | L-NC10: un test que fija `len(...) == 7` fosiliza el conteo en vez de curar el drift — cuando C cambie el conjunto, el test fallará por la razón equivocada y alguien lo actualizará a 8, re-fosilizándolo. Prohibir la **forma** («8 services», «7 servicios») ataca el mecanismo real del drift: un número escrito a mano en prosa que nadie sincroniza. El test pasa hoy y seguirá pasando tras C sin edits | Comparar el conteo de la narrativa contra el del canónico — rechazado: es L-NC10 literal. Dejarlo solo en la derivación — rechazado: la derivación cura los 3 registros, no los comentarios y docstrings donde el drift también vivía | A |
| DA14 | *(agregar las que tomen las fases)* | | | |

---

## 7. Métricas de Ejecución

> Datos reales consolidados al cierre (VERIFY + RELEASE).

| Métrica | Valor |
|---------|-------|
| Fases completadas | **1 / 11** (FASE-A ✅ 2026-09-03) |
| Iteraciones totales usadas | **55** / ≤440 |
| Tests al inicio | 3,689 (`def test_`) |
| Tests al cierre | **3,710** (`def test_`, 285 archivos `.py` en `tests/`) — RELEASE cierra el total |
| Contract tests agregados | **21 funciones / 37 casos parametrizados** (`tests/common/test_service_identity_registry.py`) |
| Versión publicada | 4.74.1 → *(4.75.0 al cierre; ninguna fase intermedia la mueve)* |
| ACs certificados | 0 / 12 formalmente — **3 con evidencia aportada** (AC1, AC2, AC3); VERIFY certifica |
| NRs certificados | 0 / 12 formalmente — **NR5 verificado en A** (848 passed / 2 skipped, byte-idéntico) |
| Hallazgos del dossier superados | **4** (V2, V3, V14, P10) de (6+4+8/3+16+8) |
| Lecciones capitalizadas | **5** de FASE-A (§8: L-A1 … L-A5) — VERIFY consolida el total |
| Coherence baseline → final | 0.88 → *(sin cambio: A es delta cero por diseño, medido por contrafactual)* |

---

## 8. Lecciones Aprendidas

> **Petición literal del usuario**: *«lecciones aprendidas»*. La llena **FASE-VERIFY** (V4).
> Formato obligatorio: qué pasó / por qué / qué lo previene + pertinencia INCLUIR/EXCLUIR.
> Las INCLUIR se **proponen** al notebook QMind `iah-cli-lecciones` (el usuario confirma; no se auto-ingiere).

**L-A1 — Un grep de IDs fantasma también cuenta la prosa** *(FASE-A)*
- **Qué pasó**: con el código ya limpio, el grep de AC1 seguía dando 2 positivos. Los habían reintroducido
  **mis propios comentarios explicativos** en `v4_diagnostic_generator.py:160,162`, que nombraban los IDs
  eliminados para explicar qué se había corregido.
- **Por qué**: el criterio de aceptación es textual y no distingue código de comentario. Documentar el
  «antes» en el sitio del «después» vuelve a escribir el string prohibido.
- **Qué lo previene**: el comentario en el sitio debe enunciar **la regla**, no el historial
  («ningún pain_id fuera de `PAIN_SOLUTION_MAP`»); el antes/después pertenece a `evidence/FASE-A/`.
  Al cerrar una fase cuyo AC es un grep, **re-correr el grep después de escribir la documentación**.
- **Pertinencia**: INCLUIR en QMind `iah-cli-lecciones` — aplica a todo AC basado en ausencia de string
  (V11 residuos D6 en FASE-H, V13 en FASE-H).

**L-A2 — El regex del censo se ancla a la raíz, no a la palabra de un idioma** *(FASE-A)*
- **Qué pasó**: el primer escaneo del drift «8 vs 7» usó `\b\d+\s+servicio` y halló **2 de las 3 copias**.
  La tercera decía «8 services» en inglés.
- **Por qué**: `servicio` (servic+io) y `services` (servic+es) comparten raíz pero no terminación. Un
  censo que depende del idioma del comentario no es un censo.
- **Qué lo previene**: anclar a la raíz (`\b\d+\s+servic`) y **validar el escáner contra un conteo conocido
  por otra vía** antes de confiar en su resultado. El contract test definitivo quedó anclado a la raíz.
- **Pertinencia**: INCLUIR en QMind — misma familia que `sondas-url-derivadas-deben-anclarse-al-origen`:
  un derivado que no se ancla al origen real corrompe el resultado.

**L-A3 — Dos namespaces parecidos no son un drift** *(FASE-A)*
- **Qué pasó**: `opportunity_scorer.py` figuraba en A4 por contener `no_llms_txt`, `ia_crawler_blocked` y
  `weak_brand_signals` — los mismos strings que AC1 declara fantasma. **No se modificó**: son claves
  legítimas de `brecha_type` (17 entradas propias del scorer), no pain_id.
- **Por qué**: el dossier censó por **string**, no por **namespace**. Dos universos que comparten nombres
  parecen uno fragmentado. Eliminarlos habría roto `tests/financial_engine/test_opportunity_scorer*.py`,
  en código dinero-adyacente, sin curar nada.
- **Qué lo previene**: antes de declarar un ID «fantasma», **encontrar el registro que legítimamente lo
  posee**. El censo de FASE-A registra namespace y pregunta-que-responde por cada registro, no solo el
  string. Es el mismo error de categoría que produjo la perla `monthly_report → no_faq_schema`.
- **Pertinencia**: INCLUIR en QMind — crítico para FASE-H (V13 gemelos) y para cualquier auditoría futura.

**L-A4 — Derivar no es sinónimo de unificar** *(FASE-A)*
- **Qué pasó**: de 14 registros censados solo **6** se derivaron del canónico. Los otros 6 se mantuvieron
  literales y se **validan contra Capa 1**. Derivar `PAIN_TO_ASSET` habría hecho que `poor_performance`
  generara `optimization_guide` en vez de `performance_audit`; derivar `PAIN_TO_PRESENCE_ASSET` produce 13
  entradas frente a 6 y cambia `apply_site_verification`.
- **Por qué**: un registro que responde **otra pregunta** no puede derivarse sin cambiar esa respuesta.
  La presión por «unificar todo» confunde eliminar la duplicación con eliminar la distinción.
- **Qué lo previene**: el criterio **derivar vs validar** (DA9) + **contrafactual medido** que pruebe delta
  cero en contenido y orden antes de declarar la migración cerrada. Validar contra Capa 1 basta para
  impedir el próximo ID fantasma, que es el defecto real.
- **Pertinencia**: INCLUIR en QMind — insumo directo de FASE-C (los 2 builders) y FASE-F (oráculo único).

**L-A5 — Un test fosilizado puede estar codificando el invariante invertido** *(FASE-A)*
- **Qué pasó**: `test_all_service_catalog_services_have_lookup_entry` falló al unificar. No pedía un número
  desactualizado: exigía que **todo** servicio del catálogo tuviera entrada en el lookup de alignment —
  es decir, codificaba como requisito exactamente el drift que el plan corrige. Se renombró a
  `test_solo_servicios_alineables_tienen_lookup_entry` y se invirtió la aserción.
- **Por qué**: cuando una invariant se rompe durante años, los tests escritos en ese periodo la capturan
  como «lo correcto». Actualizarles el número los deja defendiendo el bug con más fuerza.
- **Qué lo previene**: ante un test fosilizado que falla tras una unificación, **leer qué invariant
  codifica antes de tocar su valor esperado**. Si la invariant es el defecto, se invierte y se renombra;
  si es legítima, se deriva su expectativa del canónico. 6 aserciones de `test_proposal_dynamic.py` se
  trataron así.
- **Pertinencia**: INCLUIR en QMind — complementa `conteos-tests-documentados-metodo-def_test` y aplica a
  FASE-C/D/F, que también desfossilizarán tests.

---

**L-{id} — {título}** *(plantilla — VERIFY la instancia)*
- **Qué pasó**:
- **Por qué**:
- **Qué lo previene**:
- **Pertinencia**: INCLUIR en {memoria/QMind} | EXCLUIR porque {razón}

*(VERIFY agrega ≥1 lección por fase con desviación o decisión no trivial. Mínimo esperado: orden A/B antes
que C, interacción C↔F, interacción C↔D, anti-reversión V5/BUG-6, degradación silenciosa como familia
común a V6/V7/P11/tier_c.)*

---

## 9. Write-back a QMind (pendiente de confirmación)

> Ciclo de capitalización v2.18.0 (memoria `ciclo-de-capitalizacion-de-lecciones-qmind-memory`).

| Lección | Notebook | Estado |
|---------|----------|--------|
| L-A1 grep de IDs fantasma también cuenta prosa | `iah-cli-lecciones` | ⬜ Propuesta — el usuario confirma la ingestión |
| L-A2 regex de censo anclado a la raíz, no al idioma | `iah-cli-lecciones` | ⬜ Propuesta — el usuario confirma la ingestión |
| L-A3 dos namespaces parecidos no son un drift | `iah-cli-lecciones` | ⬜ Propuesta — el usuario confirma la ingestión |
| L-A4 derivar no es sinónimo de unificar | `iah-cli-lecciones` | ⬜ Propuesta — el usuario confirma la ingestión |
| L-A5 test fosilizado puede codificar el invariante invertido | `iah-cli-lecciones` | ⬜ Propuesta — el usuario confirma la ingestión |
| *(las INCLUIR que agregue VERIFY)* | `iah-cli-lecciones` | ⬜ Propuesto — el usuario confirma la ingestión |
