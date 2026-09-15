# FASE-P3-A: Fixes de detección y fidelidad del acta

**ID**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 / FASE-P3-A
**Objetivo**: Cerrar los tres fixes de detección y fidelidad sobre el tribunal: AC8/AC-F1 (`EMPTY_DELIVERY_TEMPLATE` en régimen ZIP-only), AC-F2 (tier del acta == MANIFEST) y AC-F4 (`first_floor_rule.reason` en `B_PLUS`). **NO toca `main.py` ni `acta_writer.py`** — eso es P3-B.
**Dependencias**: FASE-P1 ✅ (Q2b decidida + contrato de `decision-enforcement.md` fijado). Si P2 se ejecuta (Q1=sí), **P2 va antes** que esta fase: ambas tocan `judge.py` y el conteo NR1 (regla de secuencialidad en `dependencias-fases.md`).
**Presupuesto**: 20 iteraciones (R2.1: `evidence/FASE-D/measure_iterations.py`, corte = commit de código; bajo D-V2.1, auto-reporte con unidad declarada si el instrumento no alcanza el transcript).
**Complejidad técnica**: MEDIA
**Modo de ejecución**: DIRECTO (agente principal)
**Skill**: `phased_project_executor.md` v2.24.0

---

## Contexto

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-P1 | ⟨P1 fija: decisión Q2b (a) ZIP-vía-`zipfile` o (b) recalibración del heurístico; y cierre del contrato⟩ |
| FASE-P2 | ⟨P1 fija: ejecutada (O1/O2/O3) o no aplica (Q1=no/O4)⟩ |
| FASE-P3-A | ← ESTA FASE |

### Base técnica disponible
- `modules/quality_gates/tribunal/asset_reviewer.py` — `_resolve_delivery_dir`, `_is_template_stub`, `_check_implementation_order` (capas 1 y 2 de AC8, causa raíz fijada por la sonda `verify_probe_ac8.py` del predecesor)
- `modules/quality_gates/tribunal/judge.py` — `_compute_verdict`, `FIRST_FLOOR_TIERS`, `_apply_first_floor_rule` (AC-F4); fuente del tier (AC-F2)
- `modules/quality_gates/tribunal/honesty_reviewer.py` — `_extract_evidence_tier` (precedente de lectura pre-packaging de `financial_scenarios.breakdown.evidence_tier`)
- Baseline R2.6: `output/FASE-D_salentoreal_post_guard/` (fuera del repo — ver límite en §Deuda del checklist; si P1 decidió versionar fixture, usar el decidido)
- Tests base: `tests/quality_gates/tribunal/`

### Lecciones capitalizadas aplicables a esta fase
(filtras de `00-lecciones-capitalizadas.md` §2)

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-V.1 | La brecha fixture↔real tiene un tercer modo: el **layout** | Tarea 1: el test de AC8 se escribe contra el layout ZIP-only real, no contra el fixture sintético de T2-B |
| L-T4A.5 / L-T2C.4 / L-VUP-5 | Un test que no puede fallar no certifica el AC | NR7: AC-F1 y AC-F4 cierran con mutation check y par de salidas en `evidence/FASE-P3-A/` |
| L-PF6 / L-PF10 | "Sin hallazgos" ≠ "no midió" | AC-F2/AC-F4: el acta no puede pasar a "coherente" colapsando estados; la clave leída se declara en el artefacto |
| L-V.2 | VERIFY re-lee artefactos, no hereda conclusiones | Antes de editar, re-confirmar el mapa de símbolos de arriba (P1 puede haber reordenado con O1/O3) |
| R2.4 | AC no legible en artefacto = ⚠️ | Cada AC-F de esta fase cita el artefacto + clave del borrador §6 del maestro, actualizados por lo que fijara P1 |

---

## Tareas (R3: 3 tareas, 0 comandos largos)

### Tarea 1: AC8 — `EMPTY_DELIVERY_TEMPLATE` en régimen ZIP-only (AC-F1)
- Implementar la opción fijada por P1 (Q2b): `_resolve_delivery_dir()` leyendo `IMPLEMENTATION_ORDER.md` del ZIP vía `zipfile`, **o** recalibrar `_is_template_stub()` excluyendo `---`/boilerplate del conteo.
- Test contra el layout real ZIP-only (L-V.1) + sonda re-ejecutable versionada en `evidence/FASE-P3-A/`.
- **NR7**: desactivar el fix → el test se pone rojo; guardar el par de salidas.

### Tarea 2: AC-F2 — tier del acta == MANIFEST
- El Juez lee `financial_scenarios.breakdown.evidence_tier` (fuente pre-packaging; precedente: `_extract_evidence_tier`).
- Verificar contra artefacto real disponible; si P2 reordenó el flujo, la convergencia queda documentada en la evidencia.

### Tarea 3: AC-F4 — `first_floor_rule.reason` coherente en `B_PLUS`
- Aplicar lo que fijó el contrato de P1 (`reason` descriptivo o extensión de `FIRST_FLOOR_TIERS`) — no improvisar aquí la opción.
- **NR7**: mutation check con el par de salidas.

**Criterios de aceptación**:
- [ ] AC-F1, AC-F2, AC-F4 con su artefacto + clave verificados (R2.4)
- [ ] NR7 cumplido en AC-F1 y AC-F4 (pares verde/rojo en `evidence/FASE-P3-A/`)
- [ ] Delta NR1 con par pre/post y resta R2.7 (`suma_post − suma_pre == tests_nuevos`)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Cero cambios en `main.py`, `acta_writer.py` (P3-B) y `delivery_packager.py` (P2)

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| AC8 ZIP-only layout | `tests/quality_gates/tribunal/` (archivo propio de la fase) | Verde con el fix; rojo con él desactivado (NR7) |
| tier acta vs MANIFEST | idem | Compara `acta_revision.json` con `MANIFEST.json` del fixture R2.6 |
| primer piso `B_PLUS` | idem | `first_floor_rule.reason` conforme al contrato de P1 |

**Comando de validación**:
```bash
python -m pytest tests/quality_gates/tribunal/ -v
python scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: P3-A ✅ + fecha
2. `README.md`: tabla de progreso
3. `09-documentacion-post-proyecto.md`: acumular secciones A/B/D/E de esta fase
4. `10-analisis-post-implementacion.md`: fila del Resumen de Ejecución + lecciones nuevas + métricas
5. `00-lecciones-capitalizadas.md` §2: qué pasó realmente con las lecciones de arriba
6. `evidence/FASE-P3-A/`: pares NR7, sonda, par NR1
7. `log_phase_completion.py --fase FASE-P3-A --desc "..." --check-manual-docs` (SIN `--release`)

**NO esperar a la siguiente sesión.**

---

## Criterios de Completitud (CHECKLIST)

- [ ] Los 3 AC de la fase cierran con artefacto + clave (R2.4)
- [ ] NR7 con pares de salidas en evidencia
- [ ] Iteraciones medidas y escritas en `06-checklist-implementacion.md` (L-R.1 — un `—` no cierra)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Post-ejecución completada (7 puntos)

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- NO re-decidir el contrato (L-VUP-6): Q2b y la opción de AC-F4 vienen fijadas de P1; desviarse requiere decisión registrada.
- NO tocar `main.py` (conflicto con P2/P3-B).
- NO ejecutar `v4complete` (comando largo reservado a P4).
- Una sola ruta de bloqueo intacta (NR3); el tribunal no recalcula gates (NR2).
