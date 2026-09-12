# 01 — Plan Maestro: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

> **Origen**: síntesis de FASE-VERIFY del plan TRIBUNAL-OFFLINE-2026-09-09 (certificación 2026-09-11, commit `e6161a3`). Este documento desarrolla lo que sus lecciones y seguimientos apuntan pero no cierran: L-E2E.1 (timing), L-E2E.3 (advisory de facto), AC8 ❌ (D-V.4), D-V.1, D-V.3.
> **Precondición global**: ✅ cumplida el 2026-09-11 — FASE-RELEASE-4.76.0 del predecesor cerró en `bd2bf57` (v4.76.0 publicada **localmente, sin push ni tag**; plan archivado por R2.5; `--quick` 8/8).
> **Arrastre del predecesor para P1**: a los residuos técnicos de este plan se suman 6 ítems de **deuda de gates** (verificador de R2.6/R2.7, cobertura 12,5 % de `validate_plan_closure.py`, campo `Version actual` del REGISTRY, reescrito ciego de `validate_opencode_refs.py --fix`, punto ciego de `version_consistency_checker.py`, y L-R.1: la columna `Iteraciones` del checklist no obliga a medir): están listados en §Deuda de proceso de `06-checklist-implementacion.md`.

---

## 1. Secuencia y presupuesto

| Fase | Depende de | Presupuesto (iter) | delegate_task | Código |
|------|-----------|--------------------|---------------|--------|
| FASE-P1 | RELEASE-4.76.0 ✅ | 30 | No | No (decisión) |
| FASE-P2 | P1 (Q1=sí + opción elegida) | 55 | No | Sí |
| FASE-P3 | P1 (Q2b) | 30 | No | Sí |
| FASE-P4 | P1 (Q3/Q4) + P3 recomendado + datos reales (T3) | 40 | Sí (corrida) | No |
| FASE-RELEASE-4.77.0 | P2/P3 (si aplican) + P4 | 30 | Sí | Docs |

Presupuesto medido con `evidence/FASE-D/measure_iterations.py` (R2.1); corte en commit.

---

## 2. El nudo técnico (estado certificado en FASE-VERIFY)

```
main.py (v4complete)
├── FASE 4.5–5: publication gates + delivery_quality_report
├── Juez: TribunalJudge(v4_audit_dir, deliveries_dir)      ← ANTES del packaging
│        └─ acta = judge.evaluate()
│             └─ blocks_delivery_zip(acta) → condición ZIP-skip (única ruta del tribunal)
├── FASE 6: packager.package()                             ← single-write ZIP-only
│        └─ zf.writestr: MANIFEST.json, IMPLEMENTATION_ORDER.md, ASSETS/ — solo existen DESPUÉS
└── FASE 7: los 4 revisores (post-packaging, never-block por Bot, LLMPromiseExtractor compartido)
         └─ revision_diagnostico / assets / alineacion / honestidad .json  ← llegan TARDE para el Juez
```

**Consecuencia certificada**: `reviewer_reports` en el acta queda `[]`; en la corrida real Bot 1 recomendó BLOQUEAR y Bot 4 DEVOLVER-PRUEBAS y el ZIP se emitió igual (veredicto `APROBADO-CONDICIONAL-PENDING-ONBOARDING`, gates-only).

**Catch-22**: los revisores con hallazgos más bloqueantes (Bot 3 completitud de assets, Bot 4 honestidad) leen artefactos que solo existen tras `packager.package()`; la decisión del ZIP es anterior al packaging.

**El gap importa más en Tier A**: con B/C el primer piso acota el veredicto a condicional. Con dato real (Tier A) `APROBADO-PARA-ENTREGA` es alcanzable — y hoy ese veredicto ignoraría las objeciones de los revisores.

---

## 3. Opciones de refactor (a decidir en FASE-P1, Q2)

