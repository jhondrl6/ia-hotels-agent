# 06 — Checklist Maestro de Implementación

> **Estado maestro** del plan ESTABILIZACION-PRE-TRIBUNAL-2026-09-03.
> Cada sesión actualiza este archivo en su Post-Ejecución (template §5, punto 2).
> **Regla**: no marcar una fase ✅ si algún criterio de completitud falla.

**Versión objetivo**: 4.75.0 · **Versión actual del repo**: 4.74.1
**Sesiones totales**: 11 (9 implementación + VERIFY + RELEASE)
**Sesiones completadas**: 5 (FASE-A ✅, FASE-B ✅, FASE-C ✅, FASE-D ✅, FASE-E ✅ 2026-09-03)

---

## Progreso de fases

| # | Fase | Complejidad | Modo | Estado | Fecha | Iter. | Tests nuevos | ACs cerrados |
|---|------|-------------|------|--------|-------|-------|--------------|--------------|
| 1 | FASE-A — Fuente única de identidad | ALTA | DIRECTO | ✅ Completada | 2026-09-03 | 55/55 | 21 func (37 casos) | AC1, AC2, AC3 |
| 2 | FASE-B — Biyección **triple** mapa↔emisión↔narrativa (N-A1) | MEDIA-ALTA | DIRECTO | ✅ Completada | 2026-09-03 | **345 medidas**/40 ⚠️ | 29 func (46 casos) | AC4 |
| 3 | FASE-C — Punto 8 propuesta dinámica | **MÁXIMA** | DIRECTO | ✅ Completada | 2026-09-03 | **142 medidas**/60 ⚠️ | 14 func (17 casos) + 3 netos en archivos existentes | AC5, AC6 |
| 4 | FASE-D — Severidad 11+2 (H10) | MEDIA | MIXTO | ✅ Completada | 2026-09-03 | **114 medidas**/35 ⚠️ | 24 func (24 casos) | AC7, AC8 |
| 5 | FASE-E — A2 snapshot + A6 asset_path | MEDIA | DELEGADO | ✅ Completada | 2026-09-03 | **72 medidas**/30 ⚠️ | 10 func (10 casos) | AC9 |
| 6 | FASE-F — A4 + A1 + N11 | MEDIA-ALTA | DIRECTO | ⬜ Pendiente | — | —/45 | — | AC10, AC11, AC12 |
| 7 | FASE-G — Ceguera de gates | MEDIA-ALTA | DIRECTO | ⬜ Pendiente | — | —/50 | — | NR1, NR2, NR3, NR4 |
| 8 | FASE-H — Quirúrgicos | BAJA-MEDIA | DELEGADO | ⬜ Pendiente | — | —/35 | — | V6, V7, V8, V11, V12, V13 |
| 9 | FASE-I — E2E única Salento Real | BAJA | MIXTO | ⬜ Pendiente | — | —/25 | — | NR6 + deltas AC5/AC6/AC9/AC12 |
| 10 | FASE-VERIFY — Certificación | MEDIA | DIRECTO | ⬜ Pendiente | — | —/40 | — | AC1-AC12 + NR1-NR12 |
| 11 | FASE-RELEASE-4.75.0 | BAJA | DELEGABLE | ⬜ Pendiente | — | —/25 | — | Cierre documental |

Leyenda: ⬜ Pendiente · 🟡 En curso · ✅ Completada · 🔴 Bloqueada · ⏸️ Suspendida

**Columna `Iter.`** — unidad: ids de mensaje de asistente únicos del transcript de la sesión, contados con
`evidence/FASE-D/measure_iterations.py`. **Corte: hasta el commit de código de la fase**, que es el único que
hace comparables las cifras (el cierre documental añade 14 a B y 133 a D). Excepción: FASE-A (55) es
auto-reportada y **no reconstruible** con ese instrumento → `10-analisis` §5 S22.

⚠️ **Corrección 2026-09-03**: FASE-B publicó **151** en esta columna. Era una foto tomada a las 16:38
locales, **antes de terminar su cierre documental**, no el total de la fase. Al corte real (commit `e6d28b8`)
son **345** — presupuesto de ≤40 excedido **8.6×**, no 3.8×. Lo detectó la sesión paralela de FASE-D
(`evidence/FASE-D/faseD_iteraciones.txt`: «la cifra de B al cierre real de su fase es mayor que 151»); B lo
verificó y lo corrigió (`evidence/FASE-B/faseB_iteraciones.txt`). Consecuencia para el plan: con 4 de 11
fases cerradas el total medido es **≥656 sobre un presupuesto de ≤440** para el plan **completo** — y las 4
fases cerradas tenían un presupuesto conjunto de **≤190** (55+40+60+35), excedido **3.5×**. FASE-C aporta
142 sobre ≤60 (**2.4×**, `evidence/FASE-C/faseC_iteraciones.txt`). → VERIFY debe recalibrar los
presupuestos por fase o retirar la métrica.

---

## Criterios de aceptación — estado

### ACs de refactorización

