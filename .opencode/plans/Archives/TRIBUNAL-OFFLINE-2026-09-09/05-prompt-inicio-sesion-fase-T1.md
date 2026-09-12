# FASE-T1: Juez Certificador del Tribunal

**ID**: TRIBUNAL-OFFLINE-2026-09-09 / FASE-T1
**Objetivo**: Implementar el Juez determinista (`tribunal/judge.py`) que certifica las 6 cláusulas P6 + P7, produce `acta_revision.json` + `acta_revision.md`, y se integra en `main.py` junto a `delivery_quality_report` alimentando UNA ruta existente de bloqueo del ZIP.
**Dependencias**: Ninguna (baseline v4.75.0, precondiciones T0 cerradas)
**Complejidad técnica**: **ALTA** — decisión arquitectónica cross-module (elegir ruta de integración, diseñar contrato de acta que T2/T4 consumen)
**Modo de ejecución**: **DIRECTO** (agente principal). NO delegable: decisión arquitectónica que afecta múltiples consumidores (lección DT-3).
**Skill**: `phased_project_executor.md` v2.20.0

---

## Contexto

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| ESTABILIZACION-PRE-TRIBUNAL (v4.75.0) | ✅ Completada — T0.1-T0.4 cerradas |
| FASE-T1 | ← ESTA FASE |

### Base Técnica Disponible

- **Baseline**: v4.75.0, 3.934 funciones de test / 298 archivos
- **Corrida de referencia**: `evidence/FASE-I/` (coherence 0.8333, `is_coherent: true`, 5 pains)
- **Baseline solo-lectura**: `output/FASE-D_salentoreal_post_guard/` (Tier B, coherence canónico 0.88, `is_coherent: false`, ZIP 46.552 B)
- **Módulos existentes que el Juez LEE (no reimplementa)**:
  - `modules/quality_gates/publication_gates.py` — 13 gates (11 blocking + 2 advisory)
  - `modules/quality_gates/commercial_gate.py` — 12 CG-* en DOS archivos
  - `modules/quality_gates/delivery_quality_report.py` — QA post-generación
  - `modules/asset_generation/pain_ledger.py` — PainLedger facade
  - `modules/asset_generation/proposal_asset_alignment.py` — matriz servicio→asset
- **Artefactos que el Juez lee** (timestamped, resolver por glob/índice):
  - `gate_report_*.json`, `commercial_gates_report.json`, `commercial_gates_report_diagnostic_*.json`
  - `coherence_validation.json`, `pain_ledger.json`, `pain_ledger_resolved.json`
  - `proposal_asset_matrix.json`, `asset_generation_report.json`, `delivery_quality_report.json`
  - `financial_scenarios_*.json`
  - `MANIFEST.json` + `ASSETS/` + `IMPLEMENTATION_ORDER.md` — **viven en `deliveries_dir`** (`v4_complete/deliveries/<hotel>_<fecha>/`), NO en `v4_audit/`. `evidence_tier` se lee de `MANIFEST.json → quality_metadata.evidence_tier`.

### Lecciones aplicables (Paso 0)

| Lección | Aplicación |
|---------|-----------|
| R2.2: citar símbolos, no líneas | ACs usan `def judge`, `BLOCKING_GATE_NAMES`, nunca `archivo:NNN` |
| R2.4: AC legible en artefacto | Cada AC declara artefacto + clave; test de serialización obligatorio |
| Anfitrión real = `main.py` | `two_phase_flow.py` es huérfano; integrar junto a `delivery_quality_report` |
| Una ruta de bloqueo | El veredicto alimenta UNA de las tres existentes, no añade cuarta |
| Tribunal NO reimplementa gates | Lee outputs; grep verifica que no importa internals |
| S-HF1: `total_services` | Decidir qué mide como criterio de narración (no serialización) |

---

## Tareas

### Tarea 1: Research — Rutas de bloqueo del ZIP y punto de integración

**Objetivo**: Identificar las tres rutas de bloqueo del ZIP en `main.py` + el kill switch `GATE_BLOCKING_ENABLED`, elegir cuál alimenta el veredicto del Juez, y documentar la decisión. Incluye fijar la regla de resolución de `deliveries_dir` (glob del `<hotel>_<fecha>` más reciente bajo `v4_complete/deliveries/`) que el contrato de acta declara para todos los revisores.

**Archivos a leer**:
- `main.py` — zona de `delivery_quality_report` (buscar símbolos: `delivery_quality_report`, `GATE_BLOCKING_ENABLED`, `zip`, `block`)
- `modules/quality_gates/publication_gates.py` — símbolo `check_publication_readiness`
- `modules/quality_gates/delivery_quality_report.py` — punto de llamada en main

**Criterios de aceptación**:
- [ ] Decisión documentada en `evidence/FASE-T1/decision-integracion.md`: cuál ruta, por qué, qué pasa con el kill switch
- [ ] La ruta elegida es una de las tres existentes (no nueva)

### Tarea 2: Implementar `tribunal/judge.py` + `acta_writer.py`

