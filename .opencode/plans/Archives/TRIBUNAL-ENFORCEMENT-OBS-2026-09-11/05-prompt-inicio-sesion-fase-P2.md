# FASE-P2: Refactor de ordenamiento — O1-cuarentena + veredicto enriquecido

**ID**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 / FASE-P2
**Objetivo**: Implementar el contrato fijado en FASE-P1: el ZIP se escribe en cuarentena (`.zip.tmp`), los 4 revisores lo leen, el Juez decide sobre sus hallazgos y **la decisión gatea el rename**. Entregar AC-E0…AC-E5 con el par NR7 y los cuatro tests por estado de NR8.
**Creado por**: FASE-P1 (Q1=sí) — `evidence/FASE-P1/decision-enforcement.md`. **Esta fase NO re-decide nada de §1 de ese documento.**
**Dependencias**: FASE-P3-A ✅ y FASE-P3-B ✅ (**orden fijado por DA-P1.3**: substrato confiable antes que dientes). `judge.py` llega a esta fase con AC-F2 y AC-F4 ya corregidos; el resolutor de entrega ya es ZIP-aware.
**Complejidad técnica**: **ALTA** — cross-module (`judge.py` + `main.py` + `delivery_packager.py` + `acta_writer.py` + tests)
**Modo de ejecución**: **DIRECTO** (agente principal). No delegable.
**Skill**: `phased_project_executor.md` v2.24.0
**Presupuesto**: 55 iteraciones, medido con corte en el commit de código y **unidad declarada** (D-V2.1: el instrumento no alcanza el transcript bajo el cliente actual → auto-reporte de `ids` + `tool_use`).

---

## Qué está cerrado y no se reabre

| Decisión de P1 | Efecto vinculante en P2 |
|----------------|--------------------------|
| Q1 = enforcement | El tribunal bloquea. No se discute otra vez |
| Q1b = **escalar, no ciclar** | **Prohibido** implementar reintento automático. ZIP suprimido + `corrective_actions` + humano decide |
| Q2 = **O1-cuarentena** | La decisión se mueve del *write* al **rename**. `package()` se parte en write/publish. **No** usar staging de metadatos (O1-staging), ni memoria (O2), ni dos pasadas con staging (O3) |
| Q5 = (a) + AC-F2 | El tier llega correcto desde P3-A/P3-B; P2 **no** recalcula el tier |
| Q6 = **cuatro estados** | `OK_NO_FINDINGS` / `ARTIFACT_MISSING` / `READER_FAILED` / `NOT_RUN`; sección **siempre** en el MD |
| Q7 = hereda `GATE_BLOCKING_ENABLED` | Un solo knob; el acta declara `enforcement.suppressed_by_operator` |
| §2.1 matriz | Orden de evaluación de la tabla §2.1 **es** el contrato. Cambiar el orden = cambiar la decisión |
| §2.3 DTO | `ReviewerReport` / `CorrectiveAction` / `TribunalOutcome` / `EnforcementState`. **Nada de `json.loads` del acta para decidir** |

---

## Invariantes (se verifican en esta fase, no se re-diseñan)

- **NR3**: `blocks_delivery_zip` sigue siendo el **único** predicado. El packager recibe un booleano; **no** lee el veredicto por su cuenta ni consulta `acta["verdict"]` en otro sitio de `main.py`.
- **NR2**: el tribunal no reimplementa gates.
- **NR5**: el LLM propone, el Juez decide determinista. Ningún revisor escribe el veredicto.
- **Never-block**: el fallo de un revisor se registra como `READER_FAILED` y no aborta la corrida.
- **Un fallo de lectura no bloquea**: `ARTIFACT_MISSING`/`READER_FAILED`/`NOT_RUN` **nunca** producen `BLOQUEADO` ni `DEVOLVER-CORRECCIONES`; solo impiden `APROBADO-PARA-ENTREGA` vía `NOT_EVALUABLE`.

---

## Tareas (R3: 4 tareas, 0 comandos largos)