| AC | Descripción corta | Fase dueña | Estado | Evidencia |
|----|-------------------|-----------|--------|-----------|
| AC1 | Registro canónico único; 0 IDs fantasma | A | ✅ (2026-09-03) | `modules/common/service_identity.py` (`SERVICE_IDENTITIES`, 8 entradas); **15 registros** resueltos: 1 canónico (Capa 2) + 1 Capa 1 + **6 derivados** + **4 validados contra Capa 1** + **3 fuera de alcance** (`evidence/FASE-A/censo-registros.md` §8.2); grep IDs fantasma → **0** en `modules/commercial_documents` + `modules/asset_generation`; `tests/common/test_service_identity_registry.py` 37/37 casos (21 funciones). **Nota**: las 3 claves en `opportunity_scorer.py` son del namespace `brecha_type`, no pain_id — no modificadas (decisión DA8). FASE-VERIFY certifica contra salida real |
| AC2 | Drift «8 vs 7» corregido en sus 3 copias + contract test | A | ✅ (2026-09-03) | Las 3 copias eliminadas físicamente: `proposal_asset_alignment.py:35-40` (derivado), `service_catalog.py` (derivado + mutación post-hoc borrada), `v4_proposal_generator.py:1332` (derivado). Contract test `test_narrativa_no_hardcodea_conteo_de_servicios` prohíbe la **forma numeral** en 7 módulos de narrativa (L-NC10: no compara contra un número) |
| AC3 | `ASSET_TO_PAIN_ID["monthly_report"]` resuelto a favor del canónico | A | ✅ (2026-09-03) | `ASSET_TO_PAIN_ID` derivado del canónico ⟹ `monthly_report → no_monthly_report`. La perla `no_faq_schema` ya no existe en ningún registro; `test_un_asset_no_se_atribuye_a_pains_distintos_entre_registros` la vuelve imposible |
| AC4 | Biyección **triple** mapa↔emisión↔narrativa fijada; 0 pains sin decisión (**11**, no 9 — N-A1) | B | ✅ (2026-09-03) | Candado `tests/commercial_documents/test_pain_map_bijection.py` **28 casos / 11 funciones** (guardián AST + sonda conductual). Delta medido (`evidence/FASE-B/faseB_bijeccion_audit.txt`): Capa 1 **27→26**, emisiones **18→20**, `narratives` literal **16→16** (complemento **derivado** de Capa 1, L-NC4), cobertura narrativa efectiva **26/26**, **DESCARTE REAL 2→0**. Las 11 decisiones: **3 implementados** con señal verificable (`missing_llmstxt`, `missing_alt_text`, `no_social_links`), **1 narrativa-only** (`low_ota_divergence`; su guard es V7/FASE-H), **1 retirado** (`no_ga4_enhanced`), **6 diferidos** con motivo+seguimiento (`PAINS_DIFERIDOS`). ⚠️ **La premisa de N-A1 resultó falsa**: los «2 que sí se emiten y sí se descartan hoy» NO se emitían — guardias insatisfacibles (S-B7). El candado fija la **relación**, no el conteo (L-NC10) |
| AC5 | Propuesta solo promete servicios con brecha; `no_breach = 0` | C | ✅ (2026-09-03) | Partición canónica **única** `classify_promised_services()` en `modules/asset_generation/proposal_asset_alignment.py`, consumida por los **dos** builders (`ProposalAssetMatrix.build` y `AssetAlignmentMatrix.build`) — cura A5 de raíz en vez de parchear el skip silencioso dos veces. Semántica: con ledger **resuelto**, un servicio sin brecha mapeada y sin presencia verificada **no se promete** (va a `not_promised`), en vez de emitirse como `NO_BREACH`. `site_presence_report` entra en la partición, así que un servicio comprometido por presencia nace `PRESENT_IN_PRODUCTION` en la matriz (antes nacía `NO_BREACH` y lo re-clasificaba el DTO). **Delta medido** sobre la corrida real de SalentoReal (`evidence/FASE-C/faseC_contrafactual.py`): `no_breach` **6→0**, `promised_services_total` **7→1**, `actionable_total` 1→1 ⟹ **`total == actionable` es identidad estructural, no una resta que se anula**. Invariante `1+0+0==1` ✔. `coverage_ratio` sigue en `1.000` pero ya no es algebraico; que **discrimine** se prueba en el caso negativo (`coverage=0.5`, `unresolved=1` con brecha de `hotel_schema` sin asset; corrida C de `test_alignment_result.py` da `3/4` con `no_breach=0`). **vacío ≠ ausente**: 3 sitios colapsaban `[]` con `None` (`publication_gates.py` extracción `or []`, derivación `if pain_ledger:`, `v4_proposal_generator.py:1201`) — los 3 corregidos; `None`→catálogo estático legacy, `[]`→0 comprometidos. Candado: `tests/asset_generation/test_fase_c_propuesta_dinamica.py` **14 funciones / 17 casos** + 3 netos en archivos existentes (`tests/asset_generation` + `tests/quality_gates`: **872→892 passed / 2 skipped**, 0 regresiones). ⚠️ **No** cierra la escotilla V9 (0 comprometidos → PASS trivial): `C1 DEFINE, G4 IMPLEMENTA` (FASE-G) → **S-C3** |
| AC6 | `is_coherent = false` estructural desaparece por el punto 8 | C | ✅ (2026-09-03) | ⚠️ **El dossier §9.2-B5 acertó la causa; lo que resultó falso fue el parafraseo que C hizo de él.** El dossier dice textualmente: *«Causa única: `_check_assets_are_justified` = **3/4 = 0.75** → `severity="error"` … 4 assets generados, 3 con pain en el ledger, 1 (`monthly_report`) always-on sin pain. ⟹ La misma falla estructural de B1 produce a la vez el `no_breach = 6/7` y el `is_coherent = false`. Punto 8 elimina las dos.»* Acertó el check, la fracción, el asset responsable y la causa común. Una versión previa de esta fila afirmaba que B5 «atribuía el fallo a los cerrojos de `promised_assets_exist`»: **esos cerrojos son otro hallazgo** (A3/P12 — por qué *cambiar el registro* no mueve coherence), siguen intactos, dan **1.0** antes y después, y **no** son la causa → **S-C3**. **Lo que el dossier no previó**, y es lo que C decidió además del punto 8: hacer dinámica la promesa de **servicios** no saca a `monthly_report` de la lista de **assets** que coherence cuenta — se genera incondicionalmente (D4-FIX, `promised_by=["always"]`) y `_check_assets_are_justified` recorre su argumento `assets: List[AssetSpec]` ⟹ con el punto 8 solo, el `3/4 = 0.75` **sobrevive**. Mecanismo medido: `_solutions_to_asset_specs` añade los `promised_by=["always"]` con `pain_ids=[]`, y `any(pid in problem_ids for pid in asset.pain_ids)` es **siempre** False ⟹ `0.75 < 0.8` ⟹ `severity="error"` ⟹ `errors` no vacío ⟹ `is_coherent=False` **en toda corrida, cualquier hotel**. Es el mismo defecto conceptual que AC5 en la **tercera superficie de promesa**. Fix en `modules/commercial_documents/coherence_validator.py:278-319`: excluir del denominador `ALWAYS_ACTIVE_COMPLEMENT_ASSETS` (proyección **derivada** del registro canónico `counts_in_alignment=False`, no lista a mano) — los complementos siguen **generándose**, sólo dejan de contarse como promesa por brecha. Dientes preservados: un asset sin `pain_id` que **no** sea complemento sigue restando (`test_asset_sin_pain_que_no_es_complemento_sigue_restando`: 0.5, `passed=False`). **Delta medido**: `assets_are_justified` 0.75/`error` → **1.0**/`info`, `overall_score` **0.88 → 0.9133**, `errors` `[1]` → `[]`, **`is_coherent` False → True**. **Umbral 0.8 sin tocar** y `_coherence_gate` sin tocar — ⚠️ el prompt de C lo citaba en `publication_gates.py:458` y hoy está en **`:549`** (el +91 de FASE-D; `458 + 91 = 549`, caso (5) de S15): se cierra por la vía del punto 8, no relajando el gate. **Cuarta** aplicación en el plan de *«revalidar citas de código no revalida premisas»* y **la primera en dirección inversa** (la premisa falsa era del plan, no de la fuente) → **S-C1** |
| AC7 | Severidad explícita 11 blocking + 2 advisory; `asset_confidence` bloquea | D | ✅ (2026-09-03) | Fuente única en `modules/quality_gates/publication_gates.py`: `BLOCKING_GATE_NAMES` (11) + `ADVISORY_GATE_NAMES` (`content_quality`, `proposal_asset_alignment`) + predicado `gate_blocks_publication()`, consumido por `check_publication_readiness`, `get_blocking_gates` e `is_ready_for_publication` (conectada, no eliminada). Fail-fast en `__init__`: las dos listas deben ser disjuntas y su unión = `self.gates`. **`asset_confidence` sigue blocking** (dossier §8.2: protege ~37 % del corpus histórico Tier C). Piso D2 (decisión del usuario): un advisory degrada a blocking bajo su corte estructural — `content_quality` con `details["blockers"]`, `proposal_asset_alignment` con `value < 0.8` (`PROPOSAL_ASSET_ALIGNMENT_FLOOR`); un gate **no ejecutado** siempre bloquea (`GATE_EXECUTION_FAILED_KEY`). Divulgación: `summary["advisory_issues"]` → `HumanChecklistGenerator.generate(report, advisory_issues=…)` cableado en `main.py`. Candado: `tests/quality_gates/test_gate_severity_lists.py` (8) + `TestFASEDGateSeverity` (12) + `TestAdvisoryDisclosureFASED` (4) = **24 tests**. **Medido, no asumido**: contrafactual sobre la corrida real de SalentoReal ⟹ **0 flips de `ready`** (`evidence/FASE-D/faseD_contrafactual.py`) — la fase cambia la **divulgación**, no el veredicto. ⚠️ `delivery_quality_report.py` **no se tocó** (régimen delivery, dueño E→F): `content_quality` no existe en su reporte. **S24**: re-verificar el demote de los 2 advisories cuando C cierre AC5 |
| AC8 | Docstrings + `AGENTS.md` corregidos **en el mismo commit** que AC7 | D | ✅ (2026-09-03) | Mismo commit `76e0257`: docstring de módulo (`13 publication gates (11 blocking + 2 advisory)`), docstring de clase (`11 blocking gates and 2 advisory gates`), `AGENTS.md` fila `quality_gates/` y bloque «FASE 4.5» reagrupado por severidad. `grep -c "10 blocking\|3 advisory"` sobre `publication_gates.py` + `AGENTS.md` → **0**. Hallazgo colateral: el bloque FASE 4.5 de `AGENTS.md` listaba **12 gates, no 13** — faltaba `doc_audit_consistency`; corregido. Fijado por test (`test_docstrings_no_prometen_el_regimen_antiguo`, `tests/quality_gates/test_gate_severity_lists.py:109`), no por revisión manual. `validate_agents_md.py` 6 PASS / 0 FAIL con `missing_roadmap: []` |
| AC9 | `site_presence_snapshot` persistido; `asset_path` no nulo | E | ⬜ | — |
| AC10 | Un oráculo de presencia decide **y** narra | F | ⬜ | — |
| AC11 | `skipped ≠ passed` en G9 | F | ⬜ | — |
| AC12 | El gate de coherencia respeta `is_coherent` (o lo elimina con decisión) | F | ⬜ | — |

