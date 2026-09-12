# FASE-T4-B: Revisor de Honestidad Comercial (Bot 4)

**ID**: TRIBUNAL-OFFLINE-2026-09-09 / FASE-T4-B
**Objetivo**: Implementar `tribunal/honesty_reviewer.py` — revisor híbrido que detecta sobre-presentación de datos ESTIMATED como verificados, verifica que los 3 escenarios (70/20/10) están presentes, y lee los 12 CG-* repartidos en DOS archivos comerciales. Produce `revision_honestidad.json`.
**Dependencias**: FASE-T4-A ✅ (patrón de extracción LLM establecido)
**Complejidad técnica**: **MEDIA** — replica el patrón de T4-A con diferentes inputs; la dificultad es leer los DOS archivos comerciales y resolver los 12 CG-*
**Modo de ejecución**: **DIRECTO** (agente principal). NO delegable: la fase crea un módulo **y corre tests que importan el proyecto**; el venv es Windows accedido desde WSL ⟹ ejecutor v2.20.0, branch «imports del proyecto + venv Windows → DIRECTA… NO delegar a subagentes».
**Skill**: `phased_project_executor.md` v2.20.0

---

## Contexto

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-T1 | ✅ (contrato de acta) |
| FASE-T2-A | ✅ (Bot 1) |
| FASE-T2-B | ✅ (Bot 3) |
| FASE-T4-A | ✅ (Bot 2 + interfaz LLM) |
| FASE-T4-B | ← ESTA FASE |

### Base Técnica Disponible

- **Patrón de extracción** (T4-A): `modules/quality_gates/tribunal/llm_extractor.py` — protocolo `PromiseExtractor`, `MockPromiseExtractor`
- **Artefactos que Bot 4 lee**:
  - `financial_scenarios_*.json` (timestamped — resolver por glob)
  - `commercial_gates_report.json` (3 gates en verde — archivo canónico)
  - `commercial_gates_report_diagnostic_*.json` (9 gates adicionales, incluyendo CG-WHATSAPP-LEAD WARNING)
  - `02_PROPUESTA_COMERCIAL_*.md` (propuesta en lenguaje natural)
  - `quality_metadata` del MANIFEST (evidence_tier, precision_tier) — **en `deliveries_dir`** (`v4_complete/deliveries/<hotel>_<fecha>/`, resolver por glob del más reciente; NO en `v4_audit/`)
- **⚠️ CRÍTICO**: El reporte comercial está PARTIDO en dos archivos. Leer solo el canónico produce falso "todo pasó". El único gate que falló en la corrida real (CG-WHATSAPP-LEAD) está en el archivo de diagnóstico.

### Lecciones aplicables

| Lección | Aplicación |
|---------|-----------|
| Reporte comercial partido en 2 | Bot 4 DEBE leer ambos archivos y unir los 12 CG-* |
| LLM solo extrae, Juez decide | Mismo patrón de T4-A: extractor propone, determinista verifica |
| R2.4: AC legible en artefacto | Test de serialización |
| Nombres timestamped | Resolver por glob, no hardcodear |
| **D-T1.3 ✅ resuelta (opción a)** | `P6.5` es limpiamente de Bot 4 (honestidad NL). El primer piso del Juez vive en `first_floor_rule` (top-level del acta), no en `clauses.P6.5`. El Juez reserva `P6.5` como `NOT_EVALUABLE` hasta que este revisor la certifique |

---

## Tareas

### Tarea 1: Implementar `honesty_reviewer.py`

**Objetivo**: Clase `HonestyReviewer` — replica el patrón híbrido de T4-A.

**Archivo a crear**:
- `modules/quality_gates/tribunal/honesty_reviewer.py`

**Responsabilidades del Bot 4** (§5 del CONTEXT):
1. Cifras de fuga y proyecciones tienen `evidence_tier` declarado
2. Propuesta no presenta ESTIMATED como verificado
3. Escenarios son los 3 declarados (70/20/10), no solo el favorable
4. Claims de "recuperación en X meses" tienen base de cálculo visible
5. No hay contradicciones entre propuesta y gates financieros
6. Los 12 CG-* están leídos de AMBOS archivos (6 blocking + 4 warning + 2 adicionales)

**Flujo**:
1. LLM extrae claims de sobre-presentación de la propuesta (usa `PromiseExtractor` de T4-A o un `ClaimExtractor` análogo)
2. Capa determinista verifica cada claim contra: tier labels, escenarios, CG-*
3. Clasifica: `OVER_PRESENTATION` / `TIER_MISMATCH` / `CG_WARNING_UNDISCLOSED` / `MISSING_SCENARIO`
4. Produce `revision_honestidad.json`

