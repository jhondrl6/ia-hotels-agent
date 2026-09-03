# FASE-A — Fuente única de identidad servicio↔asset↔pain

**ID**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03 / FASE-A
**Objetivo**: Construir UN registro canónico de identidad servicio↔asset↔pain del que deriven (o contra
el que validen) los ≥12 registros censados (9 del dossier + 3 del complemento de auditoría 2026-09-03),
con contract tests que fallen fuerte ante drift. Corrige
V2 (6 IDs fantasma), V3 (fragmentación ≥9 + perla `monthly_report → no_faq_schema`) y V14 (drift «8 vs 7» en 3 copias).
**Dependencias**: Ninguna — es la base del plan.
**Duración estimada**: 4-6 horas
**Complejidad técnica**: **ALTA**
**Modo de ejecución**: **DIRECTO** (no delegable)
**Skill**: `phased_project_executor.md` v2.18.0
**Presupuesto**: ≤55 iteraciones (R2 tope: 60)
**ACs que cierra**: AC1, AC2, AC3

---

## Contexto

El dossier de estabilización pre-tribunal
(`.opencode/context/CONTEXT-AUDITORIA-BRECHAS-VS-MODULOS-SALENTOREAL-2026-09-03.md`) identificó una
causa raíz única con tres manifestaciones. Su §12.5 la nombra verbatim:

> *"contrato de detección fragmentado y sin candado — ≥9 registros no canónicos, consumidores derivan
> de copias parciales, 0 tests fijan la biyección."*

Esta fase construye el **contrato único** (Nivel 1.2 del dossier). Va PRIMERA porque ROADMAP v4.2 §7.2
establece que *"decidir cuál registro manda es precondición de la propuesta dinámica"* — el punto 8
(FASE-C) necesita un registro del que derivar la promesa; construirlo sobre una copia parcial
reproduciría el drift que FASE-SR-B ya resolvió una vez.

### Por qué es complejidad ALTA y no delegable

Dos de los registros alimentan **narrativa comercial visible**. Un error de migración cambia lo que se
le promete al cliente, no solo un conteo interno. Y la decisión de *cuál registro manda* es
arquitectónica cross-module: requiere conocer a los 6 módulos consumidores simultáneamente. Un
subagente carece de ese contexto (lección DT-3 del executor).

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| (ninguna — FASE-A es la primera) | — |

### Base Técnica Disponible

- **Repo**: v4.74.1 (`VERSION.yaml`), rama `master`, working tree limpio
- **Python**: `./venv/Scripts/python.exe` (venv Windows — los subagentes no pueden importar `bs4`/`selenium`)
- **Tests base**: 3.689 funciones en 284 archivos; baseline del dossier §8.6: **848 passed / 2 skipped**
  en `tests/quality_gates` + `tests/asset_generation`
- **Patrón a copiar**: guardián AST de FASE-SR-A (contract test transversal, no regex)
- **Artefactos de referencia**: `output/FASE-D_salentoreal_post_guard/v4_complete/` (corrida baseline
  2026-08-31 12:28, coherence 0.88, 13/13 gates)

### Los registros censados: 9 del dossier (V3 + B3) + 3 del complemento de auditoría (≥12)