### ACs de no-regresión

| AC-NR | Descripción corta | Fase dueña | Estado | Evidencia |
|-------|-------------------|-----------|--------|-----------|
| NR1 | `doc_audit_consistency` cableado + acepta `gbp.reviews` int | G | ⬜ | — |
| NR2 | `_identify_critical_issues` cubre PageSpeed ERROR + banda GEO critical | G | ⬜ | — |
| NR3 | Escotilla V5 cerrada **sin revertir** BUG-6/N2 | G | ⬜ | — |
| NR4 | Escotilla V9 cerrada (ledger vacío ≠ PASS) | G | ⬜ | — |
| NR5 | Baseline 848 passed / 2 skipped preservado | todas | 🟡 4/11 | FASE-A: `tests/quality_gates` + `tests/asset_generation` → **848 passed / 2 skipped / 11 warnings**, igual al pre-cambio. ⚠️ No «byte-idéntico»: `diff evidence/FASE-A/faseA_baseline_{pre,post}.txt` da **1 línea** — la duración (`7.05s` → `6.02s`). Conteos y warnings idénticos. **FASE-B**: mismos dos directorios → **848 passed / 2 skipped**, conteos idénticos post-B2 (medido antes del commit). **FASE-D**: → **872 passed / 2 skipped** = 848 **+ 24 tests propios de D**, 0 regresiones (`evidence/FASE-D/faseD_baseline_{pre,post}.txt`). **FASE-C**: → **892 passed / 2 skipped** = 872 **+ 20** (17 de `test_fase_c_propuesta_dinamica.py` + 3 netos al actualizar tests existentes), 0 regresiones (`evidence/FASE-C/faseC_{antes,despues}.txt`, `suite_final.txt`). ⚠️ **NR5 está mal formulado**: fija el número **848** como invariante, pero D **y C** —y cualquier fase que añada tests en `tests/quality_gates` o `tests/asset_generation`— lo rompen **por diseño y en verde**. La intención real es «cero regresiones», no «cero delta». Debe reescribirse como regla de delta (`post − pre == tests nuevos de la fase`, con el pre medido en el mismo árbol) → **S26**. ⚠️ Árbol ancho (`tests/` salvo `tests/commercial_documents`): **14 failed / 3348 passed / 32 skipped / 9 errors**, verificados **pre-existentes en HEAD** con `git stash` de `modules/` + `tests/` — no son de C |
| NR6 | Corrida FASE-I: coherence ≥ 0.80 + perfil de gates esperado | I | ⬜ | — |

