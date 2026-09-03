# 09 — Documentación Post-Proyecto

> **Plan**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03
> **Estado**: 🟡 EN CURSO — archivo creado **desde la concepción** del plan (executor §4). Se actualiza
> **incrementalmente al cierre de cada fase** (Post-Ejecución punto 3), NO al final.
> **Consumidor**: FASE-RELEASE lo lee para generar CHANGELOG y GUIA_TECNICA. Si este archivo está vacío,
> RELEASE produce documentación vacía.
> **Regla anti-reproceso**: cada fase vuela su propia fila; RELEASE solo consolida.

---

## Sección A — Módulos nuevos

> Módulos/archivos **creados** por el plan que no existían antes. Fuente: Post-Ejecución de cada fase.

| Fase | Módulo / archivo nuevo | Propósito | Estado |
|------|------------------------|-----------|--------|
| A | `modules/common/service_identity.py` *(el plan predecía `modules/asset_generation/service_asset_registry.py` — nombre y ubicación corregidos al cierre)* | Fuente canónica única de identidad servicio↔asset↔pain (Capa 2). `modules/common/` no importa nada del proyecto ⟹ lo consumen `asset_generation`, `commercial_documents` y `financial_engine` sin ciclo | ✅ 2026-09-03 |
| A | `tests/common/test_service_identity_registry.py` *(el plan predecía `tests/asset_generation/test_canonical_registry_contract.py`)* | **21 funciones test / 37 casos parametrizados**, en 6 secciones: AC1 integridad del canónico, AC1/V2 cero IDs fantasma, V3 biyección asset↔pain, guardián AST «derivar no copiar», AC2/V14 narrativa↔fuente, validación de registros no derivados contra Capa 1 | ✅ 2026-09-03 |
| A | `evidence/FASE-A/` (`censo-registros.md`, `tdd-contract-tests-ROJO.txt`, `tdd-contract-tests-post-canonico.txt`) | Censo de los 14 registros + la curva TDD completa (27 fallados → 37 pasados) | ✅ 2026-09-03 |
| B | `tests/commercial_documents/test_pain_map_bijection.py` | Guardián AST **tridireccional** de la biyección mapa↔emisión↔narrativa (patrón SR-A, no regex). **11 funciones / 28 casos**. Fija: capa narrativa **total** sobre Capa 1 (sonda conductual que llama a `_pain_to_brecha`), emisiones ⊆ Capa 1, y la partición **del lado de la emisión** `Capa 1 = emitidos ⊎ PAINS_DIFERIDOS` (6 diferidos con motivo + seguimiento). Incluye el guardián L-NC4 («la narrativa derivada sale de Capa 1, no de una tabla paralela») y el de S14 («el peso de impacto no vive de un default mudo») | ✅ 2026-09-03 |
| B | `tests/commercial_documents/test_detect_pains_emisiones_faseB.py` *(no previsto en el plan)* | **18 tests** (9 negativos) sobre las 3 ramas emisoras nuevas + el retiro de `no_ga4_enhanced`. Los negativos fijan «vacío vs ausente»: clave `llms_txt` presente y == 0, `images_without_alt > 0`, y `confidence == "high"` para excluir la ruta de excepción del detector | ✅ 2026-09-03 |
| B | `evidence/FASE-B/` — **13 archivos nuevos**: `decision-pains-muertos.md`, `faseB_narratives_audit.py` **re-ejecutable**, `faseB_bijeccion_audit.txt`, `tdd-candado-ROJO.txt`, `faseB_iteraciones.txt` (re-medición de las iteraciones de B con el instrumento de D: **345** al corte del commit `e6d28b8`, corrige los 151 publicados) + 8 logs de tests/validaciones | B1 (las 11 decisiones motivadas) + la medición conductual del delta. El script importa los helpers del candado ⟹ evidencia y candado miden **igual**. ⚠️ **El directorio ya existía** con 7 archivos de la FASE-B de **otro plan** (commit `d2a9700`, «tabla de servicios dinámica desde opportunity_scores»): `fase_b_*.txt` y `verify_breach_consistency_static*`. Los de este plan usan el prefijo `faseB_*` (camelCase). Colisión de nombres por fase-letra → VERIFY debe distinguirlos | ✅ 2026-09-03 |
| E | `modules/.../site_presence_writer.py` *(nombre a confirmar en E1)* | Persiste `site_presence_snapshot` en disco (mitad pendiente de DT4-R2) | ⬜ Pendiente |
| D | `tests/quality_gates/test_gate_severity_lists.py` *(el plan predecía `test_gate_severity.py` — nombre corregido al cierre)* | **8 funciones** que fijan la estructura 11 blocking + 2 advisory: `asset_confidence` no es advisory, los advisory son **exactamente** 2, las listas suman 13 y son disjuntas, el registro `self.gates` coincide con la unión, **guardián AST** contra el `not r.passed` plano en `check_publication_readiness`, contra una segunda copia del criterio y contra un **cuarto régimen** de severidad en `modules/quality_gates/*.py` (exonera `delivery_quality_report.py` y `commercial_gate.py`), y que los docstrings no prometan el régimen antiguo | ✅ 2026-09-03 |
| D | `evidence/FASE-D/faseD_contrafactual.py` (+ `.txt`) | **Re-ejecutable**: reconstruye los 13 veredictos de la corrida real de SalentoReal y aplica el criterio viejo vs el nuevo ⟹ **0 flips de `ready`**, 2 advisories antes silenciosos ahora divulgados. Es la prueba de que D **no relajó** ningún veredicto | ✅ 2026-09-03 |
| D | `evidence/FASE-D/measure_iterations.py` | Cierra en parte la brecha que señaló B («no hay contador instrumentado de iteraciones, cada fase se auto-reporta»). Cuenta ids de mensaje de asistente únicos + `tool_use` sobre un transcript `.jsonl`, con corte opcional por timestamp ⟹ la cifra de iteraciones de una fase es **auditable y comparable**. Misma unidad con la que B y D publicaron sus números | ✅ 2026-09-03 |
| D | `evidence/FASE-D/` — 8 archivos de salida (`faseD_baseline_{pre,post}.txt`, `faseD_severity_lists.txt`, `faseD_publication_gates.txt`, `faseD_validations.txt`, `validate_agents_md.txt`, `faseD_contrafactual.txt`) | Baseline 848 → **872** con delta explicado (24 tests propios), `-v` del candado de severidad, 69+1 del archivo de gates, `run_all_validations.py` 7/7 y `validate_agents_md.py` 6 PASS / 0 FAIL. ⚠️ **Un artefacto llegó fósil al commit de código**: `faseD_severity_lists.txt` se capturó a mitad de fase con **18** tests y el archivo final tiene **8** — el log **no reproducía** el candado que decía probar. Regenerado en el cierre documental. Lección: capturar los logs **después** de estabilizar los tests, no antes. ⚠️ El directorio **ya existía** con 6 archivos `fase_d_*` (snake_case) de la FASE-D de **otro plan** (commit `04fe193`) — misma colisión por fase-letra que registró B; VERIFY debe distinguirlos | ✅ 2026-09-03 |
| … | *(agregar filas si una fase crea archivos no previstos)* | | |

