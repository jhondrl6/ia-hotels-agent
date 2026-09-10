# FASE-T4-A: Revisor de Alineación NL (Bot 2) + Interfaz de Extracción LLM

**ID**: TRIBUNAL-OFFLINE-2026-09-09 / FASE-T4-A
**Objetivo**: Diseñar la interfaz de extracción LLM compartida (`llm_extractor.py`) e implementar `tribunal/alignment_reviewer.py` — revisor híbrido que extrae promesas verbales de la propuesta y las verifica deterministamente contra la matriz. Produce `revision_alineacion.json`.
**Dependencias**: FASE-T1 ✅, FASE-T2-A ✅, FASE-T2-B ✅
**Complejidad técnica**: **ALTA** — define la arquitectura híbrida LLM+determinista que T4-B replica; decisión de diseño sobre el protocolo de extracción y la estrategia de mock
**Modo de ejecución**: **DIRECTO** (agente principal). NO delegable: decisión arquitectónica (diseño del protocolo de extracción LLM + mock strategy que establece patrón para T4-B).
**Skill**: `phased_project_executor.md` v2.20.0

---

## Contexto

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-T1 | ✅ (contrato de acta) |
| FASE-T2-A | ✅ (Bot 1: diagnóstico) |
| FASE-T2-B | ✅ (Bot 3: assets) |
| FASE-T4-A | ← ESTA FASE |

### Base Técnica Disponible

- **Contrato de acta** (T1): `modules/quality_gates/tribunal/judge.py`
- **Reportes de T2**: `revision_diagnostico.json`, `revision_assets.json` (el Juez los agrega)
- **Artefactos que Bot 2 lee**:
  - `02_PROPUESTA_COMERCIAL_*.md` (propuesta en lenguaje natural)
  - `proposal_asset_matrix.json` (matriz servicio→asset con `asset_path`)
  - `pain_ledger_resolved.json` (brechas con assets mapeados)
- **Estados reales de la matriz (auditoría 2026-09-09)**: `entries[].status ∈ {LINKED, PRESENT_IN_PRODUCTION, NO_BREACH}` (FASE-I real: 3 PRESENT_IN_PRODUCTION + 1 LINKED). Mapeo al vocabulario del tribunal:
  - `LINKED` con `pain_id` + promesa verbal → `ALINEADO`
  - `LINKED` sin `pain_id` → `SIN-BRECHA-ASOCIADA`
  - `PRESENT_IN_PRODUCTION` → `ALINEADO` (con nota "presente en producción")
  - `NO_BREACH` → NO es hallazgo (estado legítimo de servicio no prometido; info)
  - promesa verbal sin entrada en matriz → `PROMESA-SIN-MATRIZ`
- **LLM del pipeline**: `modules/providers/` (provider registry); el extractor usa el mismo LLM que el pipeline, con cache
- **Residuo S-C4**: la tabla de assets técnicos en la propuesta imprime catálogo incondicional — es una tercera superficie de promesa que Bot 2 debe detectar

### Lecciones aplicables

| Lección | Aplicación |
|---------|-----------|
| §15.1: LLM solo extrae, Juez decide | El extractor NUNCA emite veredicto; solo lista promesas encontradas |
| §15.4.2: T4 con extracción intercambiable | Protocolo abstracto: LLM del pipeline O subagente; mockeado en tests |
| R2.4: AC legible en artefacto | Test de serialización del JSON real |
| Vocabulario §10.3: `promesa-sin-matriz` y `SIN-BRECHA-ASOCIADA` | Usar estos términos exactos en la clasificación |
| S-C4: tercera superficie de promesa | La tabla de assets técnicos también promete; Bot 2 la cubre |

---

## Tareas

### Tarea 1: Diseñar + implementar `llm_extractor.py`

**Objetivo**: Protocolo de extracción LLM compartida (patrón que T4-B replica).

**Archivo a crear**:
- `modules/quality_gates/tribunal/llm_extractor.py`

**Diseño**:
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class PromiseExtractor(Protocol):
    """Protocolo de extracción de promesas verbales desde texto de propuesta."""
    def extract_verbal_promises(self, proposal_text: str) -> list[VerbalPromise]: ...

class VerbalPromise:
    """Una promesa encontrada en lenguaje natural."""
    text: str           # texto literal de la promesa
    service_hint: str   # servicio al que parece referirse (inferido por el LLM)
    location: str       # sección de la propuesta donde aparece
    confidence: float   # confianza de la extracción (0-1)

class LLMPromiseExtractor:
    """Implementación default: usa el LLM del pipeline con cache."""
    def __init__(self, provider=None, cache_dir=None): ...
    def extract_verbal_promises(self, proposal_text: str) -> list[VerbalPromise]: ...

class MockPromiseExtractor:
    """Para tests: retorna promesas fijas sin llamar LLM."""
    def __init__(self, promises: list[VerbalPromise]): ...
    def extract_verbal_promises(self, proposal_text: str) -> list[VerbalPromise]: ...
