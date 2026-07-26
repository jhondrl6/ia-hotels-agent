# Prompt de Inicio de Sesión: FASE-2 — Persistir Commercial Gates + BLOCKED_BY_GATES

**Fase**: FASE-2 — FIX-PRIORITY-2: BUG-7 Persistir commercial gates + HALLAZGO-N5 BLOCKED_BY_GATES
**Plan**: DT-4-ROOT-CAUSE-2026-07-25
**Sesión**: Nueva (fresh)
**Iteraciones máx**: 60
**Complejidad**: MEDIA
**Ejecución**: **SUBAGENTE** ✅ — delegate_task viable (edits localizados en 2 archivos)
**Depende de**: FASE-0 ✅ (pain_ledger resuelto)
**Bloquea a**: FASE-RELEASE

---

## Objetivo

Hacer visibles los commercial gates que actualmente bloquean la propuesta sin dejar trace. Actualmente `CommercialGateBlockedError` aborta la generación sin persistir resultados, y `BLOCKED_BY_GATES.md` solo menciona publication gates (16 líneas). El fix persiste `commercial_gates_report.json` y amplía `BLOCKED_BY_GATES.md`.

---

## Contexto

3 commercial gates bloquean Zi One Luxury:
- CG-SCENARIO-ORDER: optimistic < realistic → BLOCKING
- CG-SCENARIO-NEGATIVE: optimistic < 0 → BLOCKING
- CG-ROI-NEGATIVE: CommercialGateBlockedError aborta propuesta

Ninguno de estos aparece en `gate_report.json` ni en `BLOCKED_BY_GATES.md`. La única evidencia es que `01_DIAGNOSTICO_*.md` y `02_PROPUESTA_*.md` no existen en disco.

---

## Tareas

### T1: Persistir `commercial_gates_report.json` antes del raise

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py` (L610)

Antes del `raise CommercialGateBlockedError`, persistir el reporte a disco:

```python
# En v4_proposal_generator.py, alrededor de L610:
# Antes:
raise CommercialGateBlockedError(
    [r.gate_id for r in commercial_report.blocking_failures],
    "Proposal commercial gates BLOCKING (hidden from client)",
)

# Después:
# Persist commercial gates report before raising
commercial_gates_path = (
    output_path / hotel_slug / "v4_audit" / "commercial_gates_report.json"
)
commercial_gates_path.parent.mkdir(parents=True, exist_ok=True)
commercial_gates_path.write_text(
    json.dumps(commercial_report.to_dict(), indent=2, ensure_ascii=False),
    encoding="utf-8",
)
logger.info(f"Commercial gates report persisted to {commercial_gates_path}")

raise CommercialGateBlockedError(
    [r.gate_id for r in commercial_report.blocking_failures],
    "Proposal commercial gates BLOCKING — see commercial_gates_report.json for details",
)
```

**Nota**: `commercial_report.to_dict()` ya existe en `commercial_gate.py:56-62` (`CommercialGateReport.to_dict()`). Usar ese método.

### T2: Ampliar `BLOCKED_BY_GATES.md` para incluir commercial gates

**Archivo**: `main.py` — donde se genera `BLOCKED_BY_GATES.md`

Agregar una sección "🚨 Commercial Gates Bloqueantes" cuando exista `commercial_gates_report.json` con `blocking_passed: false`:

```python
# En la generación de BLOCKED_BY_GATES.md (main.py, bloque que escribe el .md):

