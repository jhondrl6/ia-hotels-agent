# FASE-C-A: Gates Reales — D5 (coverage honesto) + N2 (gate doc↔audit)

**ID**: COHERENCIA-FASE-C-A
**Objetivo**: Que los gates validen lo que se publica: coverage que cuenta de verdad (D5) y detección de contradicciones entre el documento generado y el audit (N2).
**Dependencias**: FASE-A ✅, FASE-B ✅.
**Duración estimada**: 1 sesión (~45 iteraciones de 60).
**Skill**: `phased_project_executor` v2.13.0 · skill de apoyo: `iah-cli-output-forensics` (patrón gate discrepancy).

## Contexto

El run 2026-08-01 pasó `coverage_no_silent_drop` con `covered=0` (D5: no puede detectar drops silenciosos) y `hard_contradictions` con count=0 pese a que el doc decía "Sin Meta Tags" contra 8 tags OG del audit (N2). Causa raíz compartida (contexto §7 patrón 5): los gates validan INPUTS (assessment/status), no el ARTEFACTO que publican.

Fuente completa: contexto §5 FASE-3 (D5/N2).

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada |
| FASE-B | ✅ Completada |
| FASE-C-A | ▶️ EN CURSO (esta sesión) |

### Base Técnica Disponible
- Tests base: 3,185 + tests FASE-A/B.
- Baseline: `output/v4_complete/zione/v4_audit/gate_report_20260801_170540.json` (L169-181 coverage).
- `main.py:2638-2639` ya puebla `diagnostic_pain_ids` desde `brechas_reales`.

## Modo de ejecución (delegate_task)

**DIRECTO con el agente principal.** Rediseño de semántica de gates: la decisión WARNING-vs-BLOCKING y el diseño del gate doc↔audit requieren contexto completo de `publication_gates.py` y de los 11 gates existentes. NO delegable (branch decisión arquitectónica del executor).

## Decisiones de diseño

### DEC-C1 — Severidad inicial del gate doc↔audit (N2)
- **Riesgo §8 fila 3**: si nace BLOCKING, fallarán runs existentes con contradicciones hoy invisibles.
- **Decisión**: el gate nace en modo **WARNING** (se reporta en gate_report, no bloquea) y se documenta el upgrade a BLOCKING para una release posterior. Catalogar las contradicciones conocidas (OG, reviews, fotos, performance) en el mensaje.

### DEC-C2 — Mecanismo de evidencia del documento
- **Opción A (mínima viable, recomendada)**: el generador emite `evidence_used.json` (o reutiliza `diagnostic_pain_ids`) con los valores del audit que alimentaron cada sección; el gate compara contra el audit.
- **Opción B**: parsear el markdown del doc y comparar pares clave (frágil ante cambios de texto).
- **Decisión por defecto**: Opción A con fallback a B para pares simples (OG "Sin ... Open Graph").

## Tareas

### T1 — Fix D5: `_coverage_gate` (publication_gates.py L1263-1276)
- [ ] `covered` (pains que aparecen en el doc) cuenta ANTES de eximir por status justificado.
- [ ] `is_justified` exime solo si el pain además está explicado por un asset.
- [ ] Si `covered=0` y `justified>0` → WARNING en el mensaje ("0 pains aparecen en el documento").
- [ ] Nunca más "Coverage completo" con covered=0.

### T2 — Fix N2: gate `doc_audit_consistency` (o extensión de `_hard_contradictions_gate` L240-270)
Pares clave a validar (doc parseado/evidence_used vs audit):
- [ ] audit.seo_elements.open_graph=true → el doc NO puede decir "Sin ... Open Graph".
- [ ] reviews citadas en el doc vs `gbp.reviews`.
- [ ] target de fotos del doc vs photos del audit.
- [ ] performance.status=ERROR → el doc no puede decir "sitio nuevo o tráfico bajo".
- [ ] FAILED/WARNING con mensaje que cite la sección del doc.
- [ ] Modo inicial WARNING (DEC-C1).

### T3 — Tests
**Archivos**: `tests/quality_gates/`.
- [ ] Test: covered=0 con pains existentes → gate emite WARNING y mensaje honesto.
- [ ] Test: doc con "Sin Open Graph" + audit open_graph=true → gate reporta la contradicción.
- [ ] Test: doc coherente con audit → gate PASSED silencioso.
- [ ] Test: modo WARNING no bloquea la publicación.

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| Gates | `./venv/Scripts/python.exe -m pytest tests/quality_gates -q` | 0 regresiones |
| Integración | `./venv/Scripts/python.exe -m pytest tests/ -k "publication_gates or coverage_gate" -q` | 0 fallos |
| Validaciones | `./venv/Scripts/python.exe scripts/run_all_validations.py --quick` | 4/4 |

## Post-Ejecución (OBLIGATORIO)

1. Marcar FASE-C-A ✅ en `dependencias-fases.md`, `09-checklist-implementacion.md`, `README.md`.
2. Actualizar `11-documentacion-post-proyecto.md` (A, B, D, E) — documentar DEC-C1/C2.
3. Ejecutar:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-C-A \
    --desc "D5 coverage gate honesto + N2 gate doc-audit consistency (WARNING)" \
    --archivos-mod "modules/quality_gates/publication_gates.py" \
    --tests "<N nuevos>" --check-manual-docs
```
> ⚠️ NO usar `--release` en fases intermedias (L3/L9) — solo en FASE-RELEASE.

## Criterios de Completitud (CHECKLIST)

- [ ] D5 cerrado: covered cuenta antes de eximir; warning si covered=0
- [ ] N2 cerrado: gate detecta contradicción OG en test
- [ ] Tests T3 pasan + 0 regresiones
- [ ] `run_all_validations.py --quick` 4/4
- [ ] `log_phase_completion.py` ejecutado

## Restricciones

- Máximo 60 iteraciones (R2).
- NO delegar a subagente.
- NO ejecutar v4complete (única ejecución: FASE-E).
- El gate N2 nace WARNING, NO blocking (riesgo §8 fila 3).
- NO tocar textos del generador (D6/D7 son FASE-C-B) ni templates.
