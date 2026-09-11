# Remediación D-T4B-A1 — FASE-T4-B (2026-09-11)

> **Aditiva**: no reescribe `evidencia-final.md` ni borra los snapshots originales; enlaza las salidas que cierran cada gate G1–G11 del dossier.
> **Dossier de auditoría**: `.opencode/context/CONTEXT-AUDITORIA-FORENSE-FASE-T4B-REMEDIACION-2026-09-11.md`
> **Modo**: DIRECTO, una fase por sesión (R1 del executor). Restricciones del plan vigentes: `main.py`, `judge.py`, `llm_extractor.py`, `ROADMAP.md` **sin tocar**; sin `v4complete`; sin LLM real en tests; citas por símbolo (R2.2).

---

## Decisiones tomadas por el usuario (no por el ejecutor)

| # | Pregunta | Decisión | Dónde se registró |
|---|----------|----------|-------------------|
| Q1 | ¿Se cablean los 4 revisores en `main.py` ahora, o es entregable de FASE-E2E? | **Vía A: diferir a FASE-E2E** con fila de seguimiento y dueño; T4-B degrada a ⚠️ | `10-analisis` DA-T4B.1 + §Seguimientos; `dependencias-fases` (E2E dueña del cableado) |
| Q2 | ¿Qué significa "CG warning divulgado en la propuesta"? | **Tabla de frases específicas por `gate_id`** que nombran el problema; gate sin entrada no se juzga | DA-T4B.2; `DISCLOSURE_PHRASES_BY_GATE` |
| Q3 | ¿§5.1, §5.4 y §5.5 se implementan ahora o se difieren? | **Diferidas con dueño y AC nuevo** (E2E/VERIFY, AC17–AC19) + nota de alcance en `06-checklist` | DA-T4B.3 + §Seguimientos |
| Q4 | ¿`total_cg_count` cuenta entradas (12) o CG-* distintos (10)? | **Entradas + campos explícitos** (`distinct_cg_count`, `duplicate_gate_ids`) y findings deduplicados | DA-T4B.4 |

---

## Salidas de los gates de cierre

### G1 — sonda sobre el baseline real (§2.6 del dossier)

Pre-fix (misma sonda, código de `HEAD`):

```
propuesta cargada: False
{"canonical_file": null, "diagnostic_file": null, "total_cg_count": 0, "warnings_found": []}
veredicto: BLOQUEAR | findings: [('MISSING_ARTIFACT', 'No se encontró 02_PROPUESTA_COMERCIAL*.m')]
```

Post-fix:

```
propuesta cargada: True
escenarios: True | canonical: True | diagnostico: True
deliveries_dir: output\...\v4_complete\deliveries True
{"canonical_file": "commercial_gates_report.json",
 "diagnostic_file": "commercial_gates_report_diagnostic_20260831_122803.json",
 "total_cg_count": 12, "distinct_cg_count": 10,
 "duplicate_gate_ids": ["CG-OTA-NARRATIVE", "CG-TECH-JARGON"],
 "warnings_found": ["CG-WHATSAPP-LEAD"]}
veredicto: DEVOLVER-PRUEBAS
findings: [('CG_WARNING_UNDISCLOSED', 'WARNING', tier='B', cg_reference='CG-WHATSAPP-LEAD')]
summary: {"over_presentations":0,"tier_mismatches":0,"undisclosed_warnings":1,"missing_scenarios":0,"total_findings":1}
```

El veredicto sale de un hallazgo real, no de un artefacto ausente. `AlignmentReviewer` sobre el mismo baseline: `propuesta cargada: True`, matriz 1 fila, veredicto `APROBADO` (antes: `MISSING_ARTIFACT` + `BLOQUEAR`).

La contraste es reproducible: `python evidence/FASE-T4-B/sonda_contraste_pre_post.py` carga el revisor tal como esta en `HEAD` (sin tocar el arbol) y el del arbol de trabajo, yuxtapone las dos salidas sobre el mismo baseline, y funciona desde cualquier directorio. Tras commitear la remediacion ambas lineas coinciden; hasta entonces imprime exactamente el delta de arriba.

### G2 — tests retro sobre artefactos reales

```
$ pytest tests/quality_gates/tribunal -q
114 passed
```
(92 previos + 7 retro reales + 4 contrato de ubicación + 11 fidelidad de salida). `test_honesty_reviewer_retro_reales.py` se omite con `skipif` si `output/FASE-D_salentoreal_post_guard/` no está, para no romper CI en máquinas sin baseline.