| Opción | Idea | Pros | Contras | Blast radius |
|--------|------|------|---------|--------------|
| **O1 — metadata pre-ZIP** | Serializar MANIFEST/ASSETS-metadata **antes** de escribir el ZIP; revisores corren pre-decisión; el ZIP se escribe al final | Un solo pase; los revisores siguen leyendo archivos reales (contrato intacto) | Serialización duplicada; riesgo de drift entre staging y ZIP final | `main.py`, `delivery_packager.py` |
| **O2 — estado en memoria** | Los revisores consumen objetos runtime pre-packaging | Sin archivos staging | Rompe el contrato "leen artefactos del disco"; acopla revisores a objetos runtime; tests más frágiles | revisores + `main.py` |
| **O3 — dos pasadas** | `package()` → staging; revisores leen staging; decisión final ship/suppress | El más limpio y auditable; el ZIP final solo nace si pasa | Cambia el contrato de `delivery_packager.py`; mayor superficie de cambio | `delivery_packager.py`, `main.py` |
| **O4 — sin refactor** | Mantener auditoría-only; decisión de producto explícita y documentada | Cero riesgo técnico | El gap advisory persiste; Tier A diría "entrega" ignorando objeciones | ninguno |

**Restricción transversal (NR3)**: O1/O2/O3 deben integrar el enforcement en la ruta existente — la decisión final sigue pasando por `blocks_delivery_zip()`/ZIP-skip. Nunca una cuarta ruta de bloqueo.

**Precedente aprovechable**: `_extract_evidence_tier` de `honesty_reviewer.py` ya lee `financial_scenarios.breakdown.evidence_tier` — la fuente de tier pre-packaging existe para el fix de fidelidad (P3) y como entrada del Juez si se elige reordenarlo.

---

## 4. Fases (detalle)

### FASE-P1 — Decisión y contrato (MEDIA · DIRECTO · sin código)
- **Tarea 1 — Research (solo lectura)**: confirmar el mapa con símbolos: `TribunalJudge.evaluate` / `_compute_verdict` (`judge.py`), `blocks_delivery_zip` + condición ZIP-skip (`main.py`), bloque FASE 7 de revisores (`main.py`), `package()` (`delivery_packager.py`), `_resolve_delivery_dir` / `_is_template_stub` (`asset_reviewer.py`), `_extract_evidence_tier` (`honesty_reviewer.py`). Verificar si D-V.3 (endurecimiento del executor) ya se ejecutó en RELEASE-4.76.0 — **resuelto: sí**, executor v2.21.0 con R2.6 y R2.7; lo abierto es su verificador mecánico y que el baseline que exige R2.6 vive bajo `output/`, excluido por `.gitignore`. Entregable: `evidence/FASE-P1/research-estado.md`.
- **Tarea 2 — Decisión con el usuario (una tanda de preguntas)**: Q1–Q4 (ver prompt de inicio).
- **Tarea 3 — Contrato + ACs finales**: `evidence/FASE-P1/decision-enforcement.md` con: decisión, opción elegida, matriz recomendación→veredicto propuesta (hereda la de T1: finding CRITICAL o veredicto BLOQUEAR de revisor → DEVOLVER-CORRECCIONES/BLOQUEADO; WARNING no degrada bajo el primer piso; never-block preservado), y ACs finales con artefacto+clave (R2.4).
- **Regla heredada (§15.4.1)**: el contrato fijado aquí obliga a P2/P3; cambios posteriores requieren decisión registrada.

### FASE-P2 — Refactor de ordenamiento (ALTA · solo si Q1=sí y opción ≠ O4)
- Implementar O1/O2/O3 manteniendo never-block, NR2 y NR3.
- Tests obligatorios: camino de bloqueo ejercitado (recomendación BLOQUEAR de un revisor → ZIP no emitido), camino aprobado, never-block (fallo de un revisor no rompe la corrida), retro sobre `output/` vivo y sobre la corrida E2E del predecesor (`evidence/FASE-E2E/`).
- Si Q1=no (O4): la fase se sustituye por documentación de la decisión y se cierra sin código.

### FASE-P3 — Fixes localizados (MEDIA)
- **AC8**: opción a fijar en P1 (Q2b) — (a) `_resolve_delivery_dir()` lee `IMPLEMENTATION_ORDER.md` del ZIP vía `zipfile`, o (b) recalibrar `_is_template_stub()` (excluir `---` y boilerplate Fecha/Score/footer del conteo).
- **Tier del acta**: el Juez lee el tier de una fuente disponible pre-packaging (`financial_scenarios.breakdown.evidence_tier`) o se reordena — converger con P2 si hay reordenamiento.
- **Whitelist barreda (D-V.1)**: test-only — autorizar a Bot 3 como emisor legítimo de `asset_path` en `test_barreda_un_solo_emisor_de_la_clave`.
- **Versión del acta**: `acta_writer.py` lee de `VERSION.yaml` (fuente única).

