# FASE-SR-C — Self-Healing Loop para CG-CLAIM-VS-EVIDENCE

**ID**: FASE-SR-C
**Objetivo**: Implementar el ciclo de corrección (D-PF2) para el gate comercial `CG-CLAIM-VS-EVIDENCE`: al detectar un claim factualmente falso, REGENERAR la sección con el `suggestion` del gate como restricción y re-validar; si persiste tras 1 reintento → escalar a BLOCKED real (documentos retenidos, ZIP abortado). Fin del patrón "detecta, loggea y publica igual" (L-SR5).
**Dependencias**: FASE-SR-B ✅ (orden del plan; no hay conflicto directo de archivos, pero `main.py` puede tocarse → SR-C antes que SR-D).
**Complejidad**: Alta · **Delegación**: ❌ DIRECTO (diseño de mecanismo nuevo cross-module + código+tests)
**Duración estimada**: 60-90 min · **Presupuesto**: ~25-30 iteraciones trabajo + ~15 verificación/docs (R2: máx. 60)

## Reglas de Sesión (MANDATORIO)

- R1: Una fase por sesión. R2: máx. 60 iteraciones (checkpoint + evidencia si se agota). R3: 4 tareas + 0 comandos largos.
- Python: `./venv/Scripts/python.exe`.

## Contexto

**Lectura previa obligatoria**: CONTEXT-SALENTOREAL §7.2 (hallazgo 6.2), §8.2 L-SR5, §9 #2 + plan maestro §8.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-SR-A | ✅ Completada |
| FASE-SR-B | ✅ Completada |

### Base Técnica Disponible (H6.2 verificado en corrida C)
- `modules/quality_gates/commercial_gate.py`: `CG-CLAIM-VS-EVIDENCE` (L74, lógica L538-595, tres emisiones con `gate_id`). Detectó "El documento dice 'no aparece' (factual) pero place_found=True y rating=4.5/5.0" → BLOCKING → registrado como "hidden from client" (`WARNING:root:Diagnostic commercial gates BLOCKING`) → **el flujo continuó y publicó el claim falso**.
- El gate YA provee el texto trazable correcto en su `suggestion` — solo falta inyectarlo en la regeneración.
- La regeneración post-FASE 4 del diagnóstico NO consume el resultado del gate (no hay self-healing loop para claims).

## Tareas

### T1: Investigar el flujo de gates comerciales del diagnóstico
**Archivos**: `modules/quality_gates/commercial_gate.py`, flujo de regeneración post-FASE 4 (localizar: `main.py` `run_v4_complete_mode` y/o `modules/orchestration_v4/`), escritura de `commercial_gates_report*.json`.
**Criterios**:
- [ ] Mapa del flujo: dónde se evalúan los gates → dónde se archiva "hidden from client" → dónde se regenera el documento → por qué el claim sobrevive
- [ ] Confirmar que `suggestion` del gate contiene la restricción trazable correcta

### T2: Implementar el loop self-healing (D-PF2)
**Criterios**:
- [ ] Al detectar `CG-CLAIM-VS-EVIDENCE` BLOCKING → regenerar la sección/documento afectado usando el `suggestion` como restricción obligatoria
- [ ] Re-evaluar los gates comerciales sobre el documento regenerado
- [ ] Máximo 1 regeneración (guard anti-bucle); si persiste → BLOCKED real: documentos cliente retenidos, ZIP abortado, BLOCKED_BY_GATES registra la causa real
- [ ] Trazabilidad: el reporte final distingue "resuelto por regeneración" vs "escalado a BLOCKED"

### T3: Tests del loop
**Criterios**:
- [ ] Test: claim contradictorio con GBP → regeneración corrige el claim → 0 gates blocking en 2ª evaluación
- [ ] Test: claim persistente (suggestion ignorado) → BLOCKED real, documentos retenidos
- [ ] Test: guard anti-bucle — nunca más de 1 regeneración
- [ ] Tests de regresión de gates comerciales (archivos específicos)

### T4: Greps + docs
**Criterios**:
- [ ] Grep: sin código de regeneración duplicado fuera del loop (0 caminos paralelos)
- [ ] `grep "hidden from client"` — el registro persiste pero ya no es terminal (documentar comportamiento nuevo)

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| loop corrige claim | tests de `commercial_gate` / integración del diagnóstico | 2ª evaluación = 0 blocking |
| escalado a BLOCKED | ídem | Persistencia → BLOCKED real |
| anti-bucle | ídem | Máx. 1 regeneración |

**Comandos** (procesos aislados, salida a archivo):
```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates -k "commercial or claim" -v > temp/fase_sr_c_tests1.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_commercial_gates.py -v > temp/fase_sr_c_tests2.txt 2>&1
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```
⚠️ NUNCA la suite completa de `tests/commercial_documents` en un proceso (memoria 2026-08-03).

## Post-Ejecución (OBLIGATORIO — antes de cerrar la sesión)

1. `dependencias-fases.md` §2 → ✅. 2. `README.md` → ✅. 3. `06-checklist` → SR-C. 4. `09-documentacion` → B/D/E + Notas. 5. `10-analisis` → Resumen + L-PF3 + D-PF2 confirmada/ajustada. 6. `evidence/FASE-SR-C/` → diff + tests. 7. Registro (SIN `--release`):
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-SR-C --desc "Self-healing loop CG-CLAIM-VS-EVIDENCE: regeneracion con suggestion + re-validacion; persistencia escalada a BLOCKED" --archivos-mod "modules/quality_gates/commercial_gate.py" --tests "<N reales>" --check-manual-docs
```
8. `./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer`

## Criterios de Completitud (CHECKLIST)

- [ ] Tests del loop pasan; regresiones = 0
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Guard anti-bucle verificado
- [ ] Docs post-fase completos (1-8)
- [ ] Evidencia en `evidence/FASE-SR-C/`

## Restricciones

- Máx. 60 iteraciones; NO ejecutar v4complete/v4audit.
- NO modificar `modules/financial_engine/` ni otros gates de publicación (solo el ciclo comercial).
- NO eliminar el registro "hidden from client" (auditoría) — solo cambiar su consecuencia.
- NO delegar a subagente.
- NO usar `--release` en log_phase_completion.
- Smoke L-SR1: si se toca una rama condicional nueva en `main.py`, ejecutar la rama una vez (o cubrirla con test) + grep de símbolos sospechosos (`logger\.`, imports no usados).