**Nota**: los nombres exactos los fija cada fase en su implementación; esta tabla se corrige al cierre de
fase con el nombre real. Lo importante para RELEASE es la **lista consolidada de archivos nuevos**.

---

## Sección B — Funcionalidades nuevas

> Comportamiento **nuevo o modificado** que el sistema gana con el plan.

| Fase | Funcionalidad | Hallazgo del dossier que cura | Estado |
|------|---------------|-------------------------------|--------|
| A | Fuente única de identidad servicio↔asset↔pain en `modules/common/service_identity.py`, en **dos capas** (Capa 1 = `PAIN_SOLUTION_MAP` 27 pains como universo de pain_id, intacto; Capa 2 = `SERVICE_IDENTITIES` 8 entradas). De los **14** registros censados (el dossier decía ≥9): **6 derivados** del canónico, **6 validados** contra Capa 1 con razón registrada, 2 fuera de alcance. Drift «8 vs 7» disuelto **eliminando sus 3 copias**, no comparándolas. Perla `monthly_report → no_faq_schema` eliminada. 6 IDs fantasma + 1 asset fantasma corregidos sin cambio de comportamiento (contrafactual medido) | V2, V3, V14 (§12.3); causa raíz §12.5 (≥9 registros); deuda P10 | ✅ 2026-09-03 |
| B | Biyección **triple** mapa↔emisión↔narrativa. Lo que gana el sistema: (1) **`_pain_to_brecha` ya no descarta en silencio** — el `return None` se reemplazó por una **derivación de Capa 1**, así que la capa narrativa es **total (26/26)** y no se escribió ni una entrada a mano (L-NC4: el dict literal sigue en 16); (2) **3 pains ganan señal verificable** (`missing_llmstxt` vía sonda HTTP de `ia_readiness`, `missing_alt_text` y `no_social_links` vía `seo_elements`), cada uno con guard «vacío vs ausente» para no emitir falsos positivos cuando el detector falló; (3) **`no_ga4_enhanced` se retira** de Capa 1 y de `asset_catalog` (guardia insatisfacible: `is_enhanced` no existe en el repo) ⟹ Capa 1 **27 → 26**; (4) **6 pains se difieren con decisión registrada** (`PAINS_DIFERIDOS` en el candado, con motivo y seguimiento S-B1…S-B6). Delta neto: emisiones 18 → 20, **DESCARTE REAL 2 → 0** | V1 (9 pains muertos) + N-A1 (2 que se emitían y se descartaban) = **11**; §3 candado de biyección. ⚠️ La premisa de N-A1 resultó **falsa** (S-B7) | ✅ 2026-09-03 |
| C | **Punto 8**: propuesta dinámica — solo promete servicios con brecha detectada (`no_breach = 0` por construcción) | §9.2 B1-B5; tautología de coverage; `is_coherent = false` estructural | ⬜ Pendiente |
| D | **Severidad explícita de gates**: el régimen de publicación pasa de «los 13 bloquean» a **11 blocking + 2 advisory** decidido por **un único predicado** `gate_blocks_publication()`. Lo que gana el sistema: (1) **una fuente** (`BLOCKING_GATE_NAMES`/`ADVISORY_GATE_NAMES`) con **fail-fast en `__init__`** — añadir un gate sin declarar su severidad ahora revienta al instantiar, no en producción; (2) **piso por naturaleza del fallo**: un advisory degrada a blocking bajo su corte estructural (`content_quality` con `details["blockers"]`; `proposal_asset_alignment` con `value < PROPOSAL_ASSET_ALIGNMENT_FLOOR = 0.8`) y **un gate que no se ejecutó siempre bloquea** (`GATE_EXECUTION_FAILED_KEY`), así que «advisory» no puede volverse «inocuo por fallo de infraestructura»; (3) **divulgación**: `summary["advisory_issues"]` llega al `human_checklist.md` vía el nuevo parámetro `advisory_issues` de `HumanChecklistGenerator.generate()`, antes los fallos advisory eran invisibles para el humano; (4) `content_quality` con solo warnings pasa de `PASSED` a `WARNING`, el estado que ya existía y nadie producía. **`asset_confidence` sigue bloqueando** (dossier §8.2: es el único mecanismo que vuelve no-entregable un paquete Tier C con 100 % assets ESTIMATED — ~37 % del corpus). ⚠️ **Medido**: contrafactual sobre las 2 corridas reales disponibles ⟹ **0 flips de `ready`** y **2 advisories nuevos divulgados** ⟹ la fase **no relajó veredictos**, corrigió el mecanismo y la visibilidad | H10; §8.1 (cuatro regímenes), §8.2 (asset_confidence medido), §8.4; docstrings 10+3 vs código 13 | ✅ 2026-09-03 |
| E | A2: `site_presence_snapshot` persistido en disco + A6: `asset_path` poblado | A2, A6 (§9.1); H7; DT4-N2 mitad disco pendiente | ⬜ Pendiente |
| F | A4: oráculo único de presencia + A1: `skipped != passed` (`NOT_EVALUATED`) + N11: gate respeta `is_coherent` | A4, A1 (§9.1); V15; N11/P9 (deuda más grave) | ⬜ Pendiente |
| G | Ceguera de gates: `doc_audit_consistency` cableado + `critical_recall` expandido + escotillas V5/V9 cerradas sin reversar BUG-6 | §12.5 Nivel 3.7; V5, V9, V10 | ⬜ Pendiente |
| H | Quirúrgicos: V6 (`except Exception`), V7 (guard `__iter__`), V8 (dedup), V11 (residuos D6), V12 (doc OPS), V13 (gemelos `MetadataValidator`) | §12.5 Nivel 3.8; V6, V7, V8, V11, V12, V13 | ⬜ Pendiente |

