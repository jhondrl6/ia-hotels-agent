# DT-2 — Delivery Contract Residual Fixes (Post-DT-1)

> **Plan ID**: DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24
> **Origen**: Evaluación post-DT-1 (sesión 2026-07-24)
> **Versión base**: v4.63.1 (Delivery-Contract, commit acf943b)
> **Versión objetivo**: v4.63.2
> **Hotel de referencia**: Zi One Luxury (https://zione.co/)
> **Datos reales**: `output/clientes/zi-one-luxury_onboarding.yaml`
> **Severidad**: MEDIA-ALTA — no bloquea entrega, pero el "4/4 gates PASS" es factualmente incorrecto
> **Fecha**: 2026-07-24
> **Contexto fuente**: `.opencode/context/CONTEXT-DT-2-DELIVERY-CONTRACT-RESIDUAL.md`

---

## 1. Resumen Ejecutivo

DT-1 implementó el delivery contract (DeliveryAssetState, DeliveryAssetEntry,
DeliveryContext, packager dinámico, 28 tests). La evaluación post-DT-1
identificó 7 findings residuales (P-01 a P-07) agrupados en 3 raíces:

- **RAÍZ-1**: Orden de construcción — README se renderiza antes del manifest
- **RAÍZ-2**: Filtros sin contrato de exclusión mutua — advisory aparece en múltiples secciones
- **RAÍZ-3**: Gates declarados pero no implementados — G9 dead gate + score pre-gen

El plan corrige los 7 findings en 6 fases de código + 1 fase de v4complete + 1 fase RELEASE.

**Calificación DT-1**: 7.5/10 — los componentes son sólidos, el gap a 10/10 son estos 4-7 fixes.

---

## 2. Findings (7 total: 4 originales + 3 nuevos de auditoría)

| ID | Título | Severidad | Raíz | Archivo principal | Fase |
|----|-------|-----------|------|-------------------|------|
| P-01 | Conteo 44 vs 46 en README Overview | BAJA | RAÍZ-1 | delivery_packager.py L450 | A |
| P-07 | Comparación string vs enum en filtro | BAJA | RAÍZ-2 | delivery_packager.py L603 | A |
| P-02 | Assets advisory en múltiples secciones README | MEDIA | RAÍZ-2 | delivery_context.py L407-425 | B |
| P-03 | Quality report usa score pre-generación | MEDIA | RAÍZ-3 | delivery_quality_report.py L122 | C |
| P-05 | G9 proposal_asset_gate es dead gate | ALTA | RAÍZ-3 | delivery_quality_report.py L238 | C |
| P-04 | proposal_asset_matrix diverge + no empaquetado | MEDIA | RAÍZ-2+3 | proposal_asset_alignment.py L562 | D |
| P-06 | proposal_asset_matrix.json no se empaqueta | MEDIA | RAÍZ-2 | delivery_packager.py _collect_files | D |

---

## 3. Causas Raíz Consolidadas

### RAÍZ-1: Orden de construcción (P-01)
El README se renderiza en Pass 1 (L175) ANTES de que el manifest exista (Pass 2-3).
El README consume `delivery_context.files` (pre-meta, 44 archivos) mientras el manifest
refleja el estado final (46 archivos). La información correcta existe pero en orden equivocado.

### RAÍZ-2: Filtros sin contrato de exclusión mutua (P-02, P-06, P-07)
Cada sección del README tiene su propio filtro independiente:
- `delivered_assets`: `state == DELIVERED` (no excluye advisory)
- `estimated_assets`: `state == ESTIMATED` (no excluye advisory)
- `advisory_assets`: `is_advisory == True` (no excluye por state)

Ninguno excluye lo que el otro captura. `is_advisory` corta horizontalmente los estados.

### RAÍZ-3: Gates declarados pero no implementados (P-03, P-05)
El `delivery_quality_report` tiene 4 gates (G6, G7, G8, G9):
- G6 (coherence): IMPLEMENTADO — lee `coherence_validation.json` (pre-gen)
- G7 (coverage): IMPLEMENTADO — lee `asset_generation_report.json`
- G8 (specificity): IMPLEMENTADO — lee `asset_generation_report.json`
- G9 (proposal_asset_alignment): NO IMPLEMENTADO — default `True` hardcodeado

G9 está declarado en el dataclass, en el JSON, y en la lógica de bloqueo (L205),
pero nunca se evalúa. Además, G6 lee el score PRE-generación cuando existe POST-generación.

---

## 4. Fases del Plan

| Fase | Título | Findings | Tipo | Ejecución | R3 (tareas + cmd largo) |
|------|--------|----------|------|-----------|-------------------------|
| A | Conteo README + string-vs-enum | P-01, P-07 | CODE FIX | SUBAGENTE | 3 + 0 |
| B | Exclusión mutua advisory sections | P-02 | CODE FIX | SUBAGENTE | 3 + 0 |
| C | Quality report post-gen + G9 dead gate | P-03, P-05 | CODE FIX | DIRECTA | 3 + 0 |
| D | proposal_asset_matrix path + packaging | P-04, P-06 | CODE FIX | DIRECTA | 3 + 0 |
| E | Tests nuevos P-01..P-07 | 7 fixes | TESTS | DIRECTA | 4 + 0 |
| F | v4complete Zi One + análisis post-impl | S-1..S-9 | E2E + ANALYSIS | MIXTO | 2 + 1 |
| RELEASE | Version bump + docs cascade | — | RELEASE | SUBAGENTE | 3 + 0 |

**Total**: 7 fases, 7 sesiones.

### Fase de mayor complejidad técnica: FASE-C

**Por qué**: P-05 (G9 dead gate) es el finding de severidad ALTA. Requiere:
1. Decidir si implementar G9 (evaluar alineación real) o eliminarlo del reporte
2. Si se implementa, debe consumir `ProposalAssetMatrix` o `AlignmentReport` —
   lo que acopla `delivery_quality_report.py` con `proposal_asset_alignment.py`
3. P-03 requiere lógica de fallback: leer `coherence_validation_post_gen.json`
   cuando exista, con fallback a `coherence_validation.json`
4. Ambos fixes están en el mismo archivo (`delivery_quality_report.py`)
5. El impacto del G9 es que el quality report puede dar "PASS" con "4/4 gates"
   aunque la alineación propuesta→asset esté rota

**Mitigaciones**:
- Decisión documentada: implementar G9 (opción 1 del contexto) por valor a largo plazo
- Si la implementación de G9 resulta demasiado compleja para la fase, fallback
  a eliminación del gate (opción 2) como deuda técnica documentada
- Tests de contrato en FASE-E validan que G9 se evalúa realmente

---

## 5. Dependencias entre Fases

```
FASE-A (P-01, P-07) ─┐
FASE-B (P-02)       ─┼─→ FASE-E (Tests) ─→ FASE-F (v4complete) ─→ FASE-RELEASE
FASE-C (P-03, P-05) ─┤
FASE-D (P-04, P-06) ─┘
```

- FASE-A, B, C, D son independientes entre sí (modifican archivos distintos)
- FASE-E depende de A-D (testea los fixes)
- FASE-F depende de E (verifica con v4complete que los fixes funcionan end-to-end)
- FASE-RELEASE depende de F (version bump + changelog con resultados)

### Tabla de conflictos de archivos

| Archivo | Fase(s) que lo modifican | Conflicto |
|---------|--------------------------|-----------|
| delivery_packager.py | A (L450, L603), B (L603), D (_collect_files) | A+B comparten L603 — B va después de A |
| delivery_context.py | B (L407-425) | Sin conflicto |
| delivery_quality_report.py | C (L122, L238) | Sin conflicto |
| proposal_asset_alignment.py | D (L562) | Sin conflicto |
| v4_proposal_generator.py | D (L642) | Sin conflicto |
| test_delivery_contract.py | E | Sin conflicto |

**Resolución**: FASE-A va primero (modifica L603 con fix P-07). FASE-B va después
y se beneficia del fix de P-07 (L603 ya usa enum). D modifica `_collect_files` que
no toca A ni B. Orden de ejecución: A → B → C → D → E → F → RELEASE.

---

## 6. Matriz de Viabilidad delegate_task

| Fase | ¿Viable delegate_task? | Razón |
|------|------------------------|-------|
| A | SI (SUBAGENTE) | 2 fixes localizados en 1 archivo, sin imports de proyecto |
| B | SI (SUBAGENTE) | 1 fix en delivery_context.py, mechanical |
| C | NO (DIRECTA) | P-05 requiere decisión arquitectónica (implementar vs eliminar G9). Acoplamiento entre módulos. Riesgo ALTO. |
| D | NO (DIRECTA) | P-04 requiere tracing de path mismatch entre 3 archivos. Acoplamiento proposal_asset_alignment ↔ delivery_packager. |
| E | NO (DIRECTA) | Tests requieren imports del proyecto → WSL import cascade. Usar subprocess con venv/Scripts/python.exe |
| F | MIXTO | v4complete via delegate_task (timeout 900s) + análisis post-impl directo (main agent tiene contexto completo) |
| RELEASE | SI (SUBAGENTE) | Solo edita YAML/MD, corre scripts. 18 tool calls típico. |

---

## 7. Criterios de Éxito (DoD)

| # | Criterio | Verificable en | Fase |
|---|----------|----------------|------|
| S-1 | README Overview muestra conteo y tamaño que coinciden con MANIFEST.json | ZIP → README_DELIVERY.md | F |
| S-2 | Ningún asset aparece en sección state-based Y "Advisory Guides" simultáneamente | ZIP → README_DELIVERY.md | F |
| S-3 | delivery_quality_report refleja score post-generación (o ambos scores) | output/v4_complete/zione/v4_audit/ | F |
| S-4 | proposal_asset_matrix usa DeliveryContext como fuente de verdad o alinea con gate | output/v4_complete/ | F |
| S-5 | Tests existentes (28) siguen pasando | test_delivery_contract.py | E |
| S-6 | Tests nuevos cubren los 7 fixes (P-01 a P-07) | test_delivery_contract.py | E |
| S-7 | ZIP de Zi One post-fix cumple S-1 y S-2 | zione_YYYYMMDD.zip | F |
| S-8 | G9 proposal_asset_alignment se evalúa realmente o se elimina del reporte | delivery_quality_report.json | C, F |
| S-9 | proposal_asset_matrix.json empaquetado en el ZIP | zione_YYYYMMDD.zip | D, F |

---

## 8. Restricciones

1. **No tocar el pipeline de producción**: SitePresenceChecker, CoherenceValidator,
   scenario_calculator.py están fuera de alcance.
2. **No romper backward compatibility**: `create_readme()` debe seguir funcionando
   sin DeliveryContext (legacy mode).
3. **Safety guard WSL**: No usar `rm -rf` directamente. Ver skill `wsl-safety-guard-bypass`.
4. **Una fase = una sesión**: Cada fase se ejecuta en una sesión independiente.
5. **Output path**: v4complete escribe a `output/v4_complete/` (flat), no a
   `output/<hotel_id>/v4_complete/`.
6. **pytest no disponible en .venv-wsl**: Usar `venv/Scripts/python.exe -m pytest`
   (Windows venv) o instalar pytest antes de correr tests.
7. **v4complete CLI syntax**: `venv/Scripts/python.exe main.py v4complete --url https://zione.co/`
   (no --timeout como arg CLI; el timeout es del terminal).

---

## 9. Análisis de Complejidad por Fase

| Fase | Complejidad | Factores de riesgo | Mitigación |
|------|-------------|-------------------|------------|
| A | BAJO | 2 fixes localizados, mechanical | Subagent con contexto del código actual |
| B | MEDIO | Filtros con exclusión mutua pueden romper tests existentes | Subagent + verificar 28 tests tras fix |
| C | ALTO | G9 dead gate — decisión arquitectónica + acoplamiento | Directa, agente principal decide, fallback a eliminación |
| D | MEDIO | Path mismatch entre 3 archivos, tracing de rutas | Directa, agente principal traza paths |
| E | MEDIO | 7 tests nuevos, WSL import cascade para pytest | Directa con subprocess, no importar módulos |
| F | MEDIO | v4complete 5-10 min + análisis de 9 criterios | MIXTO: subagent para v4complete, main agent analiza |
| RELEASE | BAJO | YAML/MD edits, scripts de validación | Subagent, ~18 tool calls |

---

## 10. Presupuesto de Iteraciones por Fase

| Fase | Costos fijos | Trabajo específico | Total estimado |
|------|-------------|-------------------|----------------|
| A | ~26 | ~10 (2 fixes + verify) | ~36 |
| B | ~26 | ~12 (1 fix + verify 28 tests) | ~38 |
| C | ~26 | ~18 (decisión G9 + 2 fixes + verify) | ~44 |
| D | ~26 | ~14 (path tracing + 2 fixes + verify) | ~40 |
| E | ~26 | ~20 (7 tests + run suite) | ~46 |
| F | ~26 | ~20 (v4complete + análisis) | ~46 |
| RELEASE | ~26 | ~10 (version + changelog + sync) | ~36 |

---

## 11. Post-Implementación (FASE-F)

El análisis post-implementación (08-analisis-post-implementacion.md) incluirá:

- Tabla de ejecución por fase (sesión, iteraciones, status, delegate_task usado)
- Análisis de la fase de mayor complejidad (FASE-C) — por qué, mitigaciones aplicadas
- Matriz de viabilidad delegate_task por fase (viable? por qué?)
- Tabla de riesgos (riesgo, probabilidad, impacto, mitigación)
- Matriz de verificación de los 7 fixes contra v4complete output
- Lecciones aprendidas (completar post-implementación)

### Matriz de verificación post-v4complete

| Finding | Verificación | Archivo de salida |
|---------|-------------|-------------------|
| P-01 | README `Contents:` == MANIFEST `total_files` | README_DELIVERY.md, MANIFEST.json |
| P-02 | 0 assets aparecen en 2 secciones simultáneamente | README_DELIVERY.md |
| P-03 | `coherence_score` == post-gen (o ambos reportados) | delivery_quality_report.json |
| P-04 | proposal_asset_matrix alineado con DeliveryContext | proposal_asset_matrix.json |
| P-05 | G9 muestra `passed: <bool>` con valor real (no default True) | delivery_quality_report.json |
| P-06 | `proposal_asset_matrix.json` aparece en ZIP entries | MANIFEST.json |
| P-07 | L603 usa `DeliveryAssetState.DELIVERED` (no string) | delivery_packager.py |

---

## 12. Estructura de Archivos del Plan

```
.opencode/plans/DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24/
├── README.md                           # Este índice
├── 01-plan-maestro.md                  # Plan maestro (este archivo)
├── 02-prompt-fase-A.md                 # P-01 + P-07: conteo README + string vs enum
├── 03-prompt-fase-B.md                 # P-02: exclusión mutua advisory
├── 04-prompt-fase-C.md                 # P-03 + P-05: quality report post-gen + G9 dead gate
├── 05-prompt-fase-D.md                 # P-04 + P-06: proposal_asset_matrix path + packaging
├── 06-prompt-fase-E.md                 # Tests nuevos P-01..P-07
├── 07-prompt-fase-F.md                 # v4complete Zi One + análisis post-implementación
├── 08-prompt-fase-release.md           # RELEASE v4.63.2
├── 09-checklist-implementacion.md     # Checklist maestro
└── 10-analisis-post-implementacion.md  # Template de retrospectiva
```