### G3 — export del paquete

```
$ python -c "from modules.quality_gates.tribunal import HonestyReviewer; print('ok')"
ok
$ grep -c "HonestyReviewer" modules/quality_gates/tribunal/__init__.py
2
```

### G4 — AC12 con la propuesta real

`findings[].cg_reference == "CG-WHATSAPP-LEAD"` se afirma sobre la propuesta de la corrida FASE-D, que contiene `WhatsApp: 316 6296142`. El mismo gate se deja de señalar con un fixture que nombra el problema expresamente (`test_divulgacion_expresa_cierra_el_hallazgo`). Ambos verdes.

### G5 — NR1

| | pre-fase real (medido) | post-fase | post-remediación |
|---|---|---|---|
| Suma de contados | `3 f / 3991 p / 32 s / 4 xf` = 4.030 | 4.037 | `3 f / 4020 p / 32 s / 4 xf` = 4.059 |
| Colectados | 4.029 | 4.036 | 4.058 |

`3998 = 3991 + 7` y `4020 = 3998 + 22`, sin términos de corrección ad-hoc. Ver `rectificacion-NR1.md`.

### G6 — strings inventados

El patron de grep esta en R5 del dossier (4 strings: dos nombres de archivo inexistentes y dos `gate_id` inexistentes). Aplicado sobre `.opencode/plans/` y `evidence/`: **0 coincidencias** (verificado con `grep -rE` usando ese patron, excluyendo el propio dossier de auditoria). Ademas: los 7 nombres de test que publica `evidencia-final.md` existen como `def` en `test_honesty_reviewer.py`, y no queda ninguna tabla "AC1..AC10" en la evidencia de T4-B.

> **Unica coincidencia restante**: el dossier `.opencode/context/CONTEXT-AUDITORIA-FORENSE-FASE-T4B-REMEDIACION-2026-09-11.md` conserva los strings literales porque son la evidencia del hallazgo R5.2/R5.3. No se borran: borrarlos destruiria el registro de la auditoria. Esta nota tampoco los reproduce, para que el gate sea mechanically verificable sobre `evidence/`.

### G7 — responsabilidades §5

| §5 | Estado |
|---|---|
| 1 `evidence_tier` en cifras de fuga | ⚠️ diferido → E2E, AC17 |
| 2 sobre-presentación | ✅ `_check_over_presentation` |
| 3 3 escenarios | ✅ `_check_missing_scenarios` (presencia de claves = interpretación correcta; el artefacto real no declara probabilidades) |
| 4 base de cálculo de "recuperación en X meses" | ⚠️ diferido → VERIFY, AC18 |
| 5 contradicción propuesta ↔ gates financieros | ⚠️ diferido → VERIFY, AC19 |
| 6 CG-* de ambos archivos | ✅ operativo sobre artefactos reales (R1) |

### G8 / G9 — suite y validaciones

```
$ pytest tests/ -q
3 failed, 4020 passed, 32 skipped, 4 xfailed in 139.82s
```
Los 3 fallos son los preexistentes registrados en `aba517a` (`test_function_default_flags`, `test_barreda_un_solo_emisor_de_la_clave`, `test_diagnostic_includes_geo_metrics`). Skipped 32 → 32, delta 0.

```
$ python scripts/run_all_validations.py --quick
TOTAL: 8/8 validations passed
```

### G10 / G11 — decisiones y coherencia de estado

Q1–Q4 registradas en `10-analisis` §Decisiones Arquitectónicas (DA-T4B.1–.6). El estado ⚠️ es ahora idéntico en `06-checklist` (Estado Global + sección de fase), `README` (encabezado y tabla de progreso), `dependencias-fases` (tabla de dependencias), `evidencia-final.md` y esta nota; no queda ninguna fuente que diga AC11 ✅.

---

## Lección capitalizable

Cinco de los seis hallazgos (D1, D5, S1, S2, S3) compartían una sola causa: **7/7 verdes sobre un fixture que clonaba el contenido de los artefactos reales pero no su estructura de ubicación** — y la ubicación era el requisito marcado ⚠️ CRÍTICO. T4-A arrastraba el defecto idéntico, cubierto por la misma suite verde. Endurecimiento propuesto (dueño FASE-VERIFY/RELEASE): **gate de sonda retro** en `phased_project_executor.md` + verificación de que la suma pre/post difiera en exactamente `tests_nuevos`. Ver L-T4B.4 y L-T4B.5.