---

## Sección C — Ejecución E2E (FASE-I)

> Resultado certificado de la **única** corrida `v4complete` del plan, sobre Hotel Salento Real.
> La llena FASE-I y la certifica FASE-VERIFY. **Valores reales, no de fixture.**

| Campo | Baseline (FASE-D 2026-08-31 12:28) | Corrida FASE-I | Delta | AC relacionado |
|-------|------------------------------------|----------------|-------|----------------|
| `no_breach` (proposal_asset_matrix) | 6 | *(pendiente)* | *(pendiente)* | AC5 |
| `coverage_ratio` | 1.000 (tautológico) | *(pendiente)* | *(pendiente)* | AC6 |
| `is_coherent` (3 artefactos / 6 copias) | `false` | *(pendiente)* | *(pendiente)* | AC6, AC12 |
| `coherence` score | 0.88 | *(pendiente)* | *(pendiente)* | NR2 |
| Gates ejecutados | 13 | *(pendiente: 11+2)* | *(pendiente)* | NR3 |
| `site_presence_snapshot` en disco | **ausente** | *(pendiente: presente)* | *(pendiente)* | AC9 |
| `asset_path` en entradas LINKED | `null` | *(pendiente)* | *(pendiente)* | AC9 |
| G9 (delivery_quality_report) | `skipped` contaba como `passed` | *(pendiente: NOT_EVALUATED)* | *(pendiente)* | AC11 |
| ZIP de delivery | generado | *(pendiente)* | *(pendiente)* | NR4 |