**Objetivo**: Clase `TribunalJudge` con veredicto determinista sobre las 6 cláusulas P6. Writers de acta dual (JSON + MD).

**Archivos a crear**:
- `modules/quality_gates/tribunal/__init__.py`
- `modules/quality_gates/tribunal/judge.py`
- `modules/quality_gates/tribunal/acta_writer.py`

**Diseño del contrato de acta** (estable para T2/T4):
```python
# acta_revision.json schema
{
    "verdict": "APROBADO-PARA-ENTREGA" | "APROBADO-CONDICIONAL-PENDING-ONBOARDING" | "DEVOLVER-CORRECCIONES" | "BLOQUEADO",
    "evidence_tier": "A" | "B" | "C",
    "clauses_evaluated": 6,
    "clauses": {
        "P6.1": {"status": "PASS"|"FAIL"|"ADVISORY"|"NOT_EVALUABLE", "source_artifact": "...", "finding": "..."},
        "P6.2": {...}, "P6.3": {...}, "P6.4": {...},
        "P6.5": {"status": "NOT_EVALUABLE", "source_artifact": null, "finding": "reservada para Bot 4 (honestidad NL) — D-T1.3 opción a"},
        "P6.6": {...}
    },
    "reviewer_reports": ["revision_diagnostico.json", "revision_assets.json", ...],
    "first_floor_rule": {"applied": true, "reason": "evidence_tier B → máximo condicional"},
    "timestamp": "...",
    "hotel_id": "..."
}
```

**Fuentes de lectura del Juez (fijadas por esta auditoría, NO re-decidir en T1)**:
- `evidence_tier`: `MANIFEST.json → quality_metadata.evidence_tier` (archivo en `deliveries_dir`, no en `v4_audit/`).
- **P6.6**: `gate_report_*.json → gate_results[coherence]` + `gate_results[hard_contradictions]` — NO el flag `is_coherent` de `coherence_validation.json` (el baseline FASE-D trae `is_coherent: false` por 1 error de `assets_are_justified` con gates en verde; post-N11/P9 el gate `coherence` ya respeta `is_coherent`, así que leer los gates es fuente única y evita contradecir AC2).
- **`NOT_EVALUABLE`**: cláusula sin artefacto fuente disponible (p. ej. revisores aún no implementados, o artefacto eliminado por gate-blocking) → estado `NOT_EVALUABLE`, nunca PASS. El Juez NUNCA lanza excepción por artefacto ausente (never-block).
- Constructor: `TribunalJudge(v4_audit_dir=..., deliveries_dir=...)` con `deliveries_dir` resuelto por glob (`v4_complete/deliveries/<hotel_id>_*` más reciente).

**Regla de primer piso (D-T1.3 opción a: NO es cláusula P6.5)**: si `evidence_tier ∈ {B, C}` → veredicto máximo `APROBADO-CONDICIONAL-PENDING-ONBOARDING`. Sin LLM. Determinista. Vive en la clave top-level `first_floor_rule` del acta, no en `clauses.P6.5`. `P6.5` queda reservada como `NOT_EVALUABLE` hasta que Bot 4 (T4-B) la certifique como honestidad NL.

**Resolución de artefactos timestamped**: el Juez debe resolver nombres por glob (ej. `gate_report_*.json` → más reciente) o por índice si existe. NO hardcodear timestamps. `deliveries_dir` se resuelve por glob del `<hotel>_<fecha>` más reciente.

**Matriz findings → veredicto (recomendación acotada por esta auditoría; T1 la consolida)**: gate blocking fallido en `gate_report` → `BLOQUEADO`; finding `CRITICAL` de revisores o veredicto de revisor `BLOQUEAR` → `DEVOLVER-CORRECCIONES`; solo findings WARNING/INFO con gates en verde → primer piso por tier (`APROBADO-CONDICIONAL-PENDING-ONBOARDING` para B/C, `APROBADO-PARA-ENTREGA` solo Tier A). Un WARNING (p. ej. `CG-WHATSAPP-LEAD`) NO degrada por debajo del primer piso.

**Criterios de aceptación**:
- [ ] `TribunalJudge.evaluate()` retorna veredicto determinista
- [ ] Regla de primer piso implementada y testeable
- [ ] `acta_writer.py` produce JSON + MD
- [ ] El MD incluye las 6 cláusulas con referencia al artefacto fuente
- [ ] NO importa internals de `publication_gates.py` (solo lee sus outputs)

### Tarea 3: Tests

**Objetivo**: Tests deterministas retro sobre artefactos reales + test de serialización (R2.4).

**Archivos a crear**:
- `tests/quality_gates/tribunal/__init__.py`
- `tests/quality_gates/tribunal/test_judge.py`
- `tests/quality_gates/tribunal/test_acta_serialization.py`

