# FASE-C — RC2-a: Fix CG-CLAIM-VS-EVIDENCE (N11) + Cablear CG-TIER-CONSISTENCY (N15)

**ID**: RC1-RC2-ENTREGA-COHERENTE-2026-08-04 / FASE-C
**Objetivo**: Eliminar el falso positivo estructural de CG-CLAIM-VS-EVIDENCE con texto condicional y convertir CG-TIER-CONSISTENCY de no-op vacuo a gate que valida inputs reales.
**Dependencias**: FASE-B ✅ (verificar en dependencias-fases.md; si no ✅, ABORTAR)
**Duración estimada**: 1.5-2.5 horas
**Skill**: `.agents/workflows/phased_project_executor.md`
**Modo de ejecución**: Agente principal **DIRECTO** (mismos 2 archivos, trabajo secuencial; NO delegar — no hay tracks paralelas y los tests requieren el venv del proyecto).

---

## Contexto

| Hallazgo | Problema |
|----------|----------|
| **N11 (MEDIA)** | `commercial_gate.py` L523-530 aplica regex `[Nn]o\s+aparece\|[Nn]o\s+figura\|...` sobre el texto COMPLETO sin parseo de oraciones → falso positivo BLOCKING con texto condicional ("si su web no tiene los datos correctos, no aparece en la respuesta" — diagnóstico L123 del run 124443) |
| **N15 (MEDIA)** | `validate_diagnostic` (v4_diagnostic_generator.py L617-654) nunca pasa `frontmatter_tier`/`text_tier` (defaults None) → CG-TIER-CONSISTENCY siempre responde "Sin datos de tier para comparar" y pasa vacuo SIEMPRE (Pitfall 12) |

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada |
| FASE-B | ✅ Completada (verificar antes de empezar) |

### Base Técnica Disponible
- `modules/quality_gates/commercial_gate.py` (gate definitions)
- `modules/commercial_documents/v4_diagnostic_generator.py` (invocación del gate)
- Evidencia del falso positivo: `output/v4_verify_4.70.0/v4_complete/zione/v4_audit/commercial_gates_report_diagnostic_20260804_124443.json`
- El dato de tier YA existe en `financial_breakdown.evidence_tier` del diagnóstico

---

## Tareas

### T1: R2.1 — CG-CLAIM-VS-EVIDENCE sin falsos positivos en condicionales
**Objetivo**: El regex solo debe capturar afirmaciones factuales, no cláusulas condicionales.

**Cambios en `modules/quality_gates/commercial_gate.py`** (L523-568):
1. Split del texto por oraciones (`re.split(r'[.!?]\s+', diagnostic_text)`) ANTES de aplicar el regex.
2. Para cada oración que matchee el patrón `[Nn]o\s+aparece|...`, verificar si contiene
   marcador condicional ("si ", "siempre que", "en caso de", "podría", "puede que")
   ANTES de la posición del match → descartar esa oración.
3. Si TODAS las oraciones que matchean son condicionales → PASS (no hay claim factual).
   Si al menos una oración NO es condicional → proceder con la lógica actual (evaluar
   `place_found` + `gbp_rating`).
4. **NO exigir sujeto explícito**: es frágil y genera falsos negativos (ej: "la web
   no aparece en Google" es factual pero no contiene "hotel").
5. Reproducir el caso real: con el texto del diagnóstico L123 del run 124443 el gate
   debe pasar; con "El hotel no aparece en Google." (place_found=True) debe fallar.

**Criterios de aceptación**:
- [ ] Test unitario con el texto condicional real → PASS del gate.
- [ ] Test unitario con claim factual falso + evidence place_found=True → FAIL del gate.

### T2: R2.2 — CG-TIER-CONSISTENCY con inputs reales (nunca vacuo)
**Objetivo**: El gate valida tier de verdad o falla explícitamente.

**Cambios**:
1. `v4_diagnostic_generator.py` L627-649: la invocación actual de `validate_diagnostic`
   **NO pasa `frontmatter_tier` ni `text_tier`** (verificado contra código vivo — los
   parámetros reciben `None` por default). Fix: añadir `frontmatter_tier=` y `text_tier=`
   como keyword arguments:
   - `frontmatter_tier`: desde `financial_breakdown.evidence_tier` (que ya existe —
     actualmente se pasa dentro de `financial_json` pero NO como parámetro directo).
   - `text_tier`: extracción por regex del texto del diagnóstico (menciona Tier B+/A/etc.).
2. `commercial_gate.py` L633-642: si los inputs siguen None después del cableado, el
   gate debe FALLAR con mensaje explícito (o convertirse en WARNING severo), NUNCA
   pasar vacuo con `passed=True`. Cambiar `passed=True` por `passed=False` cuando
   ambos inputs son None.

**Criterios de aceptación**:
- [ ] En el fixture del diagnóstico Zione (tier B+), el gate compara inputs reales (no el mensaje "Sin datos de tier").
- [ ] Test: inputs None → el gate NO pasa vacuo.

### T3: Tests de ambos gates
- Tests nuevos en `tests/quality_gates/` (o donde residan los tests de commercial_gate):
  condicional vs factual, tier cableado, tier None.
- Ejecutar SOLO los archivos de tests de gates (lotes pequeños, redirigidos a archivo — L6).
- Conteo de tests nuevos desde `git diff tests/` (L8).

**Criterios de aceptación**:
- [ ] Tests nuevos pasan; 0 regresiones en tests existentes de gates.

---

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| Tests de gates | `python -m pytest tests/quality_gates/test_commercial_gate*.py -v > temp/fase_c_test.txt 2>&1` | PASS |
| Subconjunto seguro FASE-A | Lotes pequeños secuenciales | 0 regresiones |
| Validaciones | `python scripts/run_all_validations.py --quick` | TOTAL PASS (conteo dinámico del script) |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. Actualizar `dependencias-fases.md` (FASE-C ✅) y `README.md` del plan.
2. `09-documentacion-post-proyecto.md`: Sección B (gates afinados), D (+N tests), E.
3. Registrar la fase:
```bash
python scripts/log_phase_completion.py --fase FASE-C --desc "RC2-a: CG-CLAIM-VS-EVIDENCE sin falsos positivos condicionales + CG-TIER-CONSISTENCY cableado (N11/N15)" --archivos-mod "modules/quality_gates/commercial_gate.py,modules/commercial_documents/v4_diagnostic_generator.py" --tests "N" --check-manual-docs
```
**SIN `--release`** (L3/L9).

---

## Criterios de Completitud (CHECKLIST)

- [ ] Texto condicional real del run 124443 ya NO dispara CG-CLAIM-VS-EVIDENCE
- [ ] Claim factual falso con evidence contraria SÍ sigue disparándolo
- [ ] CG-TIER-CONSISTENCY valida inputs reales; inputs None → fallo explícito (no vacuo)
- [ ] `run_all_validations.py --quick` TOTAL PASS (conteo dinámico del script)
- [ ] `log_phase_completion.py` ejecutado SIN --release

## Restricciones

- Máximo 60 iteraciones (R2).
- NO tocar `v4_proposal_generator.py` (FASE-B) ni `delivery_packager.py` (FASE-D).
- NUNCA suite completa de `tests/quality_gates` si contiene archivos lentos; lotes pequeños (L1/L11).
- NO ejecutar `v4complete` (reservado para FASE-F).
- Backup previo: `Copy-Item` de los 2 archivos a `temp/rc2_backup/` (L4/L5).