### Tarea 1 — Cuarentena en el packager (AC-E2, AC-E5)
- Exponer el paso existente de `tmp_zip_path` como API: **write** (devuelve la ruta del `.tmp`) y **publish** (renombre) / **suppress** (unlink), con el `except` que hoy borra el tmp preservado.
- `main.py`: el bloque FASE 7 escribe el tmp **antes** de decidir; el rename ocurre **después** del veredicto enriquecido.
- **Verificación obligatoria antes de tocar**: comprobar si el ZIP empaqueta el acta (`ActaWriter` escribe en `v4_audit_dir`). Si la contuviera, **el acta publicada debe ser la enriquecida, nunca la pre-veredicto** — anotar el resultado en la evidencia aunque no exija cambio.
- Criterios:
  - [ ] Con veredicto bloqueante no queda ningún `*.zip` publicado para el `hotel_id` de la corrida (AC-E5, glob sobre `deliveries/`)
  - [ ] Con veredicto no bloqueante el ZIP queda publicado y `_validate_zip` sigue pasando
  - [ ] NR3: `grep` de `blocks_delivery_zip` en `main.py` sigue dando **una** llamada; el packager no importa el acta

### Tarea 2 — `reviewer_reports` tipado y poblado (AC-E0, AC-E1)
- Nuevos DTOs según §2.3 del contrato; `evaluate()` pierde el literal `"reviewer_reports": []`.
- `_compute_verdict(clauses, evidence_tier, first_floor, reviewer_reports)` con la matriz de §2.1 en ese orden.
- `acta_writer`: quitar el guard `if reviewer_reports:`; la sección `Reportes de Revisores` se renderiza **siempre**, una fila por Bot con su `status`.
- Criterios:
  - [ ] **Cuatro tests nombrados por causa**, uno por estado (`test_los_4_revisores_no_hallan_nada`, `test_artefacto_ausente`, `test_lector_fallido`, `test_los_revisores_no_corrieron`) + `test_los_tres_estados_no_colapsan` (AC-E0, NR8)
  - [ ] Prohibido cerrar con un fixture que solo pueda producir uno de los cuatro estados (`L-PF10`)
  - [ ] `reviewer_reports` de longitud 4 cuando los 4 corrieron (AC-E1)

### Tarea 3 — Consecuencia del bloqueo + kill switch (AC-E4, AC-E5)
- `corrective_actions[]` derivado de los hallazgos bloqueantes, con `finding_type`/`severity`/`artifact`/`instruction`/`owner` (nunca vacía si el veredicto es bloqueante).
- Bloqueo bajo `GATE_BLOCKING_ENABLED` + clave `enforcement` en el acta.
- stdout del operador: ruta del acta, motivo, lista de acciones. **Sin reintento.**
- Criterios:
  - [ ] AC-E4 con el par: knob `false` → se publica y el acta dice `suppressed_by_operator: true`; knob forzado a `true` en el test → camino de bloqueo ejercitado
  - [ ] AC-E5: `corrective_actions` no vacía con veredicto bloqueante
  - [ ] Nunca `entrega parcial` (ningún ZIP sin el asset bloqueado)

### Tarea 4 — Evidencia, NR7 y baseline NR1
- **NR7 por AC** (AC-E2, AC-E4, AC-E5): par de salidas en `evidence/FASE-P2/` — activo (verde) y desactivado (rojo). Para AC-E2: quitar el consumo de `reviewer_reports` en `_compute_verdict` y ver el test de bloqueo en rojo. **Un test que emita el acta a mano y pase con el guard quitado no certifica el enforcement.**
- **NR1 (baseline sin contaminar)**: snapshot `pre` con `--ignore` de los archivos de test propios de esta fase (`L-T4B.5`) y resta R2.7 (`suma_post − suma_pre == tests_nuevos`; diferencia 0 = baseline contaminado, no se declara el criterio). Combinación exacta de archivos y **flaky conocidos declarados** (`test_function_default_flags`).
- **Retro**: suite de `quality_gates/tribunal` + `tests/regression/` + la corrida E2E del predecesor en `evidence/FASE-E2E/` (diff estructural, no visual — `L-VUP-14`).
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Iteraciones medidas con **unidad declarada** y escritas en `06-checklist-implementacion.md` (L-R.1; un `—` no cierra la fase)