**Tests obligatorios**:
| Test | Criterio |
|------|----------|
| `test_verdict_tier_b_is_conditional` | Artefacto SalenteReal (Tier B) → `APROBADO-CONDICIONAL-PENDING-ONBOARDING` |
| `test_verdict_tier_a_can_be_approved` | Fixture Tier A + coherence ≥ 0.8 + is_coherent true → `APROBADO-PARA-ENTREGA` |
| `test_first_floor_rule_blocks_delivery` | Tier C → nunca `APROBADO-PARA-ENTREGA` |
| `test_acta_json_serialization` | Lee el JSON del writer real (no objeto en memoria), verifica claves |
| `test_acta_md_has_six_clauses` | El MD contiene secciones P6.1-P6.6 |
| `test_resolves_timestamped_artifacts` | Glob resuelve `gate_report_*.json` sin hardcodear timestamp |
| `test_does_not_reimplement_gates` | Grep: `judge.py` no importa `publication_gates` internals |

**Nota sobre fixtures retro (auditoría 2026-09-09)**: los `gate_report_*.json` de FASE-D y FASE-I son corridas PRE-HOTFIX — sus `gate_results` NO traen `severity` ni `blocks_publication`. El parser debe tratar `severity` como opcional en fixtures (el código actual sí lo serializa; la corrida E2E sí lo tendrá). Con P6.6 leída de los gates, `test_verdict_tier_b_is_conditional` pasa contra ambas corridas.

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/tribunal/ -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

### Tarea 4: Integración en `main.py` + Docs

**Objetivo**: Cablear el Juez en el pipeline junto a `delivery_quality_report`. El veredicto alimenta la ruta de bloqueo elegida en Tarea 1.

**Archivos a modificar**:
- `main.py` — añadir llamada al tribunal tras `delivery_quality_report`

**Integración**:
```python
# Tras delivery_quality_report, antes de la decisión de ZIP:
from modules.quality_gates.tribunal import TribunalJudge
try:
    judge = TribunalJudge(v4_audit_dir=..., deliveries_dir=...)
    acta = judge.evaluate()
except Exception:
    acta = None  # never-block: el fallo del tribunal NO rompe v4complete
# El veredicto alimenta la ruta existente elegida (NO añade cuarta)
```

**Criterios de aceptación**:
- [ ] `main.py` llama al Juez una sola vez
- [ ] El veredicto se escribe en `v4_audit/acta_revision.json` + `acta_revision.md`
- [ ] La ruta de bloqueo del ZIP respeta el veredicto del Juez
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Baseline pre/post guardado en `evidence/FASE-T1/`

**Docs**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-T1 \
    --desc "Juez certificador del tribunal: acta dual P6+P7, regla de primer piso, integración main.py" \
    --archivos-nuevos "modules/quality_gates/tribunal/__init__.py,modules/quality_gates/tribunal/judge.py,modules/quality_gates/tribunal/acta_writer.py,tests/quality_gates/tribunal/__init__.py,tests/quality_gates/tribunal/test_judge.py,tests/quality_gates/tribunal/test_acta_serialization.py" \
    --archivos-mod "main.py" \
    --tests "7" \
    --check-manual-docs
```

---

## Post-Ejecución (OBLIGATORIO)

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**: marcar FASE-T1 como ✅ Completada
2. **`README.md` del plan**: actualizar tabla de progreso
3. **`09-documentacion-post-proyecto.md`**: Secciones A, B, D, E
4. **`10-analisis-post-implementacion.md`**: Resumen de Ejecución + Lecciones (mínimo 3)
5. **`evidence/FASE-T1/`**: baseline pre/post, decisión de integración, artefactos de test
6. **`06-checklist-implementacion.md`**: marcar items de T1

**NO esperar a la siguiente sesión.**

---

## Criterios de Completitud (CHECKLIST)

- [ ] **AC1**: `acta_revision.json` con clave `verdict` legible (test de serialización verde)
- [ ] **AC2**: Tier B/C → `APROBADO-CONDICIONAL-PENDING-ONBOARDING` (test verde)
- [ ] **AC3**: `acta_revision.md` con 6 cláusulas P6 (test verde)
- [ ] **AC4**: Una ruta de bloqueo, no cuarta (grep + decisión documentada)
- [ ] **NR1**: `passed_post = passed_pre + tests nuevos` (baseline pre/post)
- [ ] **NR3**: `run_all_validations.py --quick` TOTAL PASS
- [ ] **NR4**: Tribunal no reimplementa gates (test `test_does_not_reimplement_gates`)
- [ ] **S-HF1**: Criterio de narración `total_services` decidido
- [ ] **Post-ejecución completada** (6 puntos anteriores)

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- **Presupuesto**: 55 iteraciones, medido con `evidence/FASE-D/measure_iterations.py`, corte en commit de código (R2.1)
- **NO ejecutar v4complete** (solo tests retro sobre artefactos existentes)
- **NO modificar ROADMAP.md**
- **NO reimplementar lógica de gates** (regla arquitectónica inviolable)
- **NO usar números de línea en ACs ni en el código de integración** (R2.2: citar símbolos)
- **NO delegar a subagente** (decisión arquitectónica cross-module)
- **Contrato de acta estable**: lo que T1 define aquí es lo que T2-A, T2-B, T4-A, T4-B consumen. Cambios posteriores al contrato requieren decisión explícita registrada en `10-analisis`.