> **Dos familias de NR** (auditoría del plan 2026-09-03): NR1-NR6 son «de hallazgo» (la tabla anterior);
> **NR7-NR12 son «de producto»** (tests, coherence, 13 gates, ZIP, `asset_confidence` blocking,
> anomalías — definidas en `10-analisis-post-implementacion.md` §3). VERIFY certifica ambas; FASE-I
> aporta la evidencia de las dos.

---

## Hallazgos del dossier — trazabilidad

Cada fila debe quedar en estado final explícito al cierre de VERIFY (tarea V3).

### Eje 1 — Caídas silenciosas (dossier §4)

| # | Caída | Fase que la aborda | Estado |
|---|-------|--------------------|--------|
| 1 | PageSpeed `status=ERROR` sin pain ni justificación | H3 (V11 + capa de pain (a)-(d)) | ⬜ |
| 2 | GEO crítico 29/100 sin pain | G2 (`_identify_critical_issues`) | ⬜ |
| 3 | `llm_report` mention_rate 0.0 / `aeo_snippets` 0/5 sin pain_id | ~~B~~ → **sin fase dueña** | 🔴 **No cerrable por B** — medido contra Capa 1 post-B (26 pain_ids): **no existe ningún pain** para `mention_rate` ni para `aeo_snippets`. B fija la biyección sobre el universo *existente*; inventar 2 pain_id nuevos es extender Capa 1, fuera del alcance de AC4. **S-B13**: requiere decisión previa (¿pain nuevo o umbral dentro de `low_ia_readiness`/`low_citability`?) → asignar en VERIFY o abrir fase |
| 4 | `missing_llmstxt` declarado, asset generado, 0 ramas lo emiten | B2 (caso confirmado) | ✅ 2026-09-03 — rama emisora añadida en `detect_pains` (`pain_solution_mapper.py`): dispara solo si `ia_readiness` existe **y** su dict `components` tiene la clave `llms_txt` **y** vale exactamente `0`. 5 tests (`TestMissingLlmsTxt`), 3 negativos |
| 5 | Schema warnings invisibles en doc | ~~B~~ → **sin fase dueña** | 🔴 **No cerrable por B** — los 4 pains de schema en Capa 1 (`no_hotel_schema`, `no_faq_schema`, `no_org_schema`, `no_schema_reviews`) son de **ausencia**, no de *warnings*. Un schema presente-con-warnings no tiene pain_id que narrar. **S-B14**: misma naturaleza que #3 |
| 6 | Fotos GBP 10/40 solo en tabla rota | H3 (V11 tabla sin header) | ⬜ |
| 7 | metadata `title=""`/`description=""` (narrativa «por defecto» equivocada) | H4 (V13 gemelos) | ⬜ |
| 8 | `low_ota_divergence` no puede disparar con valor numérico | H1 (V7 guard `__iter__`) | ⬜ (H1 sigue dueño del guard) — **precondición B→H SATISFECHA**: el pain ya tiene narrativa (derivada de Capa 1 + peso `0.20` declarado en las 4 regiones de `regional_benchmarks.yaml`), así que cuando V7 arregle el guard la brecha aparecerá en el documento en vez de desvanecerse. **FASE-H debe leer `evidence/FASE-B/decision-pains-muertos.md` antes de tocar el guard** |