**Anomalías preexistentes** (no cuentan como regresión): *(FASE-I las clasifica; VERIFY las confirma)*.

---

## Sección D — Métricas acumulativas

> Se actualiza al cierre de **cada** fase. RELEASE cierra con el total final.

| Métrica | Valor inicial | Valor actual | Última fase que actualizó |
|---------|---------------|--------------|---------------------------|
| Tests totales (`def test_`) | 3,689 | **3,763** atribuibles al plan (**A 21 + B 29 + D 24 = 74**) · 288 archivos `.py` en `tests/`. Medición 2026-09-03 al cierre de D: `git grep -h "def test_" HEAD -- tests` = **3,734** (= 3,689 + A 21 + D 24, lo commiteado) y el árbol de trabajo = **3,763** porque el trabajo de la sesión paralela de **B sigue sin commitear** (+29). ⚠️ `AGENTS.md`/README documentan **3,689** ⟹ desfase de +74 pendiente de **S11/RELEASE** | D |
| Tests quality_gates + asset_generation | 848 passed / 2 skipped | **872 passed / 2 skipped** tras D = 848 **+ 24 tests propios**, 0 regresiones (`evidence/FASE-D/faseD_baseline_{pre,post}.txt`). B lo había dejado idéntico en 848 porque sus tests viven en `tests/commercial_documents`, fuera de los dos directorios contados. ⚠️ Medido sobre el árbol **combinado** B+D (concurrencia L-D1) | D |
| Contract tests agregados | 0 | **74 funciones / 107 casos**: A = 21/37 (`tests/common/test_service_identity_registry.py`) + B = 29/46 (`test_pain_map_bijection.py` 11/28 + `test_detect_pains_emisiones_faseB.py` 18/18) + D = 24/24 (`test_gate_severity_lists.py` 8 + `TestFASEDGateSeverity` 12 + `TestAdvisoryDisclosureFASED` 4; sin parametrizar) | D |
| Fases completadas | 0 / 11 | **3 / 11** (A, B, D) — B y D en **sesiones paralelas** sobre el mismo working tree (L-D1) | D |
| Versión | 4.74.1 | 4.74.1 *(solo RELEASE la mueve)* | — |
| Registros de identidad consolidados | ≥9 dispersos (dossier) → **15** reales tras el censo (C-5 añadió el #15) | **1 canónico** (`SERVICE_IDENTITIES`) + **Capa 1** (`PAIN_SOLUTION_MAP`) + **6 derivados** + **4 validados contra Capa 1** + **3 fuera de alcance** — censo §8.2. **B retiró 1 pain_id de Capa 1** (`no_ga4_enhanced`, guardia insatisfacible) ⟹ Capa 1 = **26**, no 27: cualquier cita de «27» en docs/prompts posteriores quedó desactualizada | B |
| Peso de impacto de narratives (S14/C-5) | 16 valores × 4 copias YAML + 16 fallbacks Python = **80 literales** | **20 valores × 4 regiones** (los 4 pains nuevos declarados en `regional_benchmarks.yaml`) + fallback Python **derivado del `estimated_impact` de Capa 1** (nunca un default mudo). La costura de regionalización se preservó a propósito (S-B8 pide el lint, no el colapso) | B |
| Gates blocking / advisory | 10 / 3 (declarado) · 13 plano (código) | **11 / 2 declarado = 11 / 2 en código**, decidido por `gate_blocks_publication()`. El `RuntimeError` de `__init__` hace imposible que las dos vistas diverjan. **Tres regímenes cerrados, el cuarto (delivery) intacto a propósito** (H10). Verificado por contrafactual: **0 flips de `ready`** sobre 2 corridas reales | D |

> **Conteos de tests** (memoria `conteos-tests-documentados-metodo-def_test`): documentar por
> `grep "def test_"`, no por `--collect-only` (3,631 vs 3,520). Actualizar README + AGENTS **juntos**.

---

## Sección E — Archivos afiliados actualizados

> Archivos de producción y documentación **modificados** por el plan. RELEASE los consolida en el
> CHANGELOG (`### Archivos Modificados`).

| Fase | Archivo modificado | Región / cambio | Estado |
|------|--------------------|-----------------|--------|
| A | `modules/asset_generation/proposal_asset_alignment.py` | **DERIVADO**. `:1-45` import de `..common.service_identity` + `PROPOSAL_SERVICE_TO_ASSET` como dict-comprehension sobre `SERVICE_IDENTITIES` filtrado por `counts_in_alignment`; `ALL_PROMISED_SERVICES` deriva de él; comentario del drift (copia #1) reescrito preservando las 2 NOTEs históricas. `:219` y `:993` no requirieron cambio. **`:609-612` / `:792-794` intactos (trampa A5 → FASE-C)** | ✅ 2026-09-03 |
| A | `modules/asset_generation/conditional_generator.py` | **VALIDADO, no derivado** (+ comentario en `:230-241`). `PAIN_TO_ASSET` (atributo de clase, 11 entradas) responde otra pregunta — enruta qué asset *generar*, no qué servicio *vender*: derivarlo haría que `poor_performance` generara `optimization_guide` en vez de `performance_audit`. `:314-326` sin cambio | ✅ 2026-09-03 |
| A | `modules/asset_generation/pain_ledger.py` | **PARCIAL**. `NORMALIZATION_RULES` **derivado** de `PainSolutionMapper.PAIN_SOLUTION_MAP` (corrige N-A2: faltaban 2 entradas y había 1 clave obsoleta). `PAIN_TO_PRESENCE_ASSET` **no derivado** a propósito: la derivación completa produce 13 vs sus 6 y cambia la semántica de `apply_site_verification` → insumo de **FASE-F** (A4/V15) | ✅ 2026-09-03 |
| A | `modules/commercial_documents/v4_diagnostic_generator.py` | `:126-166` — los **6 IDs fantasma + 1 asset fantasma** corregidos a `None`/asset real; falso encabezado «ÚNICA FUENTE DE VERDAD» y el «Sincronizar con» manual reemplazados por la regla. `ELEMENTO_KB_TO_PAIN_ID` **validado, no derivado** (responde «qué elemento del KB dispara qué pain», no identidad de servicio). `:3067-3086` sin cambio (solo itera `.keys()`) | ✅ 2026-09-03 |
| A | `modules/commercial_documents/v4_proposal_generator.py` | **DERIVADO** (2 registros locales de método). `:1281-1289` `service_brecha_candidates` ← `identidad.brecha_candidates` (**solo la fuente de identidad; la lógica intacta, como exigía A4** — C2 la reescribe); `:1365-1372` `ASSET_TO_PAIN_ID` ← canónico (**copia #3 del drift eliminada**). Único lector confirmado por grep: `:1410` | ✅ 2026-09-03 |
| A | `modules/commercial_documents/service_catalog.py` *(no previsto en el plan)* | **DERIVADO**. `SERVICE_CATALOG` construido desde `SERVICE_IDENTITIES`; **eliminada** la mutación post-hoc `SERVICE_CATALOG["optimizacion_ia_generativa"] = ServiceEntry(...)` (**copia #2 del drift**). `SERVICE_TO_ASSET_LOOKUP = dict(PROPOSAL_SERVICE_TO_ASSET)` ya derivaba — sin cambio | ✅ 2026-09-03 |
| A | `tests/commercial_documents/test_proposal_dynamic.py` *(no previsto en el plan)* | **6 aserciones fosilizadas desfossilizadas**, 3 tests renombrados, 1 docstring corregido. El renombrado clave: `test_all_service_catalog_services_have_lookup_entry` codificaba el invariante **invertido** (que la demanda sea el drift) → `test_solo_servicios_alineables_tienen_lookup_entry`. Ahora deriva sus expectativas de `SERVICE_IDENTITIES` | ✅ 2026-09-03 |
| B | `modules/commercial_documents/pain_solution_mapper.py` | **3 cambios**. (1) `PAIN_SOLUTION_MAP` `:60` — **retirada** la entrada `no_ga4_enhanced` (comentario de retiro en `:188`), Capa 1 27 → 26; (2) `_detect_analytics_pains` `:720` — **eliminada** la rama muerta `elif status and hasattr(status, "is_enhanced")`; (3) `detect_pains` `:333` — **3 ramas emisoras nuevas** con guard, insertadas antes de `# Sort by severity` (+85 líneas en el archivo). ⚠️ **Desplazó las citas de H**: el guard `__iter__` de V7 está ahora en **`:447`** (era `:453`) y la emisión `low_ota_divergence` en **`:452`** (era `:457`) | ✅ 2026-09-03 |
| B | `modules/commercial_documents/v4_diagnostic_generator.py` | **Confinado a `_pain_to_brecha`**, como exigía el prompt. `:3346-3369`: el `return None` del descarte silencioso se reemplazó por una **derivación de Capa 1** (nombre y detalle del registro canónico; peso de `pain_narratives` con fallback derivado de `estimated_impact`). El dict literal `narratives` `:3263-3344` quedó **byte-idéntico** (16 entradas) — prueba de que no se creó tabla paralela (L-NC4). **V6 `:3197-3202` y V11 `:1953` intactos y en su posición** | ✅ 2026-09-03 |
| B | `config/regional_benchmarks.yaml` *(no previsto en la Sección E; asignado a B por S14)* | `pain_narratives` de las **4 regiones**: 16 → **20 entradas** cada una (+32 líneas). Los 4 pains que dejaron de descartarse reciben peso explícito (`low_ota_divergence 0.20`, `missing_alt_text 0.10`, `missing_llmstxt 0.08`, `no_social_links 0.08`). Se preservó la costura de regionalización a propósito; el lint de sincronía queda como S-B8 | ✅ 2026-09-03 |
| B | `modules/asset_generation/asset_catalog.py` *(no previsto en el plan)* | `:298` — `promised_by` del asset huérfano: se retiró `"no_ga4_enhanced"` junto con el pain, para no dejar un asset prometido por un pain_id inexistente | ✅ 2026-09-03 |
| B | `README.md` | `:222` — `Pain narratives (16)` → `(20)`. Lo exige `run_all_validations.py --quick` (check «README numerical counts vs code»), que falló 6/7 hasta corregirlo. Se preservó el número desnudo porque el validador lo busca por regex | ✅ 2026-09-03 |
| C | `modules/commercial_documents/v4_proposal_generator.py` | `:1281-1289` `service_brecha_candidates` dinámico | ⬜ Pendiente |
| C | `modules/commercial_documents/templates/propuesta_v6_template.md` | `${dynamic_services_table}` | ⬜ Pendiente |
| C | `modules/asset_generation/proposal_asset_alignment.py` | `:575-659` y `:748-789` builders (A5: **uno** solo) | ⬜ Pendiente |
| D | `modules/quality_gates/publication_gates.py` | **2064 → 2181 líneas (+117)**. `:4` docstring de módulo y `:232` docstring de clase → «11 blocking + 2 advisory»; **`:130-190` bloque nuevo** = única fuente del régimen (`BLOCKING_GATE_NAMES` 11 en `:130`, `ADVISORY_GATE_NAMES` 2 en `:144`, `PROPOSAL_ASSET_ALIGNMENT_FLOOR` `:152`, `GATE_EXECUTION_FAILED_KEY` `:155`, `gate_severity()` `:158`, `advisory_degrades_to_blocking()` `:163`, `gate_blocks_publication()` `:179`); `__init__` **`:268-278`** fail-fast (registro ↔ severidad); `:307` el camino de excepción de `run_all` señala `GATE_EXECUTION_FAILED_KEY`; `:311` `is_ready_for_publication` y `:326` `get_blocking_gates` deciden por el predicado; `:827` `content_quality` con solo warnings emite `GateStatus.WARNING` (antes `PASSED`); `:2010/:2065` `check_publication_readiness` filtra por severidad y expone `summary["blocking_gate_names"]` + `summary["advisory_issues"]`; `__all__` +6 nombres. ⚠️ **Desplazó +91 líneas** todo símbolo posterior a `:130` ⟹ las citas de los prompts C, F y G de este archivo están **fosilizadas** (ver L-A6 en `dependencias-fases.md`) | ✅ 2026-09-03 |
| D | `modules/quality_gates/human_checklist_generator.py` | **Divulgación D2 (riesgo C)**. `generate(report, advisory_issues: Optional[List[Dict[str, Any]]] = None)` — nuevo parámetro con default ⟹ retrocompatible. Sección **5b** antes de los ítems de decisión comercial para que `items[:MAX_ITEMS]` no los corte: cada advisory no bloqueante se imprime como `ADVISORY <gate>: <message> — no bloquea la publicacion, decidir antes de entregar`. Sin esto un gate advisory que falla es **invisible para el humano**, que era el defecto de raíz de H10 | ✅ 2026-09-03 |
| D | `main.py` | 4 hunks: `:2915` importa `gate_blocks_publication`; `:2952` consola en 3 estados (✅ / ❌ / ⚠️) en vez de 2; `:2965-2966` imprime los advisories no bloqueantes; `:3181-3185` cablea `advisory_issues` desde `readiness_report["summary"]` al checklist. `delivery_quality_report.py` **no se tocó** (régimen delivery, dueño E→F) | ✅ 2026-09-03 |
| D | `tests/quality_gates/test_publication_gates.py` | `+127` líneas: helper `_gate()` + `class TestFASEDGateSeverity` (**12 tests**) conductuales — advisory que falla por encima del piso no bloquea, `content_quality` con blockers sí bloquea, `proposal_asset_alignment` bajo/sobre 0.8, `asset_confidence` sigue bloqueando, WARNING divulgado, advisory que **no se ejecutó** bloquea, `run_all` marca el fallo de ejecución, paridad con `get_blocking_gates`. 69 passed / 1 skipped en el archivo | ✅ 2026-09-03 |
| D | `tests/quality_gates/test_human_checklist_generator.py` | `+48` líneas: `class TestAdvisoryDisclosureFASED` (**4 tests**) — el checklist contiene el advisory, respeta `MAX_ITEMS`, y sigue funcionando sin el parámetro (retrocompatibilidad) | ✅ 2026-09-03 |
| D | `AGENTS.md` | Fila `quality_gates/` de «Módulos Activos» → **11 blocking (con `asset_confidence`) + 2 advisory** nombrados; bloque «FASE 4.5» del flujo reagrupado por severidad **y completado a 13** (faltaba `doc_audit_consistency`). Lo verifica `validate_agents_md.py` (6 PASS / 0 FAIL) + el candado de docstrings | ✅ 2026-09-03 |
| E | `modules/quality_gates/alignment_result.py` | `asset_path` poblado (consumidor de A6) | ⬜ Pendiente |
| F | `modules/quality_gates/alignment_result.py` | `:62` `_presence_resolved` → oráculo único | ⬜ Pendiente |
| F | `modules/quality_gates/delivery_quality_report.py` | `:250-257`, `:310-319`, `:325` skipped≠passed | ⬜ Pendiente |
| F | `modules/commercial_documents/coherence_validator.py` | `:670`, `:689-700` (`score=1.0` hardcode), N11 | ⬜ Pendiente |
| G | `modules/quality_gates/publication_gates.py` | `:1244` `doc_audit_consistency`, `:1237-1242` V5, `:1295-1344` V9. ⚠️ **Citas desplazadas +91 por FASE-D (L-A6)**: posiciones vigentes medidas — `_doc_audit_consistency_gate` **`:1555`**, `_JUSTIFIED_STATUSES` **`:1328`**, `_coverage_gate` **`:1335`** | ⬜ Pendiente |
| G | `modules/auditors/v4_comprehensive.py` | `:1789` `_identify_critical_issues` (PageSpeed ERROR + GEO) | ⬜ Pendiente |
| H | `modules/commercial_documents/pain_solution_mapper.py` | **`:447`** V7 *(era `:453` antes de FASE-B — L-A6)* · V8: las dos emisiones duplicadas de `low_organic_visibility` están ahora en **`:750-757`** y **`:761-768`** dentro de `_detect_analytics_pains` *(el plan citaba `:677-701`; medido post-B)* | ⬜ Pendiente |
| H | `modules/commercial_documents/v4_diagnostic_generator.py` | `:3197-3202` V6, `:1945-1952` V11 | ⬜ Pendiente |
| H | `modules/auditors/v4_comprehensive.py` | `:1841` residuo D6 | ⬜ Pendiente |
| H | `data_validation/metadata_validator.py` + `modules/data_validation/metadata_validator.py` | V13 unificación de gemelos | ⬜ Pendiente |
| RELEASE | `VERSION.yaml`, `CHANGELOG.md`, `GUIA_TECNICA.md`, `REGISTRY.md`, `README.md`, `.cursorrules`, `docs/CONTRIBUTING.md`, `DOMAIN_PRIMER.md` | Cierre documental 4.75.0 | ⬜ Pendiente |

> **Archivos NO tocados** (decisión explícita del plan): `delivery_quality_report.py:289`
> `BLOCKING_GATE_NAMES` (rige el ZIP, régimen de delivery, no publicación — §8.4 punto 3); `.env`
> (V12 es decisión OPS, se documenta, no se edita).
