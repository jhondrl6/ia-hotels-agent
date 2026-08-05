# FASE-D — RC2-b: Política de Entrega ZIP (N16/N21) + Loader Onboarding (S7) + Occupancy Label (S5)

**ID**: RC1-RC2-ENTREGA-COHERENTE-2026-08-04 / FASE-D
**Objetivo**: Que el ZIP de entrega al cliente no transporte evidencia interna BLOCKING ni artefactos de runs anteriores; que el loader de onboarding tenga fallback a `output/clientes`; y que el label de fuente de occupancy sea veraz en el breakdown.
**Dependencias**: FASE-C ✅ (verificar en dependencias-fases.md; si no ✅, ABORTAR)
**Duración estimada**: 1.5-2.5 horas
**Skill**: `.agents/workflows/phased_project_executor.md`
**Modo de ejecución**: ✅ **DELEGABLE vía `delegate_task`** — 3 tracks INDEPENDIENTES (archivos distintos, sin intersección).

---

## Contexto

| Hallazgo/Seguimiento | Problema |
|----------------------|----------|
| **N16 (MEDIA)** | `zione_20260804.zip` incluye `commercial_gates_report_diagnostic_*.json` (all_passed=false, BLOCKING) junto al diagnóstico con frontmatter `gate_status: PASSED` — evidencia interna contradictoria viaja al cliente |
| **N21 (INFO)** | El ZIP contiene artefactos de AMBOS runs del día (123637 y 124443): el freshness cutoff de 24h (`delivery_packager.py` L286-304) no distingue runs |
| **S7 (MEDIA)** | Loader de onboarding (`main.py` L1746 `clientes_dir = Path(args.output)/"clientes"`) no tiene fallback a `output/clientes` con `--output` alternativo → "Using defaults" (lección L13) |
| **S5 (MEDIA)** | `financial_scenarios.json` → `breakdown.data_sources.occupancy = "regional"` residual aunque el dato viene de onboarding (D12: el gate_report sí dice "onboarding") |

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A / B / C | ✅ Completadas (verificar antes de empezar) |

---

## Delegación (delegate_task)

Las 3 tracks son independientes (overlap de archivos = 0). El agente principal orquesta y
usa su presupuesto para integración + docs:

```
delegate_task(
  goal="FASE-D Track 1: política ZIP de entrega (N16/N21)...",
  context="Archivos: modules/delivery/delivery_packager.py ...",
  timeout=600, notify_on_complete=True
)
delegate_task(
  goal="FASE-D Track 2: fallback loader onboarding (S7)...",
  context="Archivo: main.py (_load_latest_onboarding_data) ...",
  timeout=600, notify_on_complete=True
)
delegate_task(
  goal="FASE-D Track 3: label occupancy en breakdown (S5)...",
  context="Archivo: modules/financial_engine/... ...",
  timeout=600, notify_on_complete=True
)
```

> ⚠️ **Fallback obligatorio**: si los subagentes NO pueden ejecutar los tests del
> proyecto (imports del venv, lección FASE-4 BUGS-ONBOARDING-ADR), el agente principal
> ejecuta las 3 tracks DIRECTAMENTE en orden T1→T2→T3. La regla de venv PREVALECE.

---

## Tareas

### T1 (Track 1): R2.3 — Política de entrega del ZIP (N16 + N21)
**Archivo**: `modules/delivery/delivery_packager.py`

1. Excluir `commercial_gates_report*` del ZIP cuando `document_audience=client`
   (reports internos de gates no viajan al cliente).
2. Filtrar artefactos por RUN: usar el timestamp del run de referencia (el más reciente
   del directorio v4_audit) como cutoff adicional al de 24h, para que evidencia de runs
   anteriores del mismo día NO viaje en el ZIP.
3. Tests: ZIP resultante sin `commercial_gates_report*` y sin duplicados por run.

### T2 (Track 2): S7 — Fallback del loader de onboarding
**Archivo**: `main.py` (`_load_latest_onboarding_data`, zona L1746)

1. Si `{--output}/clientes` no existe o está vacío → fallback a `output/clientes`
   (ruta por defecto), registrando la ruta finalmente usada en el log.
2. Mantener el mensaje "Onboarding data loaded: N campos confirmados" verificable.
3. Tests: loader encuentra el YAML en `output/clientes` aunque `--output` sea alternativo.

### T3 (Track 3): S5 — Label de fuente de occupancy veraz
**Archivo exacto**: `modules/financial_engine/harness_handlers.py` **L118**

**Bug identificado (causa raíz)**:
```python
# L118 actual — el label SIEMPRE dice "regional" cuando should_use_regional_for(region)=True,
# incluso cuando occupancy_source == "onboarding" (el valor NO se sobreescribe por L96,
# pero el label ignora esa lógica)
"occupancy": "regional" if flags.should_use_regional_for(region) else payload.get("occupancy_source", "default"),
```

**Fix**: la condición debe respetar la prioridad de `occupancy_source == "onboarding"`:
```python
"occupancy": occupancy_source if occupancy_source == "onboarding" else ("regional" if flags.should_use_regional_for(region) else occupancy_source),
```

**Verificación secundaria**: `scenario_calculator.py` L542 (`_trace_data_sources`) usa
`getattr(hotel_data, 'occupancy_source', 'unknown')` — verificar que `HotelFinancialData`
recibe el atributo `occupancy_source` correctamente desde el handler.

Tests: fixture con occupancy de onboarding → `data_sources.occupancy == "onboarding"`.

### T4 (agente principal): Integración y validación
- Merge mental de las 3 tracks: `run_all_validations.py --quick` TOTAL PASS.
- Tests de las 3 tracks en lotes pequeños redirigidos a archivo (L6).
- Conteo de tests nuevos desde `git diff tests/` (L8).

---

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| Tests delivery | `python -m pytest tests/delivery/ -v > temp/fase_d_delivery.txt 2>&1` | PASS |
| Tests loader/financial | Lotes pequeños según archivos tocados | PASS |
| Validaciones | `python scripts/run_all_validations.py --quick` | TOTAL PASS (conteo dinámico del script) |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. Actualizar `dependencias-fases.md` (FASE-D ✅) y `README.md` del plan.
2. `09-documentacion-post-proyecto.md`: Secciones B, D, E.
3. Registrar la fase:
```bash
python scripts/log_phase_completion.py --fase FASE-D --desc "RC2-b: ZIP sin evidence BLOCKING ni runs anteriores + fallback loader onboarding + occupancy label veraz (N16/N21/S7/S5)" --archivos-mod "modules/delivery/delivery_packager.py,main.py" --tests "N" --check-manual-docs
```
**SIN `--release`** (L3/L9).

---

## Criterios de Completitud (CHECKLIST)

- [ ] ZIP de cliente sin `commercial_gates_report*` y sin artefactos de runs previos
- [ ] Loader de onboarding con fallback a `output/clientes` verificado por test
- [ ] `breakdown.data_sources.occupancy` coherente con la fuente real
- [ ] `run_all_validations.py --quick` TOTAL PASS (conteo dinámico del script)
- [ ] `log_phase_completion.py` ejecutado SIN --release

## Restricciones

- Máximo 60 iteraciones (R2), distribuidas entre parent + subagentes.
- NO tocar archivos de FASE-B/C (v4_proposal_generator, commercial_gate).
- NO ejecutar `v4complete` (reservado para FASE-F).
- Si se delega: verificar el diff de cada track ANTES de integrar (L10).