**Salida**:
```json
{
    "reviewer": "honesty_reviewer",
    "clause": "P6.5",
    "findings": [
        {
            "severity": "CRITICAL" | "WARNING" | "INFO",
            "type": "OVER_PRESENTATION" | "TIER_MISMATCH" | "CG_WARNING_UNDISCLOSED" | "MISSING_SCENARIO",
            "claim_text": "..." | null,
            "evidence_tier_declared": "B",
            "cg_reference": "CG-WHATSAPP-LEAD" | null,
            "description": "..."
        }
    ],
    "commercial_gates_read": {
        "canonical_file": "commercial_gates_report.json",
        "diagnostic_file": "commercial_gates_report_diagnostic_*.json",
        "total_cg_count": 12,
        "warnings_found": ["CG-WHATSAPP-LEAD", ...]
    },
    "summary": {"over_presentations": N, "tier_mismatches": N, "undisclosed_warnings": N},
    "verdict_recommendation": "APROBADO" | "DEVOLVER-PRUEBAS" | "BLOQUEAR"
}
```

**Criterios de aceptación**:
- [ ] Clase `HonestyReviewer` con método `review(v4_audit_dir, extractor=None) → dict`
- [ ] Lee AMBOS archivos comerciales (canónico + diagnóstico) y reporta `total_cg_count: 12`
- [ ] Detecta CG-WHATSAPP-LEAD (WARNING) en el archivo de diagnóstico
- [ ] Detecta ESTIMATED presentado como verificado → `OVER_PRESENTATION`
- [ ] Verifica presencia de los 3 escenarios (70/20/10)

### Tarea 2: Tests (LLM mockeado)

**Archivo a crear**:
- `tests/quality_gates/tribunal/test_honesty_reviewer.py`

**Tests obligatorios**:
| Test | Criterio |
|------|----------|
| `test_reads_both_commercial_files` | Fixture con 2 archivos → `total_cg_count: 12` |
| `test_cg_whatsapp_lead_detected` | CG-WHATSAPP-LEAD en diagnóstico → finding `CG_WARNING_UNDISCLOSED` |
| `test_over_presentation_detected` | Mock extrae "cifras verificadas" con tier B → `OVER_PRESENTATION` |
| `test_missing_scenario_detected` | Fixture con solo escenario optimista → `MISSING_SCENARIO` |
| `test_tier_mismatch_detected` | Claim con tier declarado ≠ tier real → `TIER_MISMATCH` |
| `test_serialization_to_disk` | JSON escrito y re-leído (R2.4) |
| `test_mock_extractor_no_real_llm` | Tests no llaman LLM real |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/tribunal/test_honesty_reviewer.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

### Tarea 3: Docs + Post-ejecución

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-T4-B \
    --desc "Bot 4: revisor de honestidad comercial (12 CG-* en 2 archivos, sobre-presentación, escenarios 70/20/10)" \
    --archivos-nuevos "modules/quality_gates/tribunal/honesty_reviewer.py,tests/quality_gates/tribunal/test_honesty_reviewer.py" \
    --tests "7" \
    --check-manual-docs
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: marcar FASE-T4-B ✅
2. **`README.md` del plan**: actualizar progreso
3. **`09-documentacion-post-proyecto.md`**: Secciones A, B, D
4. **`10-analisis-post-implementacion.md`**: fila T4-B + lecciones (mínimo 3)
5. **`evidence/FASE-T4-B/`**: baseline pre/post
6. **`06-checklist-implementacion.md`**: marcar items T4-B

---

## Criterios de Completitud (CHECKLIST)

- [ ] **AC11**: `revision_honestidad.json` con `findings[]` (test de serialización verde)
- [ ] **AC12**: CG-WHATSAPP-LEAD detectado del archivo diagnóstico (test verde)
- [ ] **12 CG-* leídos**: `total_cg_count: 12` en la salida
- [ ] **NR1**: `passed_post = passed_pre + tests nuevos`
- [ ] **NR3**: `run_all_validations.py --quick` TOTAL PASS
- [ ] **NR4**: No reimplementa gates
- [ ] **Post-ejecución completada**

---

## Restricciones

- **Presupuesto**: 30 iteraciones, corte en commit de código (R2.1)
- **NO ejecutar v4complete**
- **NO modificar ROADMAP.md, `main.py`, `judge.py`, ni `llm_extractor.py`**
- **NO llamar LLM real en tests** (siempre mock)
- **NO usar números de línea** (R2.2)
- **DIRECTO (no delegable)**: los tests importan el proyecto y el venv es Windows/WSL. Si excepcionalmente se demuestra que los tests son stdlib-only, la delegación requeriría que el parent ejecute los tests.