### FASE-P4 — Corrida de observación Tier A (MEDIA · MIXTO)
- **Precondición externa (T3)**: datos operativos reales de un hotel propio — `rooms`, `occupancy_rate`, `direct_channel_percentage`, `ADR` con fuente declarada. Sin ellos no hay `evidence_tier: A` ni primer piso levantado.
- Corrida v4complete + onboarding (delegate_task para la corrida, como FASE-E2E del predecesor).
- **Encuadre**: corrida de observación/diagnóstico, NO entrega a cliente. `APROBADO-PARA-ENTREGA` = provisional si el enforcement no está cerrado.
- Entregable: `evidence/FASE-P4/informe-observacion.md` (checklist §5) + delta vs corrida E2E del predecesor (R2.3).

### FASE-RELEASE-4.77.0 (BAJA · DELEGABLE)
- Flujo documental estándar: `log_phase_completion.py --release`, `sync_versions.py`, CHANGELOG, GUIA_TECNICA, doctor, R2.5 archivado de este plan.

---

## 5. Checklist de observación (P4) — qué mirar en la corrida real

1. `evidence_tier` resultante con dato real (¿A?) y `first_floor_rule` levantado.
2. Veredicto: ¿alcanza `APROBADO-PARA-ENTREGA`? (provisional si E no cerrado).
3. Comportamiento de Bots 1–4 con dato rico: nuevos findings, falsos positivos/negativos.
4. Fidelidad del acta: `evidence_tier` del acta vs MANIFEST (post-P3 debe coincidir).
5. Gap advisory: recomendaciones de revisores vs veredicto (si P2 cerró enforcement, ya no debe existir).
6. AC17/AC19 del predecesor con cifras reales: `precision_tier`, `can_show_exact_money`, bases de pérdida (`expected_loss_cop` vs fuga mensual).
7. Delta vs corrida E2E del predecesor (R2.3: par pre/post).

---

## 6. ACs borrador (fijar definitivos en P1)

| AC | Fase | Enunciado borrador | Artefacto + clave (R2.4) |
|----|------|--------------------|--------------------------|
| AC-E1 | P2 | El acta refleja `reviewer_reports` (no vacío cuando los 4 revisores corrieron) | `acta_revision.json` → `reviewer_reports` |
| AC-E2 | P2 | Recomendación BLOQUEAR de un revisor → ZIP no emitido (una sola ruta) | `main.py` (grep) + corrida/test |
| AC-E3 | P2 | Never-block: fallo de un revisor no rompe la corrida | test output |
| AC-F1 | P3 | `EMPTY_DELIVERY_TEMPLATE` dispara en régimen ZIP-only real | `revision_assets.json` → `finding_type` |
| AC-F2 | P3 | `evidence_tier` del acta == MANIFEST en corrida real | `acta_revision.json` vs `MANIFEST.json` |
| AC-F3 | P3 | Barreda `asset_path` verde (whitelist test-only) | test output |
| AC-O1 | P4 | Corrida Tier A real produce acta + veredicto (provisionalidad registrada) | `acta_revision.json` → `verdict` + `evidence_tier` |
| AC-O2 | P4 | Informe de observación con los 7 puntos de §5 | `evidence/FASE-P4/informe-observacion.md` |
| AC-V1 | RELEASE | Certificación formal de todos los ACs contra artefacto real (patrón VERIFY) | matriz en `10-analisis` |

---

## 7. No-Regresiones (NR)

| NR | Regla | Verificación |
|----|-------|--------------|
| NR1 | Sin regresión: `passed_post = passed_pre + tests nuevos` (par pre/post con instrumento) | medición pre/post por fase |
| NR2 | El tribunal no reimplementa gates (verificar sí, recalcular no) | grep `import.*publication_gates` en `tribunal/*.py` = 0 |
| NR3 | Una sola ruta de bloqueo (no cuarta) | grep en `main.py` + decisión documentada |
| NR4 | Coherence ≥ 0.80 en toda corrida nueva | `coherence_score_final` del reporte |
| NR5 | El LLM extrae, el Juez decide (veredicto determinista) | tests del contrato (precedente: `test_no_rejulga_un_gate_que_paso`) |
| NR6 | Resolución de artefactos por fecha embebida, no `mtime` (si se toca el resolutor) | tests del resolutor |

---

## 8. Versión

Objetivo **4.77.0** (confirmar en P1). Fuente única: `VERSION.yaml`. Nunca hardcodear versiones en código — incluye `acta_writer.py` (fix P3).