# Después de escribir la sección de publication gates, agregar:
commercial_gates_path = (
    output_base / hotel_slug / "v4_audit" / "commercial_gates_report.json"
)
if commercial_gates_path.exists():
    with open(commercial_gates_path, "r", encoding="utf-8") as f:
        commercial_data = json.load(f)

    if not commercial_data.get("blocking_passed", True):
        md_lines.append("\n## 🚨 Commercial Gates Bloqueantes\n")
        md_lines.append(
            "Los siguientes gates comerciales impidieron la generación "
            "de la propuesta. **No vuelva a ejecutar sin resolverlos** — "
            "la re-ejecución idéntica fallará igual.\n\n"
        )

        for result in commercial_data.get("results", []):
            if not result.get("passed", True):
                md_lines.append(f"- **{result['gate_id']}**: {result.get('message', 'Sin detalle')}\n")

        md_lines.append(
            "\n> ⚠️ Estos gates evalúan la viabilidad comercial de la propuesta. "
            "Resuélvalos antes de re-ejecutar `v4complete`.\n"
        )
```

**Remover** la línea de "vuelva a ejecutar" si hay commercial gates bloqueantes (HALLAZGO-N5).

### T3: Test + verificación

1. Agregar test unitario verificando que `commercial_gates_report.json` se escribe cuando `CommercialGateBlockedError` se lanza
2. Agregar test verificando que `BLOCKED_BY_GATES.md` incluye sección de commercial gates
3. Ejecutar tests:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/ -v -k "commercial_gate"
./venv/Scripts/python.exe -m pytest -q
```

---

## Criterios de Completitud

- [ ] `commercial_gates_report.json` se persiste antes del raise en `v4_proposal_generator.py`
- [ ] `BLOCKED_BY_GATES.md` incluye sección "🚨 Commercial Gates Bloqueantes"
- [ ] No se sugiere "vuelva a ejecutar" si hay commercial gates bloqueantes
- [ ] Tests nuevos cubren el path de persistencia
- [ ] 100 tests existentes + nuevos siguen PASS
- [ ] git commit con mensaje descriptivo

---

## delegate_task Prompt (para subagente)

```
Implement FASE-2 of DT-4 plan for iah-cli project at /mnt/c/Users/Jhond/Github/iah-cli.

GOAL: Fix BUG-7 — make commercial gates visible by persisting their report and expanding BLOCKED_BY_GATES.md.

CONTEXT:
3 commercial gates block Zi One Luxury's proposal generation but leave no trace:
- CommercialGateBlockedError is raised at v4_proposal_generator.py ~L610 but no JSON is persisted
- BLOCKED_BY_GATES.md only mentions publication gates (16 lines, only coverage)
- The file suggests "re-run v4complete" which would fail identically

TASKS:
T1 — Persist commercial_gates_report.json before raising CommercialGateBlockedError:
  1. Read modules/commercial_documents/v4_proposal_generator.py around L610 (grep for CommercialGateBlockedError)
  2. Before the raise, persist commercial_report.to_dict() to {output_path}/{hotel_slug}/v4_audit/commercial_gates_report.json
  3. Use commercial_report.to_dict() (already exists in CommercialGateReport class)
  4. Update the error message to reference the persisted file

T2 — Expand BLOCKED_BY_GATES.md generation in main.py:
  1. Grep main.py for where BLOCKED_BY_GATES.md is written
  2. Add section "Commercial Gates Bloqueantes" when commercial_gates_report.json exists with blocking_passed=false
  3. Remove/change the "re-run v4complete" suggestion when commercial gates are blocking

T3 — Tests:
  1. Add test verifying commercial_gates_report.json is persisted on CommercialGateBlockedError
  2. Add test verifying BLOCKED_BY_GATES.md includes commercial gates section
  3. Run: ./venv/Scripts/python.exe -m pytest -q
  4. git add + commit

RESTRICTIONS:
- Do NOT modify commercial_gate.py (the gate logic itself is fine)
- Do NOT modify scenario_calculator.py
- Keep existing tests passing
```

---

## Post-Ejecución (OBLIGATORIO)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-2 --desc "BUG-7_persistir_commercial_gates_BLOCKED_BY_GATES_N5" --check-manual-docs
```

---

## Siguiente Sesión

**FASE-3** — BUG-10: Decisión de producto monthly_report (o FASE-4 si se prefiere orden independiente)