| # | Registro | Ubicación |
|---|----------|-----------|
| 1 | `PROPOSAL_SERVICE_TO_ASSET` | `modules/asset_generation/proposal_asset_alignment.py:22` (exportado en `:993`) |
| 2 | `PAIN_SOLUTION_MAP` (27 entradas, C5) | `modules/commercial_documents/pain_solution_mapper.py:60` |
| 3 | `ASSET_NAMES` | `modules/commercial_documents/pain_solution_mapper.py:311` |
| 4 | `ELEMENTO_KB_TO_PAIN_ID` | `modules/commercial_documents/v4_diagnostic_generator.py:135-157` (derivación en `:160`, validación en `:3067-3086`) |
| 5 | `PAIN_TO_ASSET` | `modules/asset_generation/conditional_generator.py:234-257` (importa #4 en `:314-326`) |
| 6 | `service_brecha_candidates` | `modules/commercial_documents/v4_proposal_generator.py:1281-1289` |
| 7 | `ASSET_TO_PAIN_ID` | `modules/commercial_documents/v4_proposal_generator.py:1365-1372` |
| 8 | `NORMALIZATION_RULES` / `PAIN_TO_PRESENCE_ASSET` | `modules/asset_generation/pain_ledger.py:52-94` |
| 9 | `SERVICE_CATALOG` | `service_catalog` (referenciado por #4 y por el drift «8 vs 7») |
| 10 | `pain_to_type` (fallback silencioso `cms_defaults`) | `modules/commercial_documents/v4_diagnostic_generator.py:3543-3546` — alimenta la columna «Problema que resuelve» de la propuesta |
| 11 | Tablas de brechas con IDs fantasma | `modules/financial_engine/opportunity_scorer.py:113-202` (`no_llms_txt`, `ia_crawler_blocked`, `weak_brand_signals`) — scorea las brechas que narra el diagnóstico |
| 12 | Tercer universo de nombres fantasma | `modules/analyzers/gap_analyzer.py:199-201` (legacy `spark`, fuera de migración) |

**Complemento de auditoría del plan (2026-09-03)**: el censo de 9 del dossier no era completo. Los
registros #10 y #11 se migran en A3/A4; el #12 queda como legacy (spark deprecado) y por eso el grep
de AC1 se acota a `modules/commercial_documents` + `modules/asset_generation`.

**Perla de V3**: `ASSET_TO_PAIN_ID` atribuye `monthly_report → "no_faq_schema"` (`:1366`),
contradiciendo a `service_catalog` (`no_monthly_report`).

**Los 6 IDs fantasma de V2** (referenciados por #4, inexistentes en #2): `no_speakable`,
`no_llms_txt`, `ia_crawler_blocked` (vs el real `ai_crawler_blocked`), `weak_brand_signals`,
`no_entity_schema`, `no_factual_data`.

**Las 3 copias del drift «8 vs 7» de V14**: `proposal_asset_alignment.py:35-37`, `service_catalog`,
`v4_proposal_generator.py:1332` (*"los 8 servicios definidos en PROPOSAL_SERVICE_TO_ASSET"* — tiene 7).

---

## Tareas

### Tarea A1: Censo de registros con derivaciones reales

**Objetivo**: Inventariar los ≥12 registros (9 del dossier + 3 del complemento de auditoría) verificando
— no asumiendo — quién escribe, quién lee y qué copia de qué. El dossier los censó por grep; esta tarea
los censura por **uso real**.

**Archivos afectados**: ninguno (solo lectura) + salida nueva `evidence/FASE-A/censo-registros.md`

**Criterios de aceptación**:
- [ ] Tabla con una fila por registro: nombre, ubicación exacta (`archivo:línea`), nº de entradas,
      consumidores reales (grep de import/uso, no de mención en docstring)
- [ ] Cada ID fantasma de V2 confirmado o refutado **contra el registro #2 real**
- [ ] La perla de V3 (`monthly_report`) confirmada o refutada
- [ ] Las 3 copias del drift «8 vs 7» localizadas con línea exacta
- [ ] **Decisión documentada**: cuál registro manda y por qué (con alternativas rechazadas)
- [ ] Salida escrita en `evidence/FASE-A/censo-registros.md`

⚠️ **Regla de oro** (lección ROADMAP v4.0→v4.1): *revalidar citas de código NO revalida premisas*.
Si el censo refuta una afirmación del dossier, registrarla como corrección y ajustar el diseño — no
forzar el diseño para que coincida con el dossier.

### Tarea A2: Registro canónico + contract tests

**Objetivo**: Construir el registro canónico y sus contract tests **antes** de migrar consumidores (TDD).

**Archivos afectados**:
- Nuevo módulo (ubicación = decisión de A1; candidatos naturales: `modules/common/` junto a los loaders
  compartidos, o `modules/asset_generation/` junto a `asset_catalog.py`)
- `tests/common/test_service_identity_registry.py` (o el directorio que corresponda a la ubicación)

**Criterios de aceptación**:
- [ ] Contract tests escritos y **fallando en rojo** antes de implementar (TDD, precedente SR-H2)
- [ ] Guardián **AST**, no regex (patrón FASE-SR-A)
- [ ] Tests de contrato **narrativa↔fuente**, no valores fijos (anti-lección **L-NC10**: un test que
      fija `coverage == 1.0` o una lista literal de 7 servicios fosiliza el drift en vez de curarlo)
- [ ] ⚠️ **Guardrail L-NC4**: NO crear tablas paralelas nuevas. El registro debe ser **consumido** por
      la narrativa, no duplicado para ella. Si el diseño exige una tabla nueva de pain_id→texto,
      detenerse y registrar la decisión.
- [ ] Test que falla si aparece un ID en cualquier registro derivado que no exista en el canónico
- [ ] Test que falla si dos registros atribuyen el mismo asset a pains distintos (caso V3)

### Tarea A3: Migrar consumidores aguas arriba

**Objetivo**: Que `conditional_generator`, `pain_ledger` y `proposal_asset_alignment` deriven del
canónico en vez de mantener copia. Corregir los 6 IDs fantasma de V2 y la perla de V3.

**Archivos afectados**:
- `modules/asset_generation/conditional_generator.py:234-257` (`PAIN_TO_ASSET`), `:314-326` (import de `ELEMENTO_KB_TO_PAIN_ID`)
- `modules/asset_generation/pain_ledger.py:52-94` (`NORMALIZATION_RULES`, `PAIN_TO_PRESENCE_ASSET`)
- `modules/asset_generation/proposal_asset_alignment.py:22` (`PROPOSAL_SERVICE_TO_ASSET`), `:219`, `:609`, `:792`, `:993`

**Criterios de aceptación**:
- [ ] Los 3 módulos derivan del canónico (import) o validan contra él
- [ ] 0 IDs fantasma (alcance: `modules/commercial_documents` + `modules/asset_generation`): `grep -rn "no_speakable\|no_llms_txt\|ia_crawler_blocked\|weak_brand_signals\|no_entity_schema\|no_factual_data" modules/commercial_documents modules/asset_generation` → 0
- [ ] `ia_crawler_blocked` unificado a `ai_crawler_blocked` (o decisión registrada en A1)
- [ ] `ASSET_TO_PAIN_ID["monthly_report"]` resuelto a favor del canónico (AC3)
- [ ] Contract tests de A2 en verde
- [ ] ⚠️ **NO tocar las rutas de skip silencioso** (`proposal_asset_alignment.py:609-612` *"Unknown
      service — skip silently"* y `:792-794`): son la trampa **A5** y pertenecen a FASE-C. Si se
      modifican aquí, FASE-C pierde su punto de comparación.

### Tarea A4: Migrar consumidores aguas abajo + drift «8 vs 7»

**Objetivo**: Que `v4_proposal_generator`, `v4_diagnostic_generator` y `service_catalog` deriven del
canónico, y que el drift «8 vs 7» quede corregido en sus **tres** copias con un test que falle si reaparece.

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py:1281-1289` (`service_brecha_candidates`), `:1332` (drift), `:1365-1372` (`ASSET_TO_PAIN_ID`)
- `modules/commercial_documents/v4_diagnostic_generator.py:135-157`, `:160`, `:3067-3086`, `:3543-3546` (`pain_to_type`, registro #10)
- `modules/financial_engine/opportunity_scorer.py:113-202` (tablas de brechas con IDs fantasma, registro #11)
- `modules/asset_generation/proposal_asset_alignment.py:35-37`
- `service_catalog`

**Criterios de aceptación**:
- [ ] Las 3 copias del drift «8 vs 7» corregidas (AC2)
- [ ] Test de contrato narrativa↔fuente que falla si un string hardcodeado vuelve a declarar un nº de
      servicios distinto al del canónico (detección proactiva de strings hardcodeados, nota §12.4 del dossier)
- [ ] ⚠️ **NO reescribir la lógica de `service_brecha_candidates`**: solo su fuente de identidad. La
      propuesta dinámica es FASE-C.
- [ ] `python scripts/run_all_validations.py --quick` → 7/7
- [ ] `python scripts/validate_agents_md.py` → 6 PASS / 0 FAIL

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Contract tests del registro canónico | `tests/common/test_service_identity_registry.py` (o el que decida A1) | Todos en verde; escritos ANTES del fix y vistos en rojo |
| Guardián AST anti-drift | ídem | Falla si un registro derivado declara un ID ausente del canónico |
| Biyección de atribución asset↔pain | ídem | Falla si dos registros atribuyen el mismo asset a pains distintos |
| Contrato narrativa↔fuente del conteo de servicios | ídem | Falla si reaparece el drift «8 vs 7» |
| Baseline del dossier §8.6 | `tests/quality_gates/` + `tests/asset_generation/` | **848 passed / 2 skipped** preservado (o delta explicado) |
| Validadores del proyecto | `scripts/` | `run_all_validations.py --quick` 7/7 · `validate_agents_md.py` 6/0 |

**Comando de validación** (pytseguro: lotes pequeños, salida a archivo):
```bash
./venv/Scripts/python.exe -m pytest tests/common/test_service_identity_registry.py -v > temp/faseA_contract.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/quality_gates tests/asset_generation -q > temp/faseA_baseline.txt 2>&1
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/validate_agents_md.py
grep -rn "no_speakable\|no_llms_txt\|ia_crawler_blocked\|weak_brand_signals\|no_entity_schema\|no_factual_data" modules/commercial_documents modules/asset_generation || echo "OK: 0 IDs fantasma"
```

⚠️ **NUNCA** correr la suite `tests/commercial_documents` completa (fuga ~8GB). Usar lotes pequeños y
archivos específicos.

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE (antes de cerrar la sesión):

1. **`dependencias-fases.md`** — marcar FASE-A ✅, fecha, notas de ejecución
2. **`README.md` del plan** — tabla de progreso + métricas
3. **`06-checklist-implementacion.md`** — fila FASE-A, AC1/AC2/AC3, trazabilidad V2/V3/V14 y deuda P10
4. **`09-documentacion-post-proyecto.md`** (ACUMULATIVO — fuente de FASE-RELEASE)
   - Sección A: módulo nuevo (registro canónico)
   - Sección B: funcionalidad nueva (contract tests anti-drift)
   - Sección D: métricas acumulativas
   - Sección E: archivos afiliados actualizados
5. **`10-analisis-post-implementacion.md`** (ACUMULATIVO)
   - Resumen de Ejecución: fila FASE-A (estado, iteraciones, notas)
   - **Decisiones Arquitectónicas**: cuál registro manda + rationale + alternativas rechazadas (obligatorio en esta fase)
   - Lecciones Aprendidas: formato qué pasó / por qué / qué lo previene + pertinencia INCLUIR/EXCLUIR
   - Métricas de Ejecución: tests collected reales
   - Seguimientos abiertos
6. **`evidence/FASE-A/`** — `censo-registros.md` (salida de A1) + logs de tests

**Cierre con script** (anti-deuda §2.5 — NO diferir a RELEASE):
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-A --desc "Fuente unica de identidad servicio-asset-pain (V2/V3/V14)" --check-manual-docs
```
**SIN `--release`**: el bump de versión y el CHANGELOG son exclusivos de FASE-RELEASE.

**NO esperar a la siguiente sesión para documentar.**

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **Tests nuevos pasan**: contract tests del registro canónico en verde
- [ ] **TDD respetado**: los contract tests fueron escritos y vistos en rojo ANTES de la implementación
- [ ] **Baseline preservado**: 848 passed / 2 skipped (o delta explicado en `10-analisis`)
- [ ] **Validaciones del proyecto**: `run_all_validations.py --quick` 7/7 · `validate_agents_md.py` 6 PASS / 0 FAIL
- [ ] **AC1 cerrado**: registro canónico existe; 0 IDs fantasma verificado por grep
- [ ] **AC2 cerrado**: drift «8 vs 7» corregido en sus 3 copias + test que falla si reaparece
- [ ] **AC3 cerrado**: `monthly_report` resuelto a favor del canónico
- [ ] **`dependencias-fases.md` actualizado**
- [ ] **`06-checklist-implementacion.md` actualizado** (fila + ACs + trazabilidad)
- [ ] **`09-documentacion-post-proyecto.md` actualizado** (secciones A, B, D, E)
- [ ] **`10-analisis-post-implementacion.md` actualizado** (incl. Decisión Arquitectónica obligatoria)
- [ ] **Evidencia preservada**: `evidence/FASE-A/censo-registros.md`
- [ ] **`log_phase_completion.py` ejecutado SIN `--release`**
- [ ] **Commit hecho** con mensaje que referencia FASE-A

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

**Alcance — qué NO está en esta fase**:
- ❌ **NO tocar las rutas de skip silencioso** `proposal_asset_alignment.py:609-612` y `:792-794`
  (trampa A5) — pertenecen a FASE-C.
- ❌ **NO implementar la propuesta dinámica** (punto 8) — FASE-C.
- ❌ **NO tocar la biyección mapa↔emisión de `detect_pains`** (los 9 pains muertos de V1) — FASE-B.
- ❌ **NO agregar el 8º servicio** al registro (dossier §8.5). La unificación 7→8 **empeora**
  `coverage_ratio` (0.571 → 0.500) — medido.
- ❌ **NO tocar `publication_gates.py`** — FASE-D/F/G.
- ❌ **NO tocar `alignment_result.py`** — FASE-C/F.
- ❌ **NO tocar `VERSION.yaml`** — exclusivo de FASE-RELEASE.
- ❌ **NO crear tablas paralelas nuevas** de pain_id→texto (guardrail L-NC4).

**Restricciones técnicas**:
- Python del venv: `./venv/Scripts/python.exe` (no `python` del sistema)
- Pytest seguro: lotes pequeños, salida a archivo, nunca `tests/commercial_documents` completo
- En Git Bash usar rutas con slash (`/c/Users/...`); `sed` falla con rutas Windows — si hace falta
  edición scripted, usar `temp/*.py` con raw-strings
- Línea base: si aparecen tests rojos preexistentes, re-verificar que ya lo eran y **NO atribuirlos al
  plan**; registrarlos en `10-analisis` §Seguimientos abiertos

**Dependencia que no se puede modificar**: la forma pública de `AlignmentResult`
(`modules/quality_gates/alignment_result.py`) — FASE-SR-A fijó `compute_unresolved()` como único punto
de cómputo. Esta fase no la toca.

---

## Prompt de Ejecución

```
Actúa como arquitecto de software senior en el repo iah-cli (Python, Windows, venv en ./venv).

OBJETIVO: Construir UN registro canónico de identidad servicio↔asset↔pain del que deriven los ≥12
registros censados (9 del dossier + 3 del complemento de auditoría), con contract tests que fallen
fuerte ante drift.

CONTEXTO:
- Plan: .opencode/plans/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/
- Dossier fuente: .opencode/context/CONTEXT-AUDITORIA-BRECHAS-VS-MODULOS-SALENTOREAL-2026-09-03.md §12.3 (V2/V3/V14) y §12.5 Nivel 1.2
- Repo v4.74.1, master limpio. Python: ./venv/Scripts/python.exe
- Baseline de tests: 848 passed / 2 skipped en tests/quality_gates + tests/asset_generation
- Patrón a copiar: guardián AST de FASE-SR-A

TAREAS:
1. A1 Censo: inventariar los ≥12 registros por USO REAL (no por mención), confirmar/refutar los 6 IDs
   fantasma de V2, la perla monthly_report de V3 y las 3 copias del drift «8 vs 7» de V14. Decidir cuál
   registro manda. Salida: evidence/FASE-A/censo-registros.md
2. A2 Registro canónico + contract tests (TDD: tests en rojo ANTES). Guardián AST. Contrato
   narrativa↔fuente, no valores fijos. NO crear tablas paralelas (L-NC4).
3. A3 Migrar aguas arriba: conditional_generator.py:234-257/:314-326, pain_ledger.py:52-94,
   proposal_asset_alignment.py:22/:219/:993. Corregir 6 IDs fantasma + monthly_report.
4. A4 Migrar aguas abajo: v4_proposal_generator.py:1281-1289/:1332/:1365-1372,
   v4_diagnostic_generator.py:135-157/:160/:3067-3086, proposal_asset_alignment.py:35-37, service_catalog.

CRITERIOS:
- AC1: registro canónico único, 0 IDs fantasma (grep → 0)
- AC2: drift «8 vs 7» corregido en 3 copias + test que falla si reaparece
- AC3: ASSET_TO_PAIN_ID["monthly_report"] resuelto a favor del canónico
- Baseline 848/2 preservado; run_all_validations.py --quick 7/7; validate_agents_md.py 6/0

RESTRICCIONES (críticas):
- NO tocar proposal_asset_alignment.py:609-612 ni :792-794 (skip silencioso A5 → FASE-C)
- NO implementar propuesta dinámica (FASE-C) ni biyección detect_pains (FASE-B)
- NO agregar el 8º servicio; NO tocar publication_gates.py, alignment_result.py, VERSION.yaml
- Pytest en lotes pequeños con salida a archivo; NUNCA tests/commercial_documents completo (~8GB)

POST-EJECUCIÓN (obligatoria, no diferir):
Actualizar dependencias-fases.md, README.md, 06-checklist-implementacion.md,
09-documentacion-post-proyecto.md (A/B/D/E), 10-analisis-post-implementacion.md (incl. Decisión
Arquitectónica: cuál registro manda + alternativas rechazadas), evidence/FASE-A/.
Luego: log_phase_completion.py --fase FASE-A --desc "..." --check-manual-docs  (SIN --release).
Commit referenciando FASE-A.
```