### Eje 2 — Candados rotos (dossier §3)

| Candado | Defecto | Fase | Estado |
|---------|---------|------|--------|
| `coverage_no_silent_drop` | Tautología extremo a extremo (ledger y doc de la misma llamada) | A+B+C (cura) · G3/G4 (escotillas) | 🟡 A ✅ (identidad unificada aguas arriba) · **B ✅ 2026-09-03** (cerró la **caída silenciosa aguas arriba** que el gate no podía ver: **2 → 0** pains emitidos-y-descartados, `_pain_to_brecha` ya no devuelve `None` para ningún pain de Capa 1; sonda conductual en `evidence/FASE-B/faseB_bijeccion_audit.txt`) · **C ✅ 2026-09-03 (en su superficie)** — la promesa dinámica elimina el **auto-cancelado del denominador**: `no_breach` 6→0 ⟹ `total == actionable` por construcción, no por una resta que se anula; `coverage_ratio = 1.000` ya no es algebraico y su capacidad de discriminar queda fijada en el caso negativo (`coverage = 0.5` con brecha sin asset). ⚠️ **La tautología propia del gate SIGUE ABIERTA** — ledger y doc salen de la misma llamada; C no tocó ese camino → **G3/G4** |
| `doc_audit_consistency` | Llegó sin datos → PASSED con `value=null` | G1 | ⬜ |
| `critical_recall` | 1.0 vacuo | G2 | ⬜ |
| `hard_contradictions` | Fuera de alcance del motor | — (documentado como límite) | ⬜ |

### Eje 3 — Agujeros vivos A1-A6 (dossier §9.1)

| # | Agujero | Fase | Estado |
|---|---------|------|--------|
| A1 | G9 se salta **en verde** | F2 | ⬜ |
| A2 | Oráculo de presencia no se persiste en absoluto | E1 | ⬜ |
| A3 | `promised_assets_exist` pre-gen only (peso 2.0/7.5) | C4 (no apoyarse) + documentar P12 | ✅ 2026-09-03 — **ninguna de las dos ACs de C se apoya en este check** (medido: pasa en `score=1.0` antes **y** después). Límite documentado en `evidence/FASE-C/delta-medido.md` §5: `coherence_validator.py:670` acota el cross-check con `if not generated_assets:` (comentario H6 FIX) ⟹ con assets reales el bucle sobre `PROPOSAL_SERVICE_TO_ASSET` **no se ejecuta**, y `:689-700` hardcodea `score=1.0` en la rama de éxito ⟹ post-gen P6.3 no tiene verificación de score. Efecto colateral hallado: su mensaje sigue citando *«7 servicios verificados»*, el catálogo estático que C ya no emite → **S-C3** |
| A4 | Doble oráculo de presencia | F1 | ⬜ |
| A5 | Skip silencioso en los 2 builders de la matriz | C3 (esquivar la trampa) | ✅ 2026-09-03 — **no esquivada: curada de raíz.** Los dos builders tenían el mismo camino `# Unknown service — skip silently`; en vez de duplicar la lógica nueva en ambos, se extrajo **una sola** función de partición `classify_promised_services()` que los dos consumen ⟹ el drift A5 vuelve estructuralmente imposible. El skip además dejó de ser silencioso: los servicios fuera del registro canónico van a `unknown_services` (publicado en `to_dict()`) + `logger.warning`. Candado: `TestAmbosBuildersIdenticos` compara los pares `(servicio, status)` **ordenados** de ambos builders en 4 variantes + `not_promised` idéntico, y fija el aviso por `caplog` |
| A6 | `asset_path: null` | E2 | ⬜ |

