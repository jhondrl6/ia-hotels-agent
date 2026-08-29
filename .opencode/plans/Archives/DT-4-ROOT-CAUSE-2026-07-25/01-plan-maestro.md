# Plan Maestro: DT-4 — Root Cause Reconciliation Post-DT-3

> **Origen**: CONTEXT-DT-4.md (validado contra código vivo 2026-07-25)
> **Versión objetivo**: v4.65.0
> **Versión actual**: v4.64.0 (tag dc303e5)
> **Hotel de referencia**: Zi One Luxury (https://zione.co/)
> **Sesiones estimadas**: 5 fases + RELEASE = 6 sesiones
> **Estimación total**: ~7-9h

---

## Resumen Ejecutivo

Post-DT-3, el delivery pipeline de iah-cli tiene 4 bugs reales (2 CRÍTICOS, 2 MEDIOS) + 5 hallazgos amplificadores (N1-N5) con una causa raíz transversal: **3 fuentes de verdad no consolidadas** para "este pain está resuelto?":

1. `pain_ledger[]` (status: DETECTED/DIAGNOSED/MAPPED_TO_SERVICE/ASSET_GENERATED/...)
2. `proposal_asset_matrix.json` (status: LINKED/MISSING_ASSET/NO_BREACH/...)
3. `skipped_assets[]` (presence_status: exists/redundant/...)

Ningún punto central reconcilia estas 3 fuentes después de la orquestación de assets. Publication G9 reconcilia 1+3 parcialmente; coverage G11 solo lee 1; delivery quality G9 lee 2 sin enriquecer. Resultado: falsos positivos en coverage (BUG-6), divergencia G9 (BUG-9), commercial gates invisibles (BUG-7).

Este plan ejecuta 5 fases + RELEASE, priorizando el **reconciliador post-orchestrator** (FIX-PRIORITY-1) que resuelve 4 issues de un solo fix.

---

## Bugs y Hallazgos

### Bugs (4)

| ID | Severidad | Descripción | FIX-PRIORITY | Fase |
|----|-----------|-------------|-------------|------|
| BUG-6 | **CRÍTICO** | Coverage gate: falso positivo `no_whatsapp_visible` | 1 | FASE-0 |
| BUG-7 | **CRÍTICO** | Commercial gates ocultos: 3 gates bloquean sin trace | 2 | FASE-2 |
| BUG-8 | MEDIO | Escenario optimista negativo (interpretación comercial) | 3 | FASE-1 |
| BUG-9 | MEDIO | Divergencia publication G9 vs delivery quality G9 | 1 | FASE-0 |

### Hallazgos Amplificadores (5)

| ID | Descripción | FIX-PRIORITY | Fase |
|----|-------------|-------------|------|
| N1 | Dos gates "coverage" con mismo nombre, diferente contrato | 5 | FASE-4 |
| N2 | `ASSET_GENERATED` falta en `_JUSTIFIED_STATUSES` | 1 | FASE-0 |
| N3 | `whatsapp_conflict` cubierto pero `no_whatsapp_visible` no | 1 | FASE-0 |
| N4 | Coherence check `whatsapp_verified` con score 0.3 (ignora SitePresence) | 1 | FASE-0 |
| N5 | `BLOCKED_BY_GATES.md` instruye re-ejecución idéntica sin mencionar commercial gates | 2 | FASE-2 |

### Causa Raíz Transversal

Los 4 bugs + 4 de 5 hallazgos son **síntomas** de un problema único: 3 sistemas que evalúan independientemente si un pain está resuelto, sin reconciliación post-orquestador. El reconciliador (FIX-PRIORITY-1) los resuelve juntos.

---

## Fases del Plan

| Fase | Título | Complejidad | delegate_task | Tareas | Comando largo | R3 |
|------|--------|-------------|---------------|--------|---------------|-----|
| **FASE-0** | Reconciliador post-orchestrator (causa raíz) | **ALTA** ⚠️ | ❌ NO VIABLE | 4 | No | ✅ |
| **FASE-1** | Reinterpretación comercial del optimista (BUG-8) | BAJA | ✅ VIABLE | 3 | No | ✅ |
| **FASE-2** | Persistir commercial gates + BLOCKED_BY_GATES (BUG-7) | MEDIA | ✅ VIABLE | 3 | No | ✅ |
| **FASE-3** | Decisión producto monthly_report (BUG-10) | BAJA | ✅ VIABLE | 2 | No | ✅ |
| **FASE-4** | Higiene nombres gates duplicados (N1) | BAJA | ✅ VIABLE | 2 | No | ✅ |
| **FASE-RELEASE** | v4complete Zi One + version bump + análisis post-implementación | MEDIA | ⚠️ MIXTO | 3 | v4complete (1) | ✅ |

---

## Fase de Mayor Complejidad Técnica: FASE-0

**FASE-0 (Reconciliador post-orchestrator)** es la fase de mayor complejidad por:

1. **Nuevo módulo**: Crear `modules/orchestration/post_orchestrator_reconciler.py` — ~80 líneas de lógica de reconciliación que lee 3 fuentes de datos y emite estado consolidado
2. **Cross-module**: Afecta 5 archivos: v4_asset_orchestrator.py, publication_gates.py, delivery_quality_report.py, coherence_validator.py, proposal_asset_alignment.py
3. **Decisión arquitectónica**: Elegir entre "pain_ledger como fuente única" vs "nuevo archivo pain_ledger_resolved.json" — afecta a todos los consumidores downstream
4. **Riesgo de regresión**: 100 tests existentes (86 base + 14 DT-3); coverage gate es blocking — un falso negativo bloquearía delivery
5. **No delegable**: Requiere agente principal para la decisión arquitectónica y el diseño del contrato de reconciliación

**Mitigaciones**:
- Tests existentes como red de seguridad (100/100 PASS)
- Diseño de contrato ya especificado en CONTEXT-DT-4.md §9 (FIX-PRIORITY-1)
- v4complete en FASE-RELEASE como verificación E2E

---

## delegate_task Viability Matrix

| Fase | ¿Viable? | Razón | Riesgo |
|------|----------|-------|--------|
| FASE-0 | ❌ **NO VIABLE** | Cross-module, nuevo archivo + 4 modificaciones. Decisión arquitectónica (reconciliador vs fuente única). >20 líneas | Subagente no tiene contexto de las 3 fuentes de verdad ni del contrato de reconciliación |
| FASE-1 | ✅ **VIABLE** | 2 funciones en 1 archivo. No ejecuta imports del proyecto. Lógica de reinterpretación ya especificada (Opción B) | WSL venv no requerido |
| FASE-2 | ✅ **VIABLE** | ~30 líneas en 2 archivos. Edits localizados. Sin imports del proyecto | WSL venv no requerido |
| FASE-3 | ✅ **VIABLE** | 1 línea o enum addition. Decisión de producto ya documentada | Sin riesgo técnico |
| FASE-4 | ✅ **VIABLE** | Rename en 1 archivo + grep para referencias. Sin imports | grep puede fallar en WSL CRLF |
| FASE-RELEASE | ⚠️ **MIXTO** | v4complete → delegate_task (comando largo). Análisis post-implementación → DIRECTO (requiere contexto completo) | Timeout 900s; ver patrón MIXTO |

---

## Criterios de Éxito (DoD)

| # | Criterio | Fase que lo cubre | Verificable en |
|---|----------|-------------------|----------------|
| S-1 | Reconciliador creado y cableado en orchestrator | FASE-0 | `modules/orchestration/post_orchestrator_reconciler.py` + `v4_asset_orchestrator.py` |
| S-2 | `ASSET_GENERATED` en `_JUSTIFIED_STATUSES` | FASE-0 | `publication_gates.py:1186` |
| S-3 | Coverage gate lee `pain_ledger_resolved` con fallback | FASE-0 | `publication_gates.py:_coverage_gate` |
| S-4 | Coherence `whatsapp_verified` consulta SitePresence | FASE-0 | `coherence_validator.py:_check_whatsapp_verified` |
| S-5 | `pain_ledger_resolved.json` existe post-v4complete | FASE-RELEASE | `output/clientes/v4_complete/zione/v4_audit/` |
| S-6 | Optimista negativo → WARNING, no BLOCKING | FASE-1 | `commercial_gates_report.json §results` |
| S-7 | `commercial_gates_report.json` existe en v4_audit | FASE-2 | `output/clientes/v4_complete/zione/v4_audit/` |
| S-8 | `BLOCKED_BY_GATES.md` menciona commercial gates | FASE-2 | `BLOCKED_BY_GATES.md` |
| S-9 | `monthly_report` excluido de alignment counts | FASE-3 | `proposal_asset_matrix.json §entries` |
| S-10 | Gates renombrados sin regresión | FASE-4 | `gate_report_*.json §gate_name` |
| S-11 | v4complete Zi One: coverage gate PASS | FASE-RELEASE | `gate_report_*.json §coverage` |
| S-12 | 100 tests existentes + N nuevos siguen PASS | Todas | `pytest --collect-only -q` |
| S-13 | Pre-commit hooks limpios | FASE-RELEASE | `version_consistency_checker.py` |

---

## Orden de Ejecución

```
FASE-0 (Reconciliador) ── causa raíz, resuelve BUG-6 + BUG-9 + N2 + N3 + N4
  │
  ├──▶ FASE-1 (BUG-8: optimista) ── independiente
  │
  ├──▶ FASE-2 (BUG-7: commercial gates) ── requiere FASE-0 para tener pain_ledger_resolved
  │
  ├──▶ FASE-3 (BUG-10: monthly_report) ── independiente, último
  │
  ├──▶ FASE-4 (N1: gate names) ── independiente, último
  │
  └──▶ FASE-RELEASE (v4complete + version bump) ── requiere TODAS las fases
```

FASE-1, FASE-3 y FASE-4 son independientes entre sí pero todas dependen de FASE-0. FASE-2 requiere FASE-0 para tener el pain_ledger resuelto (los commercial gates dependen indirectamente del estado de pains). FASE-RELEASE es la última.

---

## Archivos del Plan

```
/.opencode/plans/Archives/DT-4-ROOT-CAUSE-2026-07-25/
├── 01-plan-maestro.md                   ← Este archivo
├── 02-prompt-fase-0.md                  ← FIX-PRIORITY-1: Reconciliador post-orchestrator
├── 03-prompt-fase-1.md                  ← FIX-PRIORITY-3: BUG-8 optimista
├── 04-prompt-fase-2.md                  ← FIX-PRIORITY-2: BUG-7 commercial gates
├── 05-prompt-fase-3.md                  ← FIX-PRIORITY-4: BUG-10 monthly_report
├── 06-prompt-fase-4.md                  ← FIX-PRIORITY-5: N1 gate names
├── 07-prompt-fase-release.md            ← v4complete + version bump + análisis
├── 08-checklist-implementacion.md       ← Master tracker
├── 09-analisis-post-implementacion.md   ← Template (completar post-ejecución)
└── dependencias-fases.md                ← Dependency graph + file conflict matrix
```

---

## Restricciones Globales

1. Una fase = una sesión — no ejecutar múltiples fases en la misma sesión
2. pytest: `./venv/Scripts/python.exe -m pytest` (Windows venv desde WSL)
3. v4complete: `./venv/Scripts/python.exe main.py v4complete --url https://zione.co/ --output output/clientes`
4. Pre-commit: `version_consistency_checker.py` (BLOCKING) + `sync_versions.py --check` (advisory)
5. NO modificar `PAIN_SOLUTION_MAP` sin N≥5 observaciones
6. NO modificar `scenario_calculator.py` sin N≥5 observaciones (BUG-8 Opción B no toca la fórmula, solo interpretación)
7. WSL safety guard: evitar `rm -rf`, pipes con heredocs. Usar `write_file` para crear inputs
8. NO declarar coverage FAIL como "legítimo" sin verificar `asset_generation_report.json §skipped_assets`
9. delegate_task: viable para ediciones ≤20 líneas en un solo archivo. NO para decisiones cross-module

---

## Lecciones de DT-2 y DT-3 incorporadas

| Lección | Aplicación en DT-4 |
|---------|-------------------|
| Verificar contra `asset_generation_report.skipped_assets` antes de declarar coverage FAIL legítimo | Restricción #8 + criterio S-5 |
| Si se toca un contrato, verificar TODOS los consumidores con `grep -rn` | FASE-0 verifica todos los consumidores de pain_ledger |
| Todo fix debe verificarse con v4complete real, no solo tests | FASE-RELEASE incluye v4complete para Zi One |
| README test count stale → `pytest --collect-only -q \| tail -1` como paso de release | FASE-RELEASE incluye auditoría numérica |
| No delegar decisiones arquitectónicas | FASE-0 es DIRECTA |
| No ejecutar múltiples fases en la misma sesión | Restricción #1 |