---

## Fuentes obligatorias (Paso 0 de esta fase)

| Fuente | Qué aporta |
|--------|-----------|
| `evidence/FASE-P1/decision-enforcement.md` | **El contrato.** §2 matriz, §3 consecuencia, §4 estados, §5 ACs |
| `evidence/FASE-P1/research-estado.md` | Mapa con símbolos + los tres hechos nuevos (acta lee tier inexistente; `if reviewer_reports` omite la sección; el packager ya tiene costura tmp→rename) |
| `evidence/FASE-P3-A/` y `evidence/FASE-P3-B/` | Lo que esta fase recibe ya arreglado (AC-F1/F2/F4/F5/F3/F6) y sus baselines NR1 |
| `Archives/TRIBUNAL-OFFLINE-2026-09-09/05-prompt-inicio-sesion-fase-T1.md` | La matriz findings→veredicto que se hereda |
| `evidence/FASE-T1/decision-integracion.md` | Las 3 rutas de bloqueo del ZIP; Ruta 2 elegida |
| `Archives/SR-PIPELINE-FIXES-2026-08-27/10-analisis…` | L-PF3 (bloqueo con DTO tipado), L-PF6/L-PF10 (ausencia ≠ detección fallida) |
| `Archives/VALIDADOR-URL-PROPIA-2026-08-30/10-analisis…` | L-VUP-5 (fase sin un solo rojo = falso verde), L-VUP-1 (baseline orden-dependiente), L-VUP-14 |
| `00-lecciones-capitalizadas.md` | Actualizado al cierre de P1: las 3.b ya resueltas (D-T1.1 vigente, L-SR3 causa estructural, DA-C3 subsumido por Q6) |

**Lecciones que gobiernan esta fase**: NR7 (todo AC de bloqueo con mutation check), NR8 (cuatro tests por estado), L-T2C.2 (`except` anchos enmascaran), L-VUP-5 (exige al menos un rojo real), L-SR5/L-PF3 (bloqueo sin consecuencia no previene), L-V.1 (fixture ≠ régimen real → los tests de bloqueo corren contra ZIP real, no contra un dir inventado).

---

## Post-Ejecución (OBLIGATORIO, no esperar a la siguiente sesión)

1. `dependencias-fases.md`: P2 ✅; si algo cambió del contrato, **decisión explícita registrada** (no reinterpretación)
2. `README.md`: progreso
3. `06-checklist-implementacion.md`: items de P2 + iteraciones con unidad declarada
4. `evidence/FASE-P2/`: par NR7 por AC, los cuatro tests por estado, baseline NR1 con resta R2.7
5. `10-analisis-post-implementacion.md`: fila de P2, DA-* nuevas, ≥3 lecciones
6. `09-documentacion-post-proyecto.md`: Sección A (módulos tocados: `judge.py`, `main.py`, `delivery_packager.py`, `acta_writer.py`), B, D, E
7. `00-lecciones-capitalizadas.md` §2: qué lección se aplicó de verdad y cuál no

## Restricciones

- **NO re-decidir** Q1/Q1b/Q2/Q5/Q6/Q7 (cerradas en P1). Cambiar el contrato = decisión registrada en `10-analisis`, no un refactor conveniente.
- **NO reintento automático** (Q1b).
- **NO cuarta ruta de bloqueo** (NR3).
- **NO modificar ROADMAP.md**. **NO números de línea** (R2.2). **NO delegar a subagente.**
- Punto de partición predefinido si agota presupuesto: **P2-part1** = contrato en `judge.py` + DTOs + tests; **P2-part2** = reordenamiento write/publish en `main.py` + `delivery_packager.py`.