### Eje 4 — Hallazgos nuevos V1-V16 (dossier §12.3)

| V# | Hallazgo | Nivel | Fase | Estado |
|----|----------|-------|------|--------|
| V1 | 9 pains muertos, no 1 | 1 | B | ✅ 2026-09-03 — el censo real fue **11** pains sin decisión, no 9 (los 9 del dossier + `no_ga4_enhanced` + `low_ota_divergence`, que N-A1 daba por vivos y están muertos: **S-B7**). Todos con decisión explícita y motivada en `evidence/FASE-B/decision-pains-muertos.md` §5: **3 IMPLEMENTAR** (`missing_llmstxt`, `missing_alt_text`, `no_social_links` — señal real + guard contra falsos positivos) · **1 narrativa-only** (`low_ota_divergence`, el guard `__iter__` es de H1/V7) · **1 RETIRAR** (`no_ga4_enhanced`: `is_enhanced` no existe en el repo) · **6 DIFERIR** con seguimiento S-B1…S-B6 y registro `PAINS_DIFERIDOS` en el candado. Capa 1 pasa de 27 → **26** |
| V2 | 6 IDs fantasma en `ELEMENTO_KB_TO_PAIN_ID` | 1 | A | ✅ 2026-09-03 — los 6 pain_id y el asset fantasma sustituidos por `None`/asset real en `v4_diagnostic_generator.py:126-166`; grep de AC → **0**; comportamiento preservado (consumidores verificados: ruta muerta `generate_for_faltantes`, `ELEMENTOS_MONETIZABLES` sin consumidores, `:3083/:3086` solo iteran `.keys()`) |
| V3 | ≥9 registros, no 6 (+ perla `monthly_report → no_faq_schema`) | 1 | A | ✅ 2026-09-03 — censo real: **14** registros (no ≥9). Dos capas: Capa 1 `PAIN_SOLUTION_MAP` (27, intacto) + Capa 2 `SERVICE_IDENTITIES` (8). **6 derivados** del canónico, **6 validados** contra Capa 1 con razón registrada, 2 fuera de alcance. Perla eliminada (ver AC3) |
| V4 | Atribución de brechas excluye por diseño el pain real | 1 | C | ⬜ **Sigue abierta — y FASE-C la hizo medible.** C no tocó `service_brecha_candidates` (hoy derivado de `SERVICE_IDENTITIES[...].brecha_candidates`, `v4_proposal_generator.py:1287-1291`); `llms_txt` aún declara solo `("missing_llmstxt",)`, excluyendo `ai_crawler_blocked`. Divergencia ahora visible en la corrida real: la **matriz** clasifica `LINKED` atribuyendo vía **Capa 1** (`llms_txt` ← `ai_crawler_blocked`, `evidence/FASE-C/faseC_despues.txt`), mientras la **columna «Problema que resuelve»** del documento atribuye vía **Capa 2** y no puede mostrar esa brecha. Dos fuentes de atribución para la misma fila → **S-C5** |
| V5 | `ASSET_GENERATED` = segunda escotilla (⚠️ anti-reversión BUG-6) | 2-3 | G3 | ⬜ |
| V6 | `except Exception` silencioso | 3 | H2 | ⬜ |
| V7 | Guard `__iter__` triple defecto | 3 | H1 | ⬜ |
| V8 | Dedup `low_organic_visibility` | 3 | H3 | ⬜ |
| V9 | Ledger vacío PASS vs BLOCKED | 2-3 | G4 | ⬜ **Sigue abierta por decisión.** FASE-C separó las dos semánticas que V9 confundía (`None` = sin fuente → catálogo estático legacy; `[]` = resuelto con 0 brechas → 0 comprometidos, los 7 en `not_promised`), así que el PASS trivial ya no se dispara **por confusión entre vacío y ausente**. Pero el PASS trivial en sí (0 comprometidos → `coverage` indeterminado/1.0) **no se cerró**: el contrato de C dice `C1 DEFINE, G4 IMPLEMENTA` → G4 |
| V10 | (ver dossier §12.3) | — | según nivel | ⬜ |
| V11 | Residuos D6 | 3 | H3 | ⬜ |
| V12 | Placeholder `.env` inválido (decisión **OPS**) | 3 | H4 (documentar) | ⬜ |
| V13 | Dos `MetadataValidator` gemelos | 3 | H4 | ⬜ |
| V14 | Drift «8 vs 7» tercera copia | 1 | A | ✅ 2026-09-03 — las 3 copias eliminadas por derivación (no comparadas). Un contract test prohíbe la forma numeral `\b\d+\s+servic` en los 7 módulos de narrativa. **Detalle del censo**: un primer regex `\b\d+\s+servicio` solo halló 2 de las 3 copias porque no casaba con el inglés «8 services» — la forma prohibida se ancló a la raíz `servic` |
| V15 | Mecanismo 6→3 de `no_breach` resuelto | 2 | F1 (vía A4) | ⬜ **Premisa modificada por C**: el `6→3` ya no es observable — con ledger resuelto `no_breach` es **0 por construcción** (los servicios sin brecha ni presencia no se emiten). El **doble oráculo A4 sigue vivo** y ahora importa más: la partición canónica de C consume `site_presence_report` **directamente** (`_presence_exists`), así que F1 debe reconciliar ese consumo con el oráculo único que instale, no solo con el DTO. La re-clasificación `NO_BREACH → PRESENT_IN_PRODUCTION` que hacía `AlignmentResult` quedó **aguas arriba** (el servicio nace `PRESENT_IN_PRODUCTION` en la matriz) → F1 debe decidir si el cross-reference del DTO se retira o se conserva para artefactos pre-C |
| V16 | `is_coherent: false` en `asset_generation_report.json` | 2 | F3 (vía N11) | ⬜ **Causa estructural eliminada por C** (era `assets_are_justified = 0.75` por el complemento siempre-activo, no `promised_assets_exist` como decía B5): en el corpus medido `is_coherent` pasa **False → True**. Pero **P9/N11 sigue abierto**: el gate de coherencia continúa sin leer `is_coherent`, así que un `false` futuro —por otra causa— seguiría sin bloquear. F3 conserva su alcance |