```

**Regla clave**: el extractor SOLO propone. Nunca emite veredicto. El veredicto lo aplica la capa determinista del revisor, y el Juez lo certifica.

**Criterios de aceptación**:
- [ ] Protocolo `PromiseExtractor` definido y `runtime_checkable`
- [ ] `LLMPromiseExtractor` usa el provider del pipeline (importable desde `modules/providers/`)
- [ ] `MockPromiseExtractor` para tests (sin dependencia de LLM real)
- [ ] Cache: si el mismo texto ya fue extraído, no re-llama al LLM

### Tarea 2: Implementar `alignment_reviewer.py`

**Objetivo**: Clase `AlignmentReviewer` — híbrido acotado.

**Archivo a crear**:
- `modules/quality_gates/tribunal/alignment_reviewer.py`

**Responsabilidades del Bot 2** (§5 del CONTEXT):
1. Cada servicio vendido responde a una brecha diagnosticada (o oportunidad derivada)
2. No hay servicios sin brecha asociada
3. Cada brecha tiene al menos una recomendación o se explica por qué se descarta
4. Precios consistentes con costos estimados
5. Narrativa de impacto coherente con base de cálculo
6. **S-C4**: tabla de assets técnicos como tercera superficie de promesa

**Flujo**:
1. LLM extrae promesas verbales de `02_PROPUESTA_COMERCIAL.md`
2. Capa determinista cruza cada promesa contra `proposal_asset_matrix.json`
3. Clasifica: `ALINEADO` / `SIN-BRECHA-ASOCIADA` / `PROMESA-SIN-MATRIZ`
4. Produce `revision_alineacion.json`

**Salida**:
```json
{
    "reviewer": "alignment_reviewer",
    "clause": "P6.2",
    "service_matrix": [
        {
            "service": "...",
            "status": "ALINEADO" | "SIN-BRECHA-ASOCIADA" | "PROMESA-SIN-MATRIZ",
            "verbal_promise_found": true | false,
            "promise_text": "..." | null,
            "matrix_entry_found": true | false,
            "pain_id": "..." | null,
            "finding": "..." | null
        }
    ],
    "findings": [...],
    "summary": {"aligned": N, "no_breach": N, "promise_without_matrix": N},
    "verdict_recommendation": "APROBADO" | "DEVOLVER-PRUEBAS" | "BLOQUEAR"
}
```

**Criterios de aceptación**:
- [ ] Clase `AlignmentReviewer` con método `review(v4_audit_dir, extractor=None) → dict`
- [ ] Si `extractor` es None, usa `LLMPromiseExtractor`; en tests se inyecta `MockPromiseExtractor`
- [ ] Detecta promesa verbal sin entrada en matriz → `PROMESA-SIN-MATRIZ`
- [ ] Detecta servicio `LINKED` sin brecha asociada → `SIN-BRECHA-ASOCIADA` (`NO_BREACH` no es hallazgo)
- [ ] S-C4: tabla de assets técnicos incondicional detectada como superficie de promesa

### Tarea 3: Tests (LLM mockeado)

**Archivos a crear**:
- `tests/quality_gates/tribunal/test_alignment_reviewer.py`
- `tests/quality_gates/tribunal/test_llm_extractor.py`

**Tests obligatorios**:
| Test | Criterio |
|------|----------|
| `test_promise_without_matrix_detected` | Mock extrae "implementación de chatbot" → no está en matriz → `PROMESA-SIN-MATRIZ` |
| `test_aligned_service_not_flagged` | Servicio con brecha + entrada en matriz → `ALINEADO` |
| `test_no_breach_associated_detected` | Entrada `LINKED` en matriz sin `pain_id` → `SIN-BRECHA-ASOCIADA`; `NO_BREACH` no es hallazgo |
| `test_s_c4_asset_table_detected` | Tabla de assets técnicos incondicional → finding |
| `test_mock_extractor_used_in_tests` | `MockPromiseExtractor` retorna promesas fijas, sin LLM |
| `test_serialization_to_disk` | JSON escrito y re-leído (R2.4) |
| `test_extractor_protocol_compliance` | `LLMPromiseExtractor` cumple `PromiseExtractor` protocol |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/tribunal/test_alignment_reviewer.py tests/quality_gates/tribunal/test_llm_extractor.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

### Tarea 4: Docs + Post-ejecución

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-T4-A \
    --desc "Bot 2: revisor de alineación NL + interfaz de extracción LLM (protocolo PromiseExtractor, mock, S-C4)" \
    --archivos-nuevos "modules/quality_gates/tribunal/llm_extractor.py,modules/quality_gates/tribunal/alignment_reviewer.py,tests/quality_gates/tribunal/test_alignment_reviewer.py,tests/quality_gates/tribunal/test_llm_extractor.py" \
    --tests "7" \
    --check-manual-docs
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: marcar FASE-T4-A ✅
2. **`README.md` del plan**: actualizar progreso
3. **`09-documentacion-post-proyecto.md`**: Secciones A, B, D
4. **`10-analisis-post-implementacion.md`**: fila T4-A + lecciones (mínimo 3) + DA (decisión de diseño del protocolo)
5. **`evidence/FASE-T4-A/`**: baseline pre/post
6. **`06-checklist-implementacion.md`**: marcar items T4-A

---

## Criterios de Completitud (CHECKLIST)

- [ ] **AC9**: `revision_alineacion.json` con `service_matrix[]` (test de serialización verde)
- [ ] **AC10**: Promesa sin matriz → `PROMESA-SIN-MATRIZ` (test verde)
- [ ] **S-C4**: Tabla assets técnicos detectada (test verde)
- [ ] **Protocolo**: `PromiseExtractor` definido, `MockPromiseExtractor` funcional
- [ ] **NR1**: `passed_post = passed_pre + tests nuevos`
- [ ] **NR3**: `run_all_validations.py --quick` TOTAL PASS
- [ ] **NR4**: No reimplementa gates
- [ ] **Post-ejecución completada**

---

## Restricciones

- **Presupuesto**: 50 iteraciones, corte en commit de código (R2.1)
- **NO ejecutar v4complete**
- **NO modificar ROADMAP.md ni `main.py` ni `judge.py`**
- **NO llamar LLM real en tests** (siempre mock)
- **NO usar números de línea** (R2.2)
- **NO delegar a subagente** (decisión arquitectónica: diseño del protocolo de extracción)
- **El patrón establecido aquí es el que T4-B replica**: cualquier cambio al protocolo afecta a T4-B
