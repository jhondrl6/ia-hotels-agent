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
| B | `tests/commercial_documents/test_pain_map_bijection.py` | Guardián AST **tridireccional** de la biyección mapa↔emisión↔narrativa (patrón SR-A, no regex) | ⬜ Pendiente |
| E | `modules/.../site_presence_writer.py` *(nombre a confirmar en E1)* | Persiste `site_presence_snapshot` en disco (mitad pendiente de DT4-R2) | ⬜ Pendiente |
| D | `tests/quality_gates/test_gate_severity.py` | Lock de regresión de la estructura 11 blocking + 2 advisory | ⬜ Pendiente |
| … | *(agregar filas si una fase crea archivos no previstos)* | | |

**Nota**: los nombres exactos los fija cada fase en su implementación; esta tabla se corrige al cierre de
fase con el nombre real. Lo importante para RELEASE es la **lista consolidada de archivos nuevos**.

---

## Sección B — Funcionalidades nuevas

> Comportamiento **nuevo o modificado** que el sistema gana con el plan.

| Fase | Funcionalidad | Hallazgo del dossier que cura | Estado |
|------|---------------|-------------------------------|--------|
| A | Fuente única de identidad servicio↔asset↔pain en `modules/common/service_identity.py`, en **dos capas** (Capa 1 = `PAIN_SOLUTION_MAP` 27 pains como universo de pain_id, intacto; Capa 2 = `SERVICE_IDENTITIES` 8 entradas). De los **14** registros censados (el dossier decía ≥9): **6 derivados** del canónico, **6 validados** contra Capa 1 con razón registrada, 2 fuera de alcance. Drift «8 vs 7» disuelto **eliminando sus 3 copias**, no comparándolas. Perla `monthly_report → no_faq_schema` eliminada. 6 IDs fantasma + 1 asset fantasma corregidos sin cambio de comportamiento (contrafactual medido) | V2, V3, V14 (§12.3); causa raíz §12.5 (≥9 registros); deuda P10 | ✅ 2026-09-03 |
| B | Biyección **triple** mapa↔emisión↔narrativa: cada pain o se emite **y** tiene narrativa, o está justificado | V1 (9 pains muertos) + N-A1 (2 que se emitían y se descartaban) = **11**; §3 candado de biyección | ⬜ Pendiente |
| C | **Punto 8**: propuesta dinámica — solo promete servicios con brecha detectada (`no_breach = 0` por construcción) | §9.2 B1-B5; tautología de coverage; `is_coherent = false` estructural | ⬜ Pendiente |
| D | Severidad de gates: **11 blocking + 2 advisory** con piso explícito y WARNING a `human_checklist` | H10; §8.4; docstrings 10+3 vs código 13 | ⬜ Pendiente |
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
| Tests totales (`def test_`) | 3,689 | **3,710** (285 archivos `.py` en `tests/`) | A |
| Tests quality_gates + asset_generation | 848 passed / 2 skipped | **848 passed / 2 skipped / 11 warnings** (NR5 ✅ — diff vs pre-cambio = 1 línea, la duración) | A |
| Contract tests agregados | 0 | **21 funciones / 37 casos parametrizados** (`tests/common/test_service_identity_registry.py`) | A |
| Fases completadas | 0 / 11 | **1 / 11** | A |
| Versión | 4.74.1 | 4.74.1 *(solo RELEASE la mueve)* | — |
| Registros de identidad consolidados | ≥9 dispersos (dossier) → **15** reales tras el censo (C-5 añadió el #15) | **1 canónico** (`SERVICE_IDENTITIES`) + **Capa 1** (`PAIN_SOLUTION_MAP`) + **6 derivados** + **4 validados contra Capa 1** + **3 fuera de alcance** — censo §8.2 | A |
| Gates blocking / advisory | 10 / 3 (declarado) · 13 plano (código) | 10 / 3 · 13 plano *(sin cambio — es FASE-D)* | — |

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
| B | `modules/commercial_documents/pain_solution_mapper.py` | `:60` `PAIN_SOLUTION_MAP` (27), `:339` `detect_pains` | ⬜ Pendiente |
| C | `modules/commercial_documents/v4_proposal_generator.py` | `:1281-1289` `service_brecha_candidates` dinámico | ⬜ Pendiente |
| C | `modules/commercial_documents/templates/propuesta_v6_template.md` | `${dynamic_services_table}` | ⬜ Pendiente |
| C | `modules/asset_generation/proposal_asset_alignment.py` | `:575-659` y `:748-789` builders (A5: **uno** solo) | ⬜ Pendiente |
| D | `modules/quality_gates/publication_gates.py` | `:4`, `:162`, `:181`, `:239-249`, `:1967` severidad 11+2 | ⬜ Pendiente |
| D | `AGENTS.md` | tabla Módulos Activos + bloque FASE 4.5 → 11+2 | ⬜ Pendiente |
| E | `modules/quality_gates/alignment_result.py` | `asset_path` poblado (consumidor de A6) | ⬜ Pendiente |
| F | `modules/quality_gates/alignment_result.py` | `:62` `_presence_resolved` → oráculo único | ⬜ Pendiente |
| F | `modules/quality_gates/delivery_quality_report.py` | `:250-257`, `:310-319`, `:325` skipped≠passed | ⬜ Pendiente |
| F | `modules/commercial_documents/coherence_validator.py` | `:670`, `:689-700` (`score=1.0` hardcode), N11 | ⬜ Pendiente |
| G | `modules/quality_gates/publication_gates.py` | `:1244` `doc_audit_consistency`, `:1237-1242` V5, `:1295-1344` V9 | ⬜ Pendiente |
| G | `modules/auditors/v4_comprehensive.py` | `:1789` `_identify_critical_issues` (PageSpeed ERROR + GEO) | ⬜ Pendiente |
| H | `modules/commercial_documents/pain_solution_mapper.py` | `:453` V7, `:677-701` V8 | ⬜ Pendiente |
| H | `modules/commercial_documents/v4_diagnostic_generator.py` | `:3197-3202` V6, `:1945-1952` V11 | ⬜ Pendiente |
| H | `modules/auditors/v4_comprehensive.py` | `:1841` residuo D6 | ⬜ Pendiente |
| H | `data_validation/metadata_validator.py` + `modules/data_validation/metadata_validator.py` | V13 unificación de gemelos | ⬜ Pendiente |
| RELEASE | `VERSION.yaml`, `CHANGELOG.md`, `GUIA_TECNICA.md`, `REGISTRY.md`, `README.md`, `.cursorrules`, `docs/CONTRIBUTING.md`, `DOMAIN_PRIMER.md` | Cierre documental 4.75.0 | ⬜ Pendiente |

> **Archivos NO tocados** (decisión explícita del plan): `delivery_quality_report.py:289`
> `BLOCKING_GATE_NAMES` (rige el ZIP, régimen de delivery, no publicación — §8.4 punto 3); `.env`
> (V12 es decisión OPS, se documenta, no se edita).