### Eje 5 — Deudas del ROADMAP v4.2 §13

| Deuda | Descripción | Fase | Estado |
|-------|-------------|------|--------|
| **P9** | El gate ignora `is_coherent` (la más grave abierta) | F3 | ⬜ |
| **P10** | ≥9 registros de identidad (extendido por A5) | A | ✅ 2026-09-03 — fuente única en `modules/common/service_identity.py`; censo real **14** registros: 6 derivados, 6 validados contra Capa 1 (razón registrada en cada uno), 2 fuera de alcance (`gap_analyzer` legacy, `asset_semantics_validator.INVALID_MAPPINGS`). **La extensión A5 (skip silencioso de los 2 builders) quedó CERRADA por FASE-C el 2026-09-03**: una sola función de partición `classify_promised_services()` consumida por ambos builders + skip visible en `unknown_services` (ver A5) |
| **P11** | `precision_tier` degrada a `"C"` bajo `except` desnudo | H2 (misma familia) | ⬜ |
| **P12** | `promised_assets_exist` pre-gen only | C4 (documentar alcance) | 🟡 **Alcance de C cumplido 2026-09-03, deuda de fondo ABIERTA.** Documentado con evidencia medida en `evidence/FASE-C/delta-medido.md` §5 y ninguna AC de C se apoya en él. La deuda persiste: sigue siendo pre-gen only (`if not generated_assets:` acota el cross-check) con `score=1.0` hardcoded en la rama de éxito, y C añadió un síntoma nuevo — su mensaje cita *«7 servicios verificados»* cuando la matriz dinámica ya no emite 7. Dueño de la corrección: **F/G** → **S-C3** |
| **H7** | Nombres timestamped sin índice + oráculo no persistido | E1 | ⬜ |
| **H8** | `publication_state.py` huérfano | F3 (decisión conectar/eliminar) | ⬜ |
| **H9** | Tres rutas de bloqueo + kill switch + G9 en verde | F2 | ⬜ |
| **H10** | Docstrings 10+3 vs código 13 | D3 (+D1/D2 conductual) | ✅ 2026-09-03 — **cuatro regímenes contradictorios** hallados al medir (no dos): docstrings `10+3`, código blocking-con-13, `AGENTS.md` repitiendo el docstring y `delivery_quality_report.py::BLOCKING_GATE_NAMES`. D cerró los **tres del régimen de publicación** en una sola fuente (`BLOCKING_GATE_NAMES`/`ADVISORY_GATE_NAMES`/`gate_blocks_publication()`) y dejó el **cuarto intacto a propósito**: es el régimen delivery/ZIP, dueño E→F, no el de publicación. El candado tiene un test anti-cuarto-régimen que escanea asignaciones a nivel de módulo en `modules/quality_gates/*.py` y exonera explícitamente esos dos archivos. Fix **completo** (mitad documental D3 montada en el mismo commit que la conductual, como exigía la decisión T0.1) |

---

## Checklist de cierre de cada sesión (obligatorio)

Cada fase, al terminar, debe haber hecho **todo** lo siguiente (template §5 + §6):

- [ ] Tests nuevos pasan (lotes pequeños, salida a archivo `> temp/x.txt 2>&1`)
- [ ] Baseline preservado: 848 passed / 2 skipped en `tests/quality_gates` + `tests/asset_generation`
- [ ] `python scripts/run_all_validations.py --quick` → 7/7
- [ ] `python scripts/validate_agents_md.py` → 6 PASS / 0 FAIL
- [ ] `log_phase_completion.py --fase FASE-X --desc "..." --check-manual-docs` **SIN `--release`**
- [ ] `dependencias-fases.md` actualizado (fase ✅ + fecha + notas)
- [ ] `README.md` del plan actualizado (tabla de progreso)
- [ ] **Este archivo** actualizado (fila de fase + ACs + trazabilidad de hallazgos)
- [ ] `09-documentacion-post-proyecto.md` actualizado (secciones A, B, D, E)
- [ ] `10-analisis-post-implementacion.md` actualizado (ejecución, lecciones, métricas, seguimientos, decisiones)
- [ ] `evidence/FASE-X/` poblado si aplica
- [ ] Commit con mensaje que referencia la fase

**NO esperar a la siguiente sesión para documentar** (anti-deuda §2.5 del executor).

---

## Riesgos abiertos

| Riesgo | Probabilidad | Impacto | Mitigación | Estado |
|--------|--------------|---------|------------|--------|
| FASE-C agota R2 (60 iteraciones) | Media | Alto | Punto de partición C1/C2 predefinido en `01-plan-maestro.md` §1 | 🔴 **SE MATERIALIZÓ** — **142 medidas** al corte del commit de código `c1bf5e2` sobre ≤60 (**2.4×**, `evidence/FASE-C/faseC_iteraciones.txt`). **El punto de partición NO se usó, con motivo**: C2 y C3 resultaron ser **una sola cadena causal** — el mismo concepto de «promesa» vivido en tres superficies (tabla, matriz+gate, lista de assets a coherencia). La partición prescrita `C1' = (C1+C2)` habría dejado precisamente el **estado intermedio prohibido** por el prompt de la fase (propuesta dinámica + matriz estática ⟹ artefactos que se contradicen entre sí). Se ejecutó la fase completa en una sesión y se registra el exceso en vez de partir en un punto que no era una costura real → `10-analisis` §6 **DA-C4** |
| A5 (skip silencioso) produce Δ = 0 en C y parece que no hizo nada | Media | Alto | C4 mide el delta explícitamente contra artefactos reales | ✅ **No se materializó** — C4 midió contra el corpus real de SalentoReal (`evidence/FASE-C/faseC_contrafactual.py` sobre `output/FASE-D_salentoreal_post_guard/`): `no_breach` **6→0**, `promised_services_total` **7→1**, `assets_are_justified` **0.75/error → 1.0/info**, `is_coherent` **False → True**. La trampa A5 se desactivó de otra manera: en vez de esquivarla, se extrajo **una sola** función de partición compartida por los dos builders, así que no hay segundo camino donde el skip pueda esconderse |
| G3 re-introduce BUG-6 al cerrar V5 | Baja | Alto | Test anti-reversión obligatorio en G3 | ⬜ |
| F3 voltea veredictos indebidamente en el corpus histórico | Media | Medio | F4 mide impacto sobre las 27 corridas antes de cerrar | ⬜ |
| Run FASE-I contaminado por infraestructura (gemini 403, PageSpeed key) | Media | Medio | I1 pre-flight verifica `.env`; clasificar como anomalía preexistente | ⬜ |
| D3 (docs) se commitea separado de D1 (código) | Baja | Alto | Checklist de D exige mismo commit; VERIFY lo audita | ✅ **No se materializó** — `76e0257` contiene `publication_gates.py` + `AGENTS.md` (verificado con `git show --stat`); el candado `test_docstrings_no_prometen_el_regimen_antiguo` lo fija en verde |
| 🟡 **Dos sesiones ejecutan dos fases de este plan sobre el mismo working tree** (sin worktree) | **Se materializó** | Alto | Cada sesión hace `git status` antes de stagear y **enumera rutas explícitas** (nunca `git add -A` / `git stash`); los documentos de plan compartidos (`README`, `06-checklist`, `09`, `dependencias-fases`, `10-analisis`) se editan aditivamente y pueden sobrescribirse entre sesiones | ⚠️ **Abierto — riesgo estructural del plan, no de una fase.** OCURRIÓ 2026-09-03: FASE-B y FASE-D en sesiones simultáneas. Consecuencias medidas: (1) la sesión de D afirmó en el README que «B sigue pendiente» cuando B estaba completa en paralelo; (2) cuatro documentos de plan quedaron con diff **mezclado** de ambas fases ⟹ imposible commitear la documentación de una sin arrastrar la de la otra; (3) el baseline de D se midió sobre el árbol **combinado** (872 = 848 + 24 propios), no sobre el árbol de su propia fase. **R1 del executor («una fase por sesión») no dice nada sobre «una sesión por repo»** → **S21** (+ **S-B15**); una fase por **worktree** sería la corrección de fondo |
